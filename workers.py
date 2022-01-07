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

    def run(self):
        total_progress_min = 1
        total_progress_max = 1
        total_progress = f"Loading Series {total_progress_min} / {total_progress_max}"
        local_progress = 0

        scraper = Scraper()
        scraper.create_driver()

        series = Series(driver=scraper.driver, url=self.series_url)
        series.get_data()

        local_progress += 10
        self.progress.emit([total_progress, local_progress])

        seasons = len(series.seasons)
        print(seasons)
        parts = 90 / seasons

        for season in series.seasons:
            season.get_data()
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

    def run(self):
        total_progress_min = 1
        total_progress_max = 1
        total_progress = f"Downloading Episode {total_progress_min} / {total_progress_max}"

        scraper = Scraper()
        scraper.create_driver()

        print(self.episode.url)

        self.episode.driver = scraper.driver
        self.episode.download(self.progress, total_progress, self.season, self.series)

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

    def run(self):
        total_progress_min = 1
        total_progress_max = 0
        for episode in self.season.episodes:
            if not episode.downloaded:
                total_progress_max += 1

        total_progress = f"Downloading Episode {total_progress_min} / {total_progress_max}"

        scraper = Scraper()
        scraper.create_driver()

        tmp_counter = 1
        for episode in self.season.episodes:
            if not episode.downloaded:
                episode.driver = scraper.driver
                episode.get_download_link()
                print(episode.hoster)
                print(episode.hoster_url)
                tmp_counter += 1

        for episode in self.season.episodes:
            if not episode.downloaded:
                episode.driver = scraper.driver
                episode.download(self.progress, total_progress, self.season, self.series)
                total_progress_min += 1
                total_progress = f"Downloading Episode {total_progress_min} / {total_progress_max}"
                db = Database(db_file_name="bsdl.db", db_folder_path='./db')
                db.refresh_series_data(self.series)



        scraper.quit_driver()

        self.result.emit(self.series)
        self.finished.emit()
        self.progress.emit(["Finished", 0])
