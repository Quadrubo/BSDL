from PyQt5.QtCore import QObject, pyqtSignal

from database import Database
from series import Series
from scraper import Scraper

class SeriesLoader(QObject):
    def __init__(self, series_url):
        super().__init__()
        self.series_url = series_url

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    result = pyqtSignal(Series)
    callback_signal = pyqtSignal(list)

    def run(self):
        total_progress_min = 1
        total_progress_max = 1
        total_progress = f"Loading Series {total_progress_min} / {total_progress_max}"
        local_progress = 0

        scraper = Scraper()
        callback = scraper.create_driver()
        if callback != 0:
            self.callback_signal.emit(callback)
            return callback

        series = Series(driver=scraper.driver, url=self.series_url)
        callback = series.get_data()
        if callback != 0:
            self.callback_signal.emit(callback)
            return callback

        local_progress += 10
        self.progress.emit([total_progress, local_progress])

        seasons = len(series.seasons)
        print(seasons)
        parts = 90 / seasons

        for season in series.seasons:
            callback = season.get_data()
            if callback != 0:
                self.callback_signal.emit(callback)
                return callback
            local_progress += parts
            self.progress.emit([total_progress, local_progress])

        scraper.quit_driver()

        self.progress.emit([total_progress, local_progress])
        self.result.emit(series)
        self.finished.emit()
        self.progress.emit(["Finished", 0])


class EpisodeDownloader(QObject):
    def __init__(self, episode, season, series):
        super().__init__()
        self.episode = episode
        self.season = season
        self.series = series

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    result = pyqtSignal(Series)
    callback_signal = pyqtSignal(list)

    def run(self):
        total_progress_min = 1
        total_progress_max = 1
        total_progress = f"Downloading Episode {total_progress_min} / {total_progress_max}"

        scraper = Scraper()
        callback = scraper.create_driver()
        if callback != 0:
            self.callback_signal.emit(callback)
            return callback

        print(self.episode.url)

        self.episode.driver = scraper.driver
        callback = self.episode.download(self.progress, total_progress, self.season, self.series)
        if callback != 0:
            self.callback_signal.emit(callback)
            return callback


        scraper.quit_driver()

        self.result.emit(self.series)
        self.finished.emit()
        self.progress.emit(["Finished", 0])


class SeasonDownloader(QObject):
    def __init__(self, season, series):
        super().__init__()
        self.season = season
        self.series = series

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    result = pyqtSignal(Series)
    callback_signal = pyqtSignal(list)

    def run(self):
        total_progress_min = 1
        total_progress_max = 0
        for episode in self.season.episodes:
            if not episode.downloaded and episode.downloadable:
                total_progress_max += 1

        total_progress = f"Downloading Episode {total_progress_min} / {total_progress_max}"

        scraper = Scraper()
        callback = scraper.create_driver()
        if callback != 0:
            self.callback_signal.emit(callback)
            return callback

        for episode in self.season.episodes:
            print(episode.name)
            if not episode.downloaded and episode.downloadable:
                episode.driver = scraper.driver
                callback = episode.get_download_link()
                if type(callback) != str:
                    self.callback_signal.emit(callback)
                    return callback
                print(episode.hoster)
                print(episode.hoster_url)

        for episode in self.season.episodes:
            if not episode.downloaded and episode.downloadable:
                episode.driver = scraper.driver
                callback = episode.download(self.progress, total_progress, self.season, self.series)
                if callback != 0:
                    self.callback_signal.emit(callback)
                    return callback
                total_progress_min += 1
                total_progress = f"Downloading Episode {total_progress_min} / {total_progress_max}"
                db = Database(db_file_name="bsdl.db", db_folder_path='./db')
                db.refresh_series_data(self.series)

        scraper.quit_driver()

        self.result.emit(self.series)
        self.finished.emit()
        self.progress.emit(["Finished", 0])
