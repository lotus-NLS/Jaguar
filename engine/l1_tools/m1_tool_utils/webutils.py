from __future__ import annotations
from pyutils import DaemonThread
import time
import requests
import trafilatura
from bs4 import BeautifulSoup
from func_timeout import func_timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from engine.l3_settings import get_setting, CredentialSettings

from engine.l1_tools.m1_tooldef.tool import Tool
# ---------------------------------------------------------


class Webtools:
    def __init__(self, initial_driver_count : int = 4):
        self.drivers : list[WebDriver] = []

        for _ in range(initial_driver_count):
            start_thread = DaemonThread(target=self.make_driver)
            start_thread.start()

    def get_url_text(self,site_url: str, mode : ScrapeMode) -> str:
        driver = self.get_free_driver()
        try:
            if mode == 'dynamic':
                result = driver.fetch_dynamic_content(site_url, wait_for_load_in_sec=2)
            else:
                result = driver.fetch_static_content(site_url)

        except:
            result = f'Failed to retrieve text from website {site_url}'

        return result


    def get_free_driver(self):
        unoccupied_drivers = [driver for driver in self.drivers if not driver.is_busy]
        if len(unoccupied_drivers) > 0:
            return unoccupied_drivers[0]

        else:
            return self.make_driver()


    def make_driver(self):
        new_driver = WebDriver()
        self.drivers.append(new_driver)

        return new_driver


    @staticmethod
    def get_search_urls(search_term: str, num_results : int = 4):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': f'{search_term}',
            'key': get_setting(CredentialSettings.google_apikey_label),
            'cx': get_setting(CredentialSettings.search_engineID_label),
            'num' : num_results
        }
        search_results = requests.get(url, params=params).json()['items']
        search_result_urls = [result['link'] for result in search_results]


        return search_result_urls


class ScrapeMode(str):
    def __new__(cls, mode : str):
        return str.__new__(cls, mode)

    @classmethod
    def dynamic_mode(cls):
        return cls(mode='dynamic')

    @classmethod
    def static_mode(cls):
        return cls(mode='static')



class WebDriver:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.engine = webdriver.Chrome(options=chrome_options)
        self.is_busy = False

    def fetch_dynamic_content(self, site_url: str, wait_for_load_in_sec: float = 2) -> str:
        self.is_busy = True

        self.engine.get(site_url)
        time.sleep(wait_for_load_in_sec)
        page_source = self.engine.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        site_text = ''.join(element for element in soup.stripped_strings)

        self.is_busy = False
        return site_text

    def fetch_static_content(self, site_url: str) -> str:
        self.is_busy = True

        def get_website_text():
            downloaded = trafilatura.fetch_url(site_url)
            return trafilatura.extract(downloaded)

        content = func_timeout(timeout=Tool.timout_in_sec / 2., func=get_website_text)
        self.is_busy = False
        return content




