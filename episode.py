import os
import re
import subprocess
import time
import urllib.request

from selenium.webdriver.common.by import By

from config import Config


class Episode:
    def __init__(self, driver, url, name=None, number=None, downloadable=None, downloaded=None):
        self.name = name
        self.number = number
        self.downloadable = downloadable
        self.url = url
        self.driver = driver
        self.downloaded = downloaded
        self.hoster = None
        self.hoster_url = None
        self.config = Config()

    def dl_vupload(self, hoster_url, progress, total_progress, season, series):
        self.driver.get(hoster_url)

        m3u8_script = self.driver.find_element(By.XPATH, '/html/body/div/script[7]').get_attribute('innerHTML')

        m3u8_url = re.findall('src: ".*master\.m3u8",', m3u8_script)[0]
        m3u8_url = m3u8_url[6:m3u8_url.find(".m3u8") + 5]

        last_line = ""

        counter = 0
        for line in urllib.request.urlopen(m3u8_url):
            last_line = line
            counter += 1
            if counter == 5:
                break
        # TODO completete highest resolution picker

        last_line = last_line.decode()

        tmp_url = last_line[last_line.find("URI=\"") + 1:-1]

        counter = 0
        for line in urllib.request.urlopen(tmp_url):
            if line.decode().startswith("seg-"):
                counter += 1

        progress_all = counter

        series.name = re.sub(r'[|\\\/:*"?<>]', '', series.name)
        series_path = os.path.join('./_output', series.name)
        if not os.path.isdir(series_path):
            os.mkdir(series_path)
        season.name = re.sub(r'[|\\\/:*"?<>]', '', season.name)
        season_path = os.path.join(series_path, season.name)
        if not os.path.isdir(season_path):
            os.mkdir(season_path)

        output_file = os.path.join(season_path, f'{self.number}.mp4')

        proc = subprocess.Popen(f'ffmpeg -i "{tmp_url}" -c copy "{output_file}"', bufsize=1, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, close_fds=True)
        for line in iter(proc.stdout.readline, b''):
            line = line.decode()
            try:
                progr = re.findall('\/seg-.*-v', line)[0]
                progr = progr[5:progr.find("-v")]
                local_progress = (float(progr) / float(progress_all)) * 100
                progress.emit([total_progress, local_progress])
            except IndexError:
                pass
        proc.stdout.close()
        proc.wait()

        self.downloaded = True

    def get_download_link(self):
        self.driver.get(self.url)

        hoster = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/ul[1]/li[1]').find_element(By.TAG_NAME,
                                                                                                        'a').text.lower().strip()

        self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]').click()

        time.sleep(2)

        msg_send = False
        while True:
            try:
                vscheck = self.driver.find_element(By.XPATH, "/html/body/div[4]")
                if "visible" in vscheck.get_attribute("style"):
                    if not msg_send:
                        print("INFO: Captcha found, Human needed O.O")
                        msg_send = True
                else:
                    print("INFO: Captcha solved. Good job Human :)")
                    break
            except:
                pass

        time.sleep(1)

        hoster_url = None
        if hoster == "vupload":
            while True:
                try:
                    hoster_url = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]/a').get_attribute('href')
                    break
                except:
                    time.sleep(1)
                    pass

        self.hoster = hoster
        self.hoster_url = hoster_url

    def download(self, progress, total_progress, season, series):
        if self.hoster is not None and self.hoster_url is not None:
            if self.hoster == "vupload":
                self.dl_vupload(self.hoster_url, progress, total_progress, season, series)
            return 0

        self.driver.get(self.url)

        preferred_hosters = self.config.hosters
        available_hosters = []

        hosters_ul_1 = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/ul[1]')
        hoster_lis_1 = hosters_ul_1.find_elements(By.TAG_NAME, 'li')
        hosters_ul_2 = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/ul[2]')
        hoster_lis_2 = hosters_ul_2.find_elements(By.TAG_NAME, 'li')

        for hoster_li in hoster_lis_1:
            available_hosters.append(hoster_li.text.strip().lower())

        for hoster_li in hoster_lis_2:
            available_hosters.append(hoster_li.text.strip().lower())

        hoster_positions = []

        for hoster in available_hosters:
            counter = 0
            for pref_hoster in preferred_hosters:
                if hoster == pref_hoster.strip().lower():
                    hoster_positions.append([hoster, counter])
                    break
                counter += 1

        preferred_hoster = ""
        position = 99
        for hoster in hoster_positions:
            if hoster[1] < position:
                position = hoster[1]
                preferred_hoster = hoster[0]

        hoster_link = ""
        for hoster_li in hoster_lis_1:
            if hoster_li.text.strip().lower() == preferred_hoster:
                hoster_link = hoster_li
        for hoster_li in hoster_lis_2:
            if hoster_li.text.strip().lower() == preferred_hoster:
                hoster_link = hoster_li

        hoster_link.click()

        self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]').click()

        time.sleep(1)

        msg_send = False
        while True:
            try:
                vscheck = self.driver.find_element(By.XPATH, "/html/body/div[4]")
                if "visible" in vscheck.get_attribute("style"):
                    if not msg_send:
                        print("INFO: Captcha found, Human needed O.O")
                        msg_send = True
                else:
                    print("INFO: Captcha solved. Good job Human :)")
                    break
            except:
                pass

        time.sleep(1)

        # TODO support all hosters

        if preferred_hoster == "vupload":
            hoster_url = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]/a').get_attribute('href')
            self.dl_vupload(hoster_url, progress, total_progress, season, series)
