import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests

from src.l2_lotus_core import Tool, ToolArg, SinglePurposeAgent
from src.l2_lotus_core import get_setting, Credentials


# NOTE : If you should wait or for how long until page elements load is something to be contemplated

# ---------------------------------------------------------

# TODO: Investigate: Heavy delay btw site report init and completion request
# -> I think the heaviest part of that is starting up the

class BROWSE(Tool):
    num_results = 5

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
            url_list = self.webtools.get_search_result_urls(search_term=self.query_arg.val)
            site_reports = [self.get_site_report(url) for url in url_list]

            self.progress_log(f'All reports are done')
            self.progress_log(f'The following information was obtained from web search:'
                              f'{self.make_composition_report(site_report_list=site_reports)}')

        except Exception as e:
            self.exception_log(f'An error occured while trying to browse for sites and summarize information on query: {e}')


    def get_site_report(self, site_url : str):
        raw_site_text = self.webtools.get_url_text(site_url=site_url, wait_for_load_in_sec=1)

        summary_agent = SinglePurposeAgent.make_website_summarization_agent()
        input_text = summary_agent.model.get_limited_string(the_str=raw_site_text,max_tokens=2000)

        the_text = summary_agent.get_text_response(
            prompt=f'Website text:\n {input_text}\n Query: {self.query_arg.val}',
            max_token=300)

        return the_text


    def make_composition_report(self, site_report_list : list[str]):
        all_summaries = ''
        for index, info_text in enumerate(site_report_list):
            all_summaries += f'## Report {index} ##' \
                             f'{info_text}\n'

        composition_agent = SinglePurposeAgent.make_report_composition_agent()
        return composition_agent.get_text_response(prompt=f'Reports:  {all_summaries}'
                                                       f'Query: {self.query_arg.val}'
                                                       ,max_token=500)


class Webtools:
    def __init__(self, initial_driver_count : int = 4):
        self.drivers = []
        self.busy_drivers = []

        for _ in range(initial_driver_count):
            threading.Thread(target=self.make_driver).start()

    def make_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        new_driver = webdriver.Chrome(options=chrome_options)

        self.drivers.append(new_driver)

        return new_driver

    def get_free_driver(self):
        unoccupied_drivers = [driver for driver in self.drivers if driver not in self.busy_drivers]
        if len(unoccupied_drivers) > 0:
            return unoccupied_drivers[0]

        else:
            return self.make_driver()

    def get_url_text(self,site_url: str, wait_for_load_in_sec : float = 0.2) -> str:
        start_time = time.time()

        driver = self.get_free_driver()
        self.busy_drivers.append(driver)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: It took {elapsed_time} seconds to retrieve a driver")

        driver.get(site_url)
        time.sleep(wait_for_load_in_sec)
        page_source = driver.page_source

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: It took {elapsed_time} seconds to get the site info")

        soup = BeautifulSoup(page_source, 'html.parser')
        site_text = ''
        for text in [element for element in soup.stripped_strings]:
            site_text += text

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: It took {elapsed_time} seconds to scrape the site")

        self.busy_drivers.remove(driver)

        return site_text


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

        print(f'[Temp debug]: The following URLs were found: {search_result_urls}')

        return search_result_urls