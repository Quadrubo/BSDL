import logging
import os
import sys
import time

import selenium.common.exceptions
from selenium.webdriver.common.by import By

from season import Season

class Series:
    def __init__(self, driver, url, name=None, seasons=None):
        self.logger = None
        self.setup_logger()
        self.name = name
        self.url = url
        self.seasons = seasons
        self.driver = driver

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, filename="bsdl.txt", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger('series.py@Series')
        self.logger.debug("Logging started")

    def get_data(self):
        try:
            # Get the link to the website
            self.driver.get(self.url)

            # Scrape the name of the series
            self.name = self.driver.find_element(By.XPATH, '//*[@id="sp_left"]/h2').get_attribute('innerHTML')
            self.name = self.name[0:self.name.find('<small>')].strip()

            season_list = []

            # Scrape the metadata of each season
            seasons_ul = self.driver.find_element(By.XPATH, '//*[@id="seasons"]/ul')
            season_lis = seasons_ul.find_elements(By.TAG_NAME, 'li')
            for season_li in season_lis:
                season_a = season_li.find_element(By.TAG_NAME, 'a')
                season_name = season_a.text
                season_url = season_a.get_attribute('href')
                season = Season(driver=self.driver, url=season_url, name=season_name)
                season_list.append(season)

            self.seasons = season_list

            return 0
        except selenium.common.exceptions.InvalidArgumentException:
            self.logger.error("Please close any currently running instances of chrome and try again. Also check the Task-Manager. Check the \"bsdl.txt\" file for more information.",exc_info=True)
            return [1, "Error", "Please close any currently running instances of chrome and try again. Also check the Task-Manager. Check the \"bsdl.txt\" file for more information."]
        except selenium.common.exceptions.WebDriverException:
            self.logger.error("It seems like Chrome has been closed manually. Please try again. Check the \"bsdl.txt\" file for more information.", exc_info=True)
            return [1, "Error", "It seems like Chrome has been closed manually. Please try again. Check the \"bsdl.txt\" file for more information."]
        except Exception:
            self.logger.error("Unknown error. Please open up an issue on GitHub (https://github.com/Quadrubo/BSDL) with your error log included (\"bsdl.txt\"). Check the \"bsdl.txt\" file for more information.")
            return [1, "Error", "Unknown error. Please open up an issue on GitHub (https://github.com/Quadrubo/BSDL) with your error log included (\"bsdl.txt\"). Check the \"bsdl.txt\" file for more information."]

