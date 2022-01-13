import selenium.common.exceptions
from selenium.webdriver.common.by import By
import logging

from database import Database
from episode import Episode


class Season:
    def __init__(self, driver, url, name=None, episodes=None):
        self.logger = None
        self.setup_logger()
        self.name = name
        self.url = url
        self.episodes = episodes
        self.driver = driver

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, filename="bsdl.txt", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger('season.py@Season')
        self.logger.debug("Logging started")

    def get_data(self):
        try:
            self.driver.get(self.url)

            # Scrape the url of each episode
            episode_list = []

            episodes_table = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/table')
            episode_trs = episodes_table.find_elements(By.TAG_NAME, 'tr')
            db = Database(db_file_name="bsdl.db", db_folder_path='./db')
            for episode_tr in episode_trs:
                episode_a = episode_tr.find_element(By.TAG_NAME, 'a')
                episode_number = episode_a.text
                episode_name = episode_a.get_attribute('title')
                episode_url = episode_a.get_attribute('href')

                downloaded = False
                if db.get_episode(episode_url) is not None:
                    downloaded = True

                if 'disabled' in episode_tr.get_attribute('class'):
                    episode_downloadable = False
                else:
                    episode_downloadable = True
                episode = Episode(driver=self.driver, url=episode_url, name=episode_name, number=episode_number, downloadable=episode_downloadable, downloaded=downloaded)
                episode_list.append(episode)

            self.episodes = episode_list

            return 0
        except selenium.common.exceptions.InvalidArgumentException:
            self.logger.error("Please close any currently running instances of chrome and try again. Also check the Task-Manager. Check the \"bsdl.txt\" file for more information.", exc_info=True)
            return [1, "Error", "Please close any currently running instances of chrome and try again. Also check the Task-Manager. Check the \"bsdl.txt\" file for more information."]
        except selenium.common.exceptions.WebDriverException:
            self.logger.error("It seems like Chrome has been closed manually. Please try again. Check the \"bsdl.txt\" file for more information.", exc_info=True)
            return [1, "Error", "It seems like Chrome has been closed manually. Please try again. Check the \"bsdl.txt\" file for more information."]
        except Exception:
            self.logger.error("Unknown error. Please open up an issue on GitHub (https://github.com/Quadrubo/BSDL) with your error log included (\"bsdl.txt\"). Check the \"bsdl.txt\" file for more information.")
            return [1, "Error", "Unknown error. Please open up an issue on GitHub (https://github.com/Quadrubo/BSDL) with your error log included (\"bsdl.txt\"). Check the \"bsdl.txt\" file for more information."]

