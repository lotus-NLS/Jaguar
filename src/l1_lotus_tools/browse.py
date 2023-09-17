import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
from concurrent.futures import ThreadPoolExecutor
import trafilatura

from src.l2_lotus_core import Tool, ToolArg, SinglePurposeAgent
from src.l2_lotus_core import get_setting, Credentials
from func_timeout import func_timeout

# NOTE : If you should wait or for how long until page elements load is something to be contemplated

# ---------------------------------------------------------

class BROWSE(Tool):
    num_results = 4
    def __init__(self):
        super().__init__()
        self.desc : str = """The BROWSE tool allows you to search for information online.Provide both a "search_term" and specify the "requested_information"."""

        self.query_arg : ToolArg = self.create_arg(name='requested_information', dtype=str,
                                               desc='This is the information that you seek to obtain')

        self.search_term_arg : ToolArg = self.create_arg(name='search_term', dtype=str,
                                               desc='The search_term is what will be used in the search engine to obtain relevant web pages')

        self.webtools : Webtools = Webtools(initial_driver_count=4)


    def do(self):
        try:
            with ThreadPoolExecutor() as executor:
                url_list = self.webtools.get_search_result_urls(search_term=self.query_arg.val,num_results=BROWSE.num_results)
                self.progress_log(f'The following URLs were found: {url_list}')
                site_reports = list(executor.map(self.get_site_report, url_list))


            self.progress_log(f'All reports are done')
            self.progress_log(f'The following information was obtained from web search:'
                              f'{self.make_composition_report(site_report_list=site_reports)}')

        except Exception as e:
            self.exception_log(f'An error occured while trying to browse for sites and summarize information on query: {e}')


    def get_site_report(self, site_url : str):
        try:
            raw_site_text = self.webtools.get_url_text(site_url=site_url)

            summary_agent = SinglePurposeAgent.make_website_summarization_agent()
            input_text = summary_agent.model.get_limited_string(the_str=raw_site_text,max_tokens=2000)

            # print(f'[Temp debug]: The site {site_url} provided the following text: {input_text}')
            result = summary_agent.get_text_response(
                prompt=f'Website text:\n {input_text}\n Query: {self.query_arg.val}',
                max_token=300)
        except:
            result = f'An exception occured while trying to get report on site {site_url}. Aborting ...'

        # print(f'The following summary was acquired for {site_url}: {result}')
        return result

    #
    def make_composition_report(self, site_report_list : list[str]):
        all_summaries = ''
        for index, info_text in enumerate(site_report_list):
            all_summaries += f'## Report {index} ##' \
                             f'{info_text}\n'

        composition_agent = SinglePurposeAgent.make_report_composition_agent()
        composition_agent.get_text_response(prompt=f'Reports:  {all_summaries}\n Query: {self.query_arg.val}'
                                                   f'First evaluate the sources for their usefulness for the query, and make an outline of what you learned',
                                            max_token=500)
        return composition_agent.get_text_response(prompt=f'Now provide an answer to the initial query: {self.query_arg.val}',verbose=False)


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
        # def get_website_text():
        #     response = requests.get(site_url)
        #     soup = BeautifulSoup(response.text, 'html.parser')
        #     the_site_text = ''.join(element for element in soup.stripped_strings)
        #     return the_site_text

        def get_website_text():
            downloaded = trafilatura.fetch_url(site_url)
            return trafilatura.extract(downloaded)


        return func_timeout(timeout=Tool.timout_in_sec/2., func=get_website_text)


    @staticmethod
    def get_search_result_urls(search_term: str, num_results : int = 4):
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