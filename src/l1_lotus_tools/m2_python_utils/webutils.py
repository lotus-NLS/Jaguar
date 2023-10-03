import threading
import time

import requests
import trafilatura
from bs4 import BeautifulSoup
from func_timeout import func_timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.l2_lotus_agent import get_setting, Credentials
from src.l1_lotus_tools.m0_tool_class.tool import Tool


# ---------------------------------------------------------


class ScrapeModes:
    dynamic = 'dynamic'
    static = 'static'


class Webtools:
    def __init__(self, initial_driver_count : int = 4):
        self.drivers = []
        self.busy_drivers = []

        for _ in range(initial_driver_count):
            threading.Thread(target=self.make_driver).start()

    def get_url_text(self,site_url: str, mode = ScrapeModes.static) -> str:
        try:
            if mode == 'dynamic':
                result = self.fetch_dynamic_content(site_url, wait_for_load_in_sec=2)
            else:
                result = self.fetch_static_content(site_url)

        except:
            result = f'Failed to retrieve text from website {site_url}'

        return result

    def fetch_dynamic_content(self, site_url: str, wait_for_load_in_sec: float = 2) -> str:
        driver = self.get_free_driver()
        self.busy_drivers.append(driver)

        driver.get(site_url)
        time.sleep(wait_for_load_in_sec)
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        site_text = ''.join(element for element in soup.stripped_strings)

        self.busy_drivers.remove(driver)
        driver.quit()

        return site_text

    def get_free_driver(self):
        unoccupied_drivers = [driver for driver in self.drivers if driver not in self.busy_drivers]
        if len(unoccupied_drivers) > 0:
            return unoccupied_drivers[0]

        else:
            return self.make_driver()

    def make_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        new_driver = webdriver.Chrome(options=chrome_options)
        self.drivers.append(new_driver)

        return new_driver


    @staticmethod
    def fetch_static_content(site_url: str) -> str:
        def get_website_text():
            downloaded = trafilatura.fetch_url(site_url)
            return trafilatura.extract(downloaded)

        return func_timeout(timeout=Tool.timout_in_sec/2., func=get_website_text)


    @staticmethod
    def get_search_urls(search_term: str, num_results : int = 4):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': f'{search_term}',
            'key': get_setting(Credentials.google_apikey_label),
            'cx': get_setting(Credentials.search_engineID_label),
            'num' : num_results
        }
        search_results = requests.get(url, params=params).json()['items']
        search_result_urls = [result['link'] for result in search_results]


        return search_result_urls
