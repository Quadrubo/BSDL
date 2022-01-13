import datetime
import logging
import os
import re
import subprocess
import time
import urllib.request
import urllib.error

import selenium.common.exceptions
from selenium.webdriver.common.by import By

from config import Config


class Episode:
    def __init__(self, driver, url, name=None, number=None, downloadable=None, downloaded=None):
        self.logger = None
        self.setup_logger()
        self.name = name
        self.number = number
        self.downloadable = downloadable
        self.url = url
        self.driver = driver
        self.downloaded = downloaded
        self.hoster = None
        self.hoster_url = None
        self.config = Config()

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, filename="bsdl.txt", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger('episode.py@Episode')
        self.logger.debug("Logging started")

        urllib3_log = logging.getLogger("urllib3.connectionpool")
        urllib3_log.setLevel(logging.CRITICAL)

    def download_from_mp4(self, mp4_link, progress, total_progress, season, series, wait_time=0):
        if not os.path.isdir('./_output'):
            os.mkdir('./_output')
        series.name = re.sub(r'[|\\\/:*"?<>]', '', series.name)
        series_path = os.path.join('./_output', series.name)
        if not os.path.isdir(series_path):
            os.mkdir(series_path)
        season.name = re.sub(r'[|\\\/:*"?<>]', '', season.name)
        season_path = os.path.join(series_path, season.name)
        if not os.path.isdir(season_path):
            os.mkdir(season_path)

        output_file = os.path.join(season_path, f'{self.number}.mp4')

        print(mp4_link)

        for i in range(1, wait_time):
            print(i)
            time.sleep(1)

        proc = subprocess.Popen(f'ffmpeg -i "{mp4_link}" -c copy -movflags faststart "{output_file}"', bufsize=1, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, universal_newlines=True, close_fds=True)
        total_seconds = None
        fps = None
        total_frames = None
        calculated_frames = False
        while proc.poll() is None:
            line = proc.stdout.readline()
            print(line)

            try:
                tmp_fps = re.findall('[0-9.]* fps,', line)[0]
                tmp_fps = tmp_fps[0:tmp_fps.find(' fps,')]
                fps = float(tmp_fps)
            except IndexError:
                pass

            try:
                tmp_total_seconds = re.findall('Duration: .*, start', line)[0]
                tmp_total_seconds = tmp_total_seconds[10:tmp_total_seconds.find(', start')]
                tmp_total_seconds = time.strptime(tmp_total_seconds.split('.')[0], '%H:%M:%S')
                total_seconds = datetime.timedelta(hours=tmp_total_seconds.tm_hour, minutes=tmp_total_seconds.tm_min, seconds=tmp_total_seconds.tm_sec).total_seconds()
            except IndexError:
                pass

            if not calculated_frames:
                if total_seconds is not None and fps is not None:
                    total_frames = total_seconds * fps
                    calculated_frames = True

            try:
                progr = re.findall('frame=[ ]*[0-9]* fps', line)[0]
                progr = progr[6:progr.find(' fps')]
                local_progress = (float(progr) / float(total_frames)) * 100
                print(str(progr) + " / " + str(total_frames) + " = " + str(local_progress))
                progress.emit([total_progress, local_progress])
            except IndexError:
                pass

        proc.stdout.close()
        proc.wait()

        self.downloaded = True

        return 0

    def download_from_m3u8(self, master_m3u8_url, progress, total_progress, season, series):
        m3u8_url = ""
        highest_resolution = 0
        next_line = False
        try:
            for line in urllib.request.urlopen(master_m3u8_url):
                line = line.decode()
                if next_line:
                    next_line = False
                    m3u8_url = line.replace("\n", "")
                try:
                    resolution = re.findall('RESOLUTION=[0-9x]*', line)[0]
                    resolution = int(resolution[11:].split("x")[0])
                    if resolution > highest_resolution:
                        next_line = True
                        highest_resolution = resolution
                except IndexError:
                    pass
        except urllib.error.HTTPError as e:
            print(e)
            return 1

        counter = 0
        for line in urllib.request.urlopen(m3u8_url):
            if line.decode().startswith("seg-"):
                counter += 1

        progress_all = counter

        if not os.path.isdir('./_output'):
            os.mkdir('./_output')
        series.name = re.sub(r'[|\\\/:*"?<>]', '', series.name)
        series_path = os.path.join('./_output', series.name)
        if not os.path.isdir(series_path):
            os.mkdir(series_path)
        season.name = re.sub(r'[|\\\/:*"?<>]', '', season.name)
        season_path = os.path.join(series_path, season.name)
        if not os.path.isdir(season_path):
            os.mkdir(season_path)

        output_file = os.path.join(season_path, f'{self.number}.mp4')

        proc = subprocess.Popen(f'ffmpeg -i "{m3u8_url}" -c copy "{output_file}"', bufsize=1, stdout=subprocess.PIPE,
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
            print(line)
        proc.stdout.close()
        proc.wait()

        self.downloaded = True

        return 0

    def get_download_link(self):
        try:
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

            hoster_url = None
            if preferred_hoster == "vupload":
                hoster_url = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]/a').get_attribute('href')
            elif preferred_hoster == "voe":
                hoster_url = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]/a').get_attribute('href')
            elif preferred_hoster == "streamtape":
                hoster_url = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]/iframe').get_attribute('src')
            elif preferred_hoster == "mixdrop":
                hoster_url = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]/iframe').get_attribute('src')
            elif preferred_hoster == "vidoza":
                hoster_url = self.driver.find_element(By.XPATH, '//*[@id="root"]/section/div[9]/iframe').get_attribute('src')
            elif preferred_hoster == "upstream":
                hoster_url = None
                # TODO Not Implemented due to minified JavaScript (fixable with log reading)
            elif preferred_hoster == "videovard":
                hoster_url = None
                # TODO Not Implemented due to missing Javascript (fixable with log reading)
                # hoster_url = self.driver.find_element(By.XPATH, 'https://videovard.sx/e/hd3elvaixjwb').get_attribute('src')

            self.hoster = preferred_hoster
            self.hoster_url = hoster_url
            return hoster_url
        except selenium.common.exceptions.InvalidArgumentException:
            self.logger.error("Please close any currently running instances of chrome and try again. Also check the Task-Manager. Check the \"bsdl.txt\" file for more information.", exc_info=True)
            return [1, "Error", "Please close any currently running instances of chrome and try again. Also check the Task-Manager. Check the \"bsdl.txt\" file for more information."]
        except selenium.common.exceptions.WebDriverException:
            self.logger.error("It seems like Chrome has been closed manually. Please try again. Check the \"bsdl.txt\" file for more information.", exc_info=True)
            return [1, "Error", "It seems like Chrome has been closed manually. Please try again. Check the \"bsdl.txt\" file for more information."]
        except Exception:
            self.logger.error("Unknown error. Please open up an issue on GitHub (https://github.com/Quadrubo/BSDL) with your error log included (\"bsdl.txt\"). Check the \"bsdl.txt\" file for more information.")
            return [1, "Error", "Unknown error. Please open up an issue on GitHub (https://github.com/Quadrubo/BSDL) with your error log included (\"bsdl.txt\"). Check the \"bsdl.txt\" file for more information."]

    def download(self, progress, total_progress, season, series):
        try:
            if self.hoster_url is None or self.hoster is None:
                callback = self.get_download_link()
                if type(callback) != str:
                    return callback

            hoster_url = self.hoster_url
            preferred_hoster = self.hoster

            if preferred_hoster == "vupload":
                self.driver.get(hoster_url)

                time.sleep(1)

                m3u8_script = self.driver.find_element(By.XPATH, '/html/body/div/script[7]').get_attribute('innerHTML')

                m3u8_url = re.findall('src: ".*master\.m3u8",', m3u8_script)[0]
                m3u8_url = m3u8_url[6:m3u8_url.find(".m3u8") + 5]

                callback = self.download_from_m3u8(m3u8_url, progress, total_progress, season, series)
                if callback != 0:
                    return callback
            elif preferred_hoster == "upstream":
                # TODO Not Implemented due to minified JavaScript (fixable with log reading)
                pass
            elif preferred_hoster == "voe":
                self.driver.get(hoster_url)

                time.sleep(1)

                m3u8_script = self.driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[2]/div/script[4]').get_attribute('innerHTML')

                m3u8_url = re.findall('hls": ".*master\.m3u8",', m3u8_script)[0]
                m3u8_url = m3u8_url[7:m3u8_url.find(".m3u8") + 5]

                callback = self.download_from_m3u8(m3u8_url, progress, total_progress, season, series)
                if callback != 0:
                    return callback
            elif preferred_hoster == "streamtape":
                self.driver.get(hoster_url)

                time.sleep(1)

                self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]').click()

                time.sleep(1)

                self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]').click()

                time.sleep(1)

                mp4_link = self.driver.find_element(By.XPATH, '//*[@id="mainvideo"]').get_attribute('src')

                callback = self.download_from_mp4(mp4_link, progress, total_progress, season, series)
                if callback != 0:
                    return callback
            elif preferred_hoster == "mixdrop":
                self.driver.get(hoster_url)

                time.sleep(1)

                self.driver.find_element(By.XPATH, '//*[@id="videojs"]/button').click()

                time.sleep(1)

                self.driver.find_element(By.XPATH, '//*[@id="videojs_html5_api"]').click()

                mp4_link = self.driver.find_element(By.XPATH, '//*[@id="videojs_html5_api"]').get_attribute('src')

                callback = self.download_from_mp4(mp4_link, progress, total_progress, season, series)
                if callback != 0:
                    return callback
            elif preferred_hoster == "vidoza":
                self.driver.get(hoster_url)

                time.sleep(1)

                self.driver.find_element(By.XPATH, '//*[@id="vplayer"]/div[1]').click()

                time.sleep(1)

                mp4_link = self.driver.find_element(By.XPATH, '//*[@id="player_html5_api"]').get_attribute('src')

                callback = self.download_from_mp4(mp4_link, progress, total_progress, season, series)
                if callback != 0:
                    return callback
            elif preferred_hoster == "videovard":
                # TODO Not Implemented due to missing JavaScript (fixable with log reading)
                pass
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
