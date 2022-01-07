from selenium.webdriver.common.by import By

from database import Database
from episode import Episode


class Season:
    def __init__(self, driver, url, name=None, episodes=None):
        self.name = name
        self.url = url
        self.episodes = episodes
        self.driver = driver

    def get_data(self):
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
