import time
import json
import re

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

chrome_user_data_path = r'C:\Users\Julian\AppData\Local\Google\Chrome\User Data'
chrome_profile_path = r'Profile 1'
chrome_driver_path = r'C:\Programming\Python\BSDL\driver\chromedriver.exe'
download_url = r'https://bs.to/serie/Sword-Art-Online-SAO'
# https://bs.to/serie/Sword-Art-Online-SAO
# https://bs.to/serie/Sword-Art-Online-SAO/1/de

options = Options()
options.add_argument(f'profile-directory={chrome_profile_path}')
options.add_argument(f"user-data-dir={chrome_user_data_path}")

# Disable infobar (Chrome is being controlled by automated software)
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches",["enable-automation"])

# Avoid bot protection
options.add_argument('disable-blink-features=AutomationControlled')

d = DesiredCapabilities.CHROME
d["goog:loggingPrefs"] = {"performance": "ALL"}

# options.add_experimental_option('w3c', False)

service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, desired_capabilities=d, options=options)

driver.get("https://www.google.de/")

time.sleep(2)


class Episode:
    def __init__(self, url, name=None, number=None):
        self.name = name
        self.number = number
        self.url = url




    def dl_vupload(self, hoster_url):
        driver.get(hoster_url)

        m3u8_script = driver.find_element(By.XPATH, '/html/body/div/script[7]').get_attribute('innerHTML')

        m3u8_url = re.findall('src: ".*master\.m3u8",', m3u8_script)[0]
        m3u8_url = m3u8_url[6:m3u8_url.find(".m3u8") + 5]

        input()

    def download(self):
        driver.get(self.url)

        # TODO select proper hoster
        # chooses the first one for now

        hoster = driver.find_element(By.XPATH, '//*[@id="root"]/section/ul[1]/li[1]').find_element(By.TAG_NAME, 'a').text.lower().strip()

        driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]').click()

        # TODO captcha check

        input()

        if hoster == "vupload":
            hoster_url = driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]/a').get_attribute('href')
            self.dl_vupload(hoster_url)




class Season:
    def __init__(self, url, name=None, episodes=None):
        self.name = name
        self.url = url
        self.episodes = episodes

    def get_data(self):
        driver.get(self.url)

        # Scrape the url of each episode
        episode_list = []

        episodes_table = driver.find_element(By.XPATH, '//*[@id="root"]/section/table')
        episode_trs = episodes_table.find_elements(By.TAG_NAME, 'tr')
        for episode_tr in episode_trs:
            episode_a = episode_tr.find_element(By.TAG_NAME, 'a')
            episode_number = episode_a.text
            episode_name = episode_a.get_attribute('title')
            episode_url = episode_a.get_attribute('href')
            episode = Episode(url=episode_url, name=episode_name, number=episode_number)
            episode_list.append(episode)

        self.episodes = episode_list


class Series:
    def __init__(self, url, name=None, seasons=None):
        self.name = name
        self.url = url
        self.seasons = seasons

    def get_data(self):
        driver.get(self.url)

        # Scrape the name of the series
        self.name = driver.find_element(By.XPATH, '//*[@id="sp_left"]/h2').text

        # Scrape the url of each season
        season_list = []

        seasons_ul = driver.find_element(By.XPATH, '//*[@id="seasons"]/ul')
        season_lis = seasons_ul.find_elements(By.TAG_NAME, 'li')
        for season_li in season_lis:
            season_a = season_li.find_element(By.TAG_NAME, 'a')
            season_name = season_a.text
            season_url = season_a.get_attribute('href')
            season = Season(url=season_url, name=season_name)
            season_list.append(season)

        self.seasons = season_list


series = Series(url=download_url)
series.get_data()

for season in series.seasons:
    season.get_data()

series.seasons[1].episodes[0].download()