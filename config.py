import json
import logging
import os


class Config:
    def __init__(self):
        self.logger = None
        self.setup_logger()
        self.filename = 'config.json'
        self.chrome_user_data_dir = None
        self.chrome_profile_dir = None
        self.chrome_driver_file = None
        self.hosters = None
        self.create()
        self.load_to_vars()

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, filename="bsdl.txt", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger('config.py@Config')
        self.logger.debug("Logging started")

    def create(self):
        if not os.path.isfile(self.filename):
            self.logger.debug("No config file found, creating...")
            with open('config.json', 'w') as f:
                json.dump({'chrome_user_data_dir': '', 'chrome_profile_dir': '', 'chrome_driver_file': '', 'hosters': []}, f)
                self.logger.debug(f"Config file (\"{self.filename}\") created")
                f.close()

    def load_to_vars(self):
        self.logger.debug("Loading data into object variables...")
        data = self.load()
        if data["chrome_user_data_dir"] != '':
            self.chrome_user_data_dir = data["chrome_user_data_dir"]
        if data["chrome_profile_dir"] != '':
            self.chrome_profile_dir = data["chrome_profile_dir"]
        if data["chrome_driver_file"] != '':
            self.chrome_driver_file = data["chrome_driver_file"]
        if data["hosters"]:
            self.hosters = data["hosters"]
        self.logger.debug("Data successfully loaded into object variables")

    def set_hosters(self, hoster_list):
        self.logger.debug("Setting hosters...")
        self.hosters = hoster_list

        data = self.load()
        data["hosters"] = hoster_list

        self.write(data)
        self.logger.debug("Hosters successfully set")

        self.load_to_vars()

    def set_chrome_user_data_dir(self, text):
        self.logger.debug(f"Setting chrome user data directory to \"{text}\" ...")
        self.chrome_user_data_dir = text

        data = self.load()
        data["chrome_user_data_dir"] = text

        self.write(data)
        self.logger.debug(f"Chrome user data directory successfully set to \"{text}\"")

        self.load_to_vars()

    def set_chrome_profile_dir(self, text):
        self.logger.debug(f"Setting chrome profile directory to \"{text}\" ...")
        self.chrome_profile_dir = text

        data = self.load()
        data["chrome_profile_dir"] = text

        self.write(data)
        self.logger.debug(f"Chrome profile directory successfully set to \"{text}\"")

        self.load_to_vars()

    def set_chrome_driver_file(self, text):
        self.logger.debug(f"Setting chrome driver file to \"{text}\" ...")
        self.chrome_user_data_dir = text

        data = self.load()
        data["chrome_driver_file"] = text

        self.write(data)
        self.logger.debug(f"Chrome driver file successfully set to \"{text}\"")

        self.load_to_vars()

    def load(self):
        self.logger.debug(f"Loading data from the config file (\"{self.filename}\") ...")
        with open(self.filename) as f:
            data = json.load(f)
            self.logger.debug("Data successfully loaded")
            f.close()
            return data

    def write(self, data):
        self.logger.debug(f"Writing data to the config file (\"{self.filename}\") ...")
        with open(self.filename, 'w') as f:
            json.dump(data, f)
            self.logger.debug("Data successfully written")
            f.close()
