import time

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config import Config

class Scraper:
    def __init__(self):
        self.config = Config()

        self.chrome_user_data_path = self.config.chrome_user_data_dir
        self.chrome_profile_path = self.config.chrome_profile_dir
        self.chrome_driver_path = self.config.chrome_driver_file

        self.options = Options()

        self.options.add_argument(f'profile-directory={self.chrome_profile_path}')
        self.options.add_argument(f"user-data-dir={self.chrome_user_data_path}")

        # Disable infobar (Chrome is being controlled by automated software)
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Avoid bot protection
        self.options.add_argument('disable-blink-features=AutomationControlled')

        self.d = DesiredCapabilities.CHROME
        self.d["goog:loggingPrefs"] = {"performance": "ALL"}

    def create_driver(self):
        service = Service(executable_path=self.chrome_driver_path)
        try:
            self.driver = webdriver.Chrome(service=service, desired_capabilities=self.d, options=self.options)
        except selenium.common.exceptions.InvalidArgumentException:
            return [1, "Error", "Please close any currently running instances of chrome and try again."]

        time.sleep(1)
        self.driver.get("https://github.com/Quadrubo/BS-Downloader")
        time.sleep(1)

        return 0

    def quit_driver(self):
        self.driver.quit()
