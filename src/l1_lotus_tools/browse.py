# noinspection PyPackageRequirements
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
from concurrent.futures import ThreadPoolExecutor, Future

from src.l2_lotus_core import Tool, ToolArg, SinglePurposeAgent
from src.l2_lotus_core import get_setting, Credentials


# ---------------------------------------------------------

# TODO: Investigate: Heavy delay btw site report init and completion request

class BROWSE(Tool):
    num_results = 5

    def __init__(self):
        super().__init__()
        self.desc : str = 'The BROWSE tool allows you to search for information online. ' \
                           'The information you request will be complied based on the top search results from the search term that you specify' \
                           # 'You can use for example to look up documentation or software that can be useful to your project'

        self.query_arg : ToolArg = self.create_arg(name='requested_information', dtype=str,
                                               desc='This is the information that you seek to obtain')

        self.search_term_arg : ToolArg = self.create_arg(name='search_term', dtype=str,
                                               desc='The search_term is what will be used in the search engine to obtain relevant web pages')


    def do(self):
        try:
            # This control flow element is only left once all tasks are done
            with ThreadPoolExecutor(max_workers=4) as executor:
                url_list = Webtools.get_search_result_urls(search_term=self.query_arg.val)
                site_report_futures = [executor.submit(self.get_site_report, url) for url in url_list]

            self.progress_log(f'All reports are done')


            site_reports = [future.result() for future in site_report_futures]
            self.progress_log(f'The following information was obtained from web search:'
                              f'{self.make_composition_report(site_report_list=site_reports)}')

        except Exception as e:
            self.exception_log(f'An error occured while trying to browse for sites and summarize information on query: {e}')


    def get_site_report(self, site_url : str):
        raw_site_text = Webtools.get_url_text(site_url=site_url, wait_for_load_in_sec=1)

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

    @staticmethod
    def get_url_text(site_url: str, wait_for_load_in_sec : int =1) -> str:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(site_url)
        # NOTE : If you should wait or for how long until page elements load is something to be contemplated
        time.sleep(wait_for_load_in_sec)
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        site_text = ''
        for text in [element for element in soup.stripped_strings]:
            site_text += text

        driver.quit()
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