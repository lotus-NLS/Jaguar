from concurrent.futures import ThreadPoolExecutor

from src.l1_lotus_tools.m1_python_utils.webtools import Webtools
from src.l2_lotus_core import Tool, ToolArg, SinglePurposeAgent


# NOTE : If you should wait or for how long until page elements load is something to be contemplated

# ---------------------------------------------------------

class BROWSE(Tool):
    num_results = 4
    def __init__(self):
        super().__init__()
        self.desc : str = """The BROWSE tool allows you to search for information online.Provide both a "search_term" and specify the "requested_information"."""

        self.query_arg : ToolArg = self.create_arg(
            name='requested_information', dtype=str,
            desc='This is the information that you seek to obtain')

        self.search_term_arg : ToolArg = self.create_arg(
            name='search_term', dtype=str,
            desc='The search_term is what will be used in the search engine to obtain relevant web pages')

        self.webtools : Webtools = Webtools(initial_driver_count=4)


    def do(self):
        try:
            with ThreadPoolExecutor() as executor:
                url_list = self.webtools.get_search_urls(search_term=self.query_arg.val, num_results=BROWSE.num_results)
                self.progress_log(f'The following URLs were found: {url_list}')
                site_reports = list(executor.map(self.get_site_report, url_list))

            self.progress_log(f'The following information was obtained from web search:'
                              f'{self.make_composition_report(site_report_list=site_reports)}')

        except Exception as e:
            self.exception_log(f'An error occured while trying to browse for sites and summarize information on query: {e}')


    def get_site_report(self, site_url : str):
        try:
            raw_site_text = self.webtools.get_url_text(site_url=site_url)

            summary_agent = SinglePurposeAgent.make_website_summarization_agent()
            input_text = summary_agent.model.get_limited_string(the_str=raw_site_text,max_tokens=2000)

            result = summary_agent.get_text_response(
                prompt=f'Website text:\n {input_text}\n Query: {self.query_arg.val}',
                max_token=300)
        except:
            result = f'An exception occured while trying to get report on site {site_url}. Aborting ...'

        return result


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

