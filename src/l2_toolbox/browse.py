# noinspection PyPackageRequirements
from googlesearch import search #  It's googlesearch-python, it's in there

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

from concurrent.futures import ThreadPoolExecutor, Future

from src.l3_agent.agent import Agent
from src.l3_agent.tool import Tool
from src.l3_agent.tool import ToolArg


# ---------------------------------------------------------

# TODO: The agent identity descriptions should not be he but rather in a file in protocol
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
            with ThreadPoolExecutor() as executor:
                search_result_urls_list = search(self.query_arg.val, num_results=BROWSE.num_results)
                site_report_futures = [executor.submit(self.get_site_report, result_link_str) for result_link_str in search_result_urls_list]

            self.progress_log(f'The following information was obtained from web search \n'
                              f'{self.make_composition_report(site_report_futures)}')

        except Exception:
            self.error_log('An error occured while trying to browse for sites and summarize information on query')


    def get_site_report(self, site_url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(site_url)
        time.sleep(2)
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        site_text = ''
        for text in [element for element in soup.stripped_strings]:
            site_text += text

        driver.quit()

        summary_agent = Agent(identity='You are tasked with summarizing the content of a website to answer a query.'
                                       'You will be provided with a query and the text content of a website.'
                                       'When you are provided with the text content of the website, write a report that summarizes'
                                       'all information relevant to the query that you can find on the site')
        summary_agent.log_user_msg(msg=f'Website text:\n {site_text}\n'
                                       f'Query: {self.query_arg.val}')
        return summary_agent.get_next_action(is_allowed_functioncall=False).get_text_content()


    def make_composition_report(self, site_report_futures : list[Future]):
        all_summaries = ''
        for index,future in enumerate(site_report_futures):
            all_summaries += f'## Report {index} ##' \
                             f'{future.result()}\n'
        # TODO: The report length should be enforced through max_token = ... in openAI response options
        composition_agent=Agent(identity='You are tasked with producing information that answers a query.'
                                         'You will be provided with a list of reports which each present the information relevant to the query'
                                         'that was obtained from searching through a website.'
                                         'Upon request you will produce a report that answers the query using the information provided in the reports'
                                         'Keep the length of the report down to less than 200 words')
        composition_agent.log_user_msg(msg=f'Reports:  {all_summaries}'
                                           f'Query: {self.query_arg.val}')
        return composition_agent.get_next_action(is_allowed_functioncall=False).get_text_content()
