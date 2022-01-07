import json
import os


class Config:
    def __init__(self):
        self.filename = 'config.json'
        self.chrome_user_data_dir = None
        self.chrome_profile_dir = None
        self.chrome_driver_file = None
        self.hosters = None
        self.create()
        self.load_to_vars()

    def create(self):
        if not os.path.isfile(self.filename):
            with open('config.json', 'w') as f:
                json.dump({'chrome_user_data_dir': '', 'chrome_profile_dir': '', 'chrome_driver_file': '', 'hosters': []}, f)

    def load_to_vars(self):
        data = self.load()
        if data["chrome_user_data_dir"] != '':
            self.chrome_user_data_dir = data["chrome_user_data_dir"]
        if data["chrome_profile_dir"] != '':
            self.chrome_profile_dir = data["chrome_profile_dir"]
        if data["chrome_driver_file"] != '':
            self.chrome_driver_file = data["chrome_driver_file"]
        if data["hosters"]:
            self.hosters = data["hosters"]

    def set_hosters(self, hoster_list):
        self.hosters = hoster_list

        data = self.load()
        data["hosters"] = hoster_list

        self.write(data)

    def set_chrome_user_data_dir(self, text):
        self.chrome_user_data_dir = text

        data = self.load()
        data["chrome_user_data_dir"] = text

        self.write(data)

    def set_chrome_profile_dir(self, text):
        self.chrome_profile_dir = text

        data = self.load()
        data["chrome_profile_dir"] = text

        self.write(data)

    def set_chrome_driver_file(self, text):
        self.chrome_user_data_dir = text

        data = self.load()
        data["chrome_driver_file"] = text

        self.write(data)

    def load(self):
        with open(self.filename) as f:
            data = json.load(f)
            return data

    def write(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f)

cfg = Config()
