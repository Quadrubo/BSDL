import selenium.common.exceptions
from selenium.webdriver.common.by import By

from season import Season

class Series:
    def __init__(self, driver, url, name=None, seasons=None):
        self.name = name
        self.url = url
        self.seasons = seasons
        self.driver = driver

    def get_data(self):
        try:
            # Get the link to the website
            self.driver.get(self.url)
            # Scrape the name of the series
            self.name = self.driver.find_element(By.XPATH, '//*[@id="sp_left"]/h2').get_attribute('innerHTML')
            self.name = self.name[0:self.name.find('<small>')].strip()
        except selenium.common.exceptions.NoSuchElementException:
            return [1, "Error", "Please check if you entered a valid URL."]

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
