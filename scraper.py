import time
import logging

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.CRITICAL)

from config import Config


class Scraper:
    def __init__(self):
        self.setup_logger()
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

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, filename="bsdl.txt", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger('scraper.py@Scraper')
        self.logger.debug("Logging started")

    def create_driver(self):
        service = Service(executable_path=self.chrome_driver_path)
        try:

            self.driver = webdriver.Chrome(service=service, desired_capabilities=self.d, options=self.options)

            time.sleep(1)
            self.driver.get("https://github.com/Quadrubo/BSDL")
            time.sleep(1)

        except selenium.common.exceptions.InvalidArgumentException:
            self.logger.error("Please close any currently running instances of chrome and try again. Also check the Task-Manager. Check the \"bsdl.txt\" file for more information.", exc_info=True)
            return [1, "Error", "Please close any currently running instances of chrome and try again. Also check the Task-Manager. Check the \"bsdl.txt\" file for more information."]
        except selenium.common.exceptions.WebDriverException:
            self.logger.error("It seems like Chrome has been closed manually. Please try again. Check the \"bsdl.txt\" file for more information.", exc_info=True)
            return [1, "Error", "It seems like Chrome has been closed manually. Please try again. Check the \"bsdl.txt\" file for more information."]
        except Exception:
            self.logger.error("Unknown error. Please open up an issue on GitHub (https://github.com/Quadrubo/BSDL) with your error log included (\"bsdl.txt\"). Check the \"bsdl.txt\" file for more information.")
            return [1, "Error", "Unknown error. Please open up an issue on GitHub (https://github.com/Quadrubo/BSDL) with your error log included (\"bsdl.txt\"). Check the \"bsdl.txt\" file for more information."]

        return 0

    def quit_driver(self):
        self.driver.quit()
