import os
import sys
import logging

from PyQt5.QtCore import (
    Qt,
    QThread,
    pyqtSlot,
    QEvent
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QWidget, QTabWidget, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem,
    QAbstractItemView, QDialog, QFileDialog,
)

from config import Config
from database import Database
from workers import EpisodeDownloader, SeriesLoader, SeasonDownloader


class TabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout(self)

        self.tabList = []

        # Initialize tab screen
        self.tabs = QTabWidget()

        self.tab1 = QWidget()

        # Add tabs
        self.tabs.addTab(self.tab1, "Tab 1")

        self.tabList.append(self.tab1)

        # Create first tab
        self.tab1.layout = QGridLayout(self)
        self.loadText = QLabel("Please begin by loading a series.")
        self.tab1.layout.addWidget(self.loadText, 0, 0)
        self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTabWidgetItem in self.tabWidget.selectedItems():
            print(currentQTabWidgetItem.row(), currentQTabWidgetItem.column(), currentQTabWidgetItem.text())


class HosterList(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        self.setup_logger()
        self.installEventFilter(self)
        self.config = Config()

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, filename="bsdl.txt", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger('gui.py@HosterList')
        self.logger.debug("Logging started")

    def eventFilter(self, sender, event):
        if event.type() == QEvent.ChildRemoved:
            self.logger.debug("Hoster has been moved")
            self.hoster_moved(sender, event)
        return False

    def hoster_moved(self, sender, event):
        items = []
        for i in range(sender.count()):
            items.append(sender.item(i).text())

        self.config.set_hosters(items)


class ConfigWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_logger()
        self.config = Config()
        self.setup_ui()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowModality(Qt.ApplicationModal)

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, filename="bsdl.txt", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger('gui.py@ConfigWindow')
        self.logger.debug("Logging started")

    def chrome_user_data_dir_button_clicked(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle('Open Chrome user data directory')
        dialog.setFileMode(QFileDialog.DirectoryOnly)

        dialog.setDirectory(os.getenv('LOCALAPPDATA'))
        if self.chrome_user_data_dir_button.text() != "Browse...":
            dialog.setDirectory(self.chrome_user_data_dir_button.text())

        if dialog.exec_() == QDialog.Accepted:
            file_full_path = str(dialog.selectedFiles()[0])
            file_full_path = file_full_path.replace("/", "\\")
            print(file_full_path)
            self.chrome_user_data_dir_button.setText(file_full_path)

            self.config.set_chrome_user_data_dir(file_full_path)

    def chrome_profile_dir_button_clicked(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle('Open Chrome profile directory')
        dialog.setFileMode(QFileDialog.DirectoryOnly)

        dialog.setDirectory(os.getenv('LOCALAPPDATA'))
        if self.chrome_profile_dir_button.text() != "Browse...":
            dialog.setDirectory(self.chrome_profile_dir_button.text())
        elif self.chrome_user_data_dir_button.text() != "Browse...":
            dialog.setDirectory(self.chrome_user_data_dir_button.text())

        if dialog.exec_() == QDialog.Accepted:
            file_full_path = str(dialog.selectedFiles()[0])
            file_full_path = file_full_path.replace("/", "\\")
            profile_name = file_full_path.split("\\")[-1]
            self.chrome_profile_dir_button.setText(profile_name)

            self.config.set_chrome_profile_dir(profile_name)

    def chrome_driver_file_button_clicked(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle('Open Chrome driver file')
        dialog.setNameFilter('exe files (*.exe)')
        dialog.setFileMode(QFileDialog.ExistingFile)

        dialog.setDirectory(os.getcwd())
        if self.chrome_driver_file_button.text() != "Browse...":
            dialog.setDirectory(self.chrome_driver_file_button.text())

        if dialog.exec_() == QDialog.Accepted:
            file_full_path = str(dialog.selectedFiles()[0])
            file_full_path = file_full_path.replace("/", "\\")
            self.chrome_driver_file_button.setText(file_full_path)

            self.config.set_chrome_driver_file(file_full_path)

    def setup_ui(self):
        self.setWindowTitle("Config")
        self.resize(900, 500)

        self.chrome_user_data_dir_label = QLabel("Chrome user data directory:", self)
        self.chrome_user_data_dir_button = QPushButton("Browse...", self)
        if self.config.chrome_user_data_dir is not None:
            self.chrome_user_data_dir_button.setText(self.config.chrome_user_data_dir)
        else:
            tmp_path = os.path.join(os.getenv('LOCALAPPDATA'), "Google\\Chrome\\User Data")
            if os.path.exists(tmp_path):
                self.chrome_user_data_dir_button.setText(tmp_path)
                self.config.chrome_user_data_dir = tmp_path
                self.config.set_chrome_user_data_dir(tmp_path)
        self.chrome_user_data_dir_button.clicked.connect(self.chrome_user_data_dir_button_clicked)

        self.chrome_profile_dir_label = QLabel("Chrome profile directory:", self)
        self.chrome_profile_dir_button = QPushButton("Browse...", self)
        if self.config.chrome_profile_dir is not None:
            self.chrome_profile_dir_button.setText(self.config.chrome_profile_dir)
        self.chrome_profile_dir_button.clicked.connect(self.chrome_profile_dir_button_clicked)

        self.chrome_driver_file_label = QLabel("Chrome driver file:", self)
        self.chrome_driver_file_button = QPushButton("Browse...", self)
        if self.config.chrome_driver_file is not None:
            self.chrome_driver_file_button.setText(self.config.chrome_driver_file)
        self.chrome_driver_file_button.clicked.connect(self.chrome_driver_file_button_clicked)

        self.hosters_label = QLabel("Hosters:", self)
        self.hosters_list_widget = HosterList()
        # self.hosters_list_widget = QListWidget(self)
        if self.config.hosters is not None:
            for hoster in self.config.hosters:
                self.hosters_list_widget.addItem(QListWidgetItem(hoster))
        else:
            # TODO upstream, videovard (can't be implemented due to minified javascript rn, needed to parse logs)
            hoster_list = ["VOE", "Vupload", "Streamtape", "MIXdrop", "Vidoza", "UPStream (NOT WORKING)", "VideoVard (NOT WORKING)"]
            for item in hoster_list:
                self.hosters_list_widget.addItem(QListWidgetItem(item))

        self.hosters_list_widget.setDragDropMode(QAbstractItemView.InternalMove)

        items = []
        for i in range(self.hosters_list_widget.count()):
            items.append(self.hosters_list_widget.item(i).text())

        self.config.set_hosters(items)

        self.layout = QGridLayout()
        self.layout.addWidget(self.chrome_user_data_dir_label, 0, 0, 1, 1)
        self.layout.addWidget(self.chrome_user_data_dir_button, 0, 1, 1, 1)
        self.layout.addWidget(self.chrome_profile_dir_label, 1, 0, 1, 1)
        self.layout.addWidget(self.chrome_profile_dir_button, 1, 1, 1, 1)
        self.layout.addWidget(self.chrome_driver_file_label, 2, 0, 1, 1)
        self.layout.addWidget(self.chrome_driver_file_button, 2, 1, 1, 1)
        self.layout.addWidget(self.hosters_label, 3, 0, 1, 1)
        self.layout.addWidget(self.hosters_list_widget, 3, 1, 1, 1)
        self.setLayout(self.layout)


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_logger()
        self.config_window = None
        self.clicksCount = 0
        self.setup_ui()
        self.config = Config()
        self.check_config()
        self.series = None
        self.test = False
        self.buttons = []

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, filename="bsdl.txt", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger('gui.py@Window')
        self.logger.debug("Logging started")

    def check_config(self):
        if self.config.chrome_user_data_dir is None or self.config.chrome_profile_dir is None or self.config.chrome_driver_file is None or self.config.hosters is None:
            self.show_config_window()

    def setup_ui(self):
        self.logger.debug("Setting up the UI")

        self.setWindowTitle("BSDL v4.0.0-alpha.1")
        self.resize(900, 600)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create and connect widgets
        self.urlLabel = QLabel("BS Url:", self)
        self.urlEntry = QLineEdit()
        # DEBUG self.urlEntry.setText('https://bs.to/serie/Sword-Art-Online-SAO')
        self.loadButton = QPushButton("Load...", self)
        self.loadButton.clicked.connect(self.load_series_task)

        self.progressLabel = QLabel("0/0", self)
        self.progressBar = QProgressBar(self)

        self.outputFolderButton = QPushButton("Open Output...", self)
        self.outputFolderButton.clicked.connect(self.open_output_folder)

        self.tabWidget = TabWidget(self)

        self.configButton = QPushButton("Config", self)
        self.configButton.clicked.connect(self.show_config_window)

        # Set the layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.urlLabel, 0, 0, 1, 1)
        self.layout.addWidget(self.urlEntry, 0, 1, 1, 1)
        self.layout.addWidget(self.loadButton, 0, 2, 1, 1)
        self.layout.addWidget(self.progressLabel, 1, 0, 1, 1)
        self.layout.addWidget(self.progressBar, 1, 1, 1, 1)
        self.layout.addWidget(self.outputFolderButton, 1, 2, 1, 1)
        self.layout.addWidget(self.tabWidget, 2, 0, 1, 3)
        self.layout.addWidget(self.configButton, 3, 0, 1, 1)
        self.centralWidget.setLayout(self.layout)
        self.centralWidget.setLayout(self.layout)

        self.logger.debug("UI setup complete")

    def show_config_window(self):
        self.config_window = ConfigWindow()
        self.config_window.show()

    def create_messagebox(self, callback):
        self.enable_buttons()
        print(callback)

    def refresh_database(self):
        db = Database(db_file_name="bsdl.db", db_folder_path='./db')
        db.create_tables()
        db.refresh_series_data(self.series)

    def generate_tabs(self, data):
        self.series = data

        self.tabWidget.tabs.clear()

        self.tabWidget.tabList = []
        for season in data.seasons:
            tmp_tab = QWidget()

            tmp_tab.layout = QGridLayout(self)

            tmp_tab.download = QPushButton("Download all")
            tmp_tab.download.clicked.connect(self.download_all_button_clicked)
            tmp_tab.layout.addWidget(tmp_tab.download, 0, 0)

            tmp_tab.table = self.generate_table(season)
            tmp_tab.layout.addWidget(tmp_tab.table, 1, 0)

            tmp_tab.setLayout(tmp_tab.layout)

            self.tabWidget.tabList.append(tmp_tab)
            self.tabWidget.tabs.addTab(tmp_tab, season.name)

        self.refresh_database()

    def generate_table(self, data):
        tmp_table = QTableWidget()
        header = tmp_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        tmp_table.buttons = []

        episodes_count = len(data.episodes)
        tmp_table.setRowCount(episodes_count)

        # set column count
        tmp_table.setColumnCount(4)

        x_counter = 0
        for episode in data.episodes:
            tmp_table.setItem(x_counter, 0, QTableWidgetItem(episode.number))
            tmp_table.setItem(x_counter, 1, QTableWidgetItem(episode.name))
            if episode.downloadable:
                tmp_button = QPushButton("Download")
            else:
                tmp_button = QPushButton("Unavailable")
                tmp_button.setEnabled(False)
            tmp_button.clicked.connect(self.table_button_clicked)
            tmp_table.setCellWidget(x_counter, 2, tmp_button)
            if episode.downloaded:
                tmp_table_widget_item = QTableWidgetItem("Downloaded")
                tmp_table_widget_item.setBackground(QColor(0, 255, 0))
            else:
                tmp_table_widget_item = QTableWidgetItem("Not Downloaded")
            tmp_table.setItem(x_counter, 3, tmp_table_widget_item)

            tmp_table.buttons.append(tmp_button)
            x_counter += 1

        return tmp_table

    def table_button_clicked(self):
        self.disable_buttons()
        button = self.sender()
        tab_index = self.tabWidget.tabs.currentIndex()
        button_index = self.tabWidget.tabList[self.tabWidget.tabs.currentIndex()].table.indexAt(button.pos())
        if button_index.isValid():
            self.download_episode_task(self.series.seasons[tab_index].episodes[button_index.row()], self.series.seasons[tab_index])
        else:
            raise Exception

    def download_all_button_clicked(self):
        self.disable_buttons()
        tab_index = self.tabWidget.tabs.currentIndex()
        self.download_season_task(self.series.seasons[tab_index])

    def report_progress(self, progress_array):
        total_progress = progress_array[0]
        partial_progress = progress_array[1]
        self.progressLabel.setText(total_progress)
        self.progressBar.setValue(int(partial_progress))

    def download_season_task(self, season):
        self.thread = QThread()
        self.worker = SeasonDownloader(season, self.series)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.result.connect(self.generate_tabs)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)
        self.worker.callback_signal.connect(self.create_messagebox)

        self.thread.start()

        self.disable_buttons()

        self.thread.finished.connect(self.enable_buttons)

    def download_episode_task(self, episode, season):
        self.thread = QThread()
        self.worker = EpisodeDownloader(episode, season, self.series)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.result.connect(self.generate_tabs)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)
        self.worker.callback_signal.connect(self.create_messagebox)

        self.thread.start()

        self.disable_buttons()

        self.thread.finished.connect(self.enable_buttons)

    def disable_buttons(self):
        self.loadButton.setEnabled(False)
        self.configButton.setEnabled(False)
        try:
            for tab in self.tabWidget.tabList:
                for button in tab.table.buttons:
                    button.setEnabled(False)
                tab.download.setEnabled(False)
        except AttributeError as e:
            print(e)

    def enable_buttons(self):
        self.loadButton.setEnabled(True)
        self.configButton.setEnabled(True)
        self.progressLabel.setText("0/0")
        self.progressBar.setValue(0)

    def open_output_folder(self):
        print(os.getcwd())
        os.startfile(os.path.join(os.getcwd(), '_output'))

    def load_series_task(self):
        series_url = self.urlEntry.text()
        print(series_url)

        # TODO url validation

        self.thread = QThread()
        self.worker = SeriesLoader(series_url)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.result.connect(self.generate_tabs)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)
        self.worker.callback_signal.connect(self.create_messagebox)

        self.thread.start()

        self.disable_buttons()

        self.thread.finished.connect(self.enable_buttons)


app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())
