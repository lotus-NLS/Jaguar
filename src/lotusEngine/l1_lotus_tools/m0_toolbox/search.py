from concurrent.futures import ThreadPoolExecutor
from src.lotusEngine.l2_lotus_agent.m0_agent.tool_handler import ToolArg

from src.lotusEngine.l1_lotus_tools.m0_toolbox.tool import Tool
from src.lotusEngine.l1_lotus_tools.m1_tool_utils.webutils import Webtools, ScrapeMode
from src.lotusEngine.l1_lotus_tools.m1_tool_utils.text_agent import TextAgent

# NOTE : If you should wait or for how long until page elements load is something to be contemplated
# ---------------------------------------------------------

class SEARCH(Tool):
    num_results = 4
    def __init__(self):
        super().__init__()
        self.desc : str = """Obtains a text report from the web"""

        self.requested_info_arg : ToolArg = self.create_arg(
            name='requested_information', dtype=str,
            desc='')

        self.webtools : Webtools = Webtools(initial_driver_count=4)

    # --------------------------------------------
    #

    def do(self):
        try:
            with ThreadPoolExecutor() as executor:
                url_list = self.webtools.get_search_urls(search_term=self.requested_info_arg.val, num_results=SEARCH.num_results)
                self.update_log(f'The following URLs were found: {url_list}')

                site_reports = list(executor.map(self.get_site_report, url_list))
                print(f'[Debug]: Site reports done')

            print(f'[Debug]: Requesting summarization')
            self.update_log(f'The following information was obtained from web search:'
                            f'{self.make_composition_report(site_report_list=site_reports)}')

        except Exception as e:
            self.exception_log(f'An error occured while trying to browse for sites and summarize information on query: {e}')

    # --------------------------------------------
    #

    def get_site_report(self, site_url : str):
        try:
            summary_agent = TextAgent.make_website_summarization_agent()

            raw_site_text = self.webtools.get_url_text(site_url=site_url, mode=ScrapeMode.dynamic_mode())
            input_text = summary_agent.model.get_limited_string(the_str=raw_site_text,max_tokens=2000)
            summary_agent.think(msg=f'Website text:\n {input_text}\n Query: {self.requested_info_arg.val}')

            result = summary_agent.get_text_response(max_tokens=300)
        except:
            result = f'An exception occured while trying to get report on site {site_url}. Aborting ...'

        return result


    def make_composition_report(self, site_report_list : list[str]):
        all_summaries = ''
        for index, info_text in enumerate(site_report_list):
            all_summaries += f'## Report {index} ##' \
                             f'{info_text}\n'
        composition_agent = TextAgent.make_report_composition_agent()

        # Evaluate sources
        composition_agent.log_system_msg(msg=f'Reports:  {all_summaries}\n Query: {self.requested_info_arg.val}'
                                    f'First evaluate the sources for their usefulness for the query'
                                    f', and make an outline of what you learned')
        evaluation = composition_agent.get_text_response(max_tokens=300)
        composition_agent.think(evaluation)

        # Make report
        composition_agent.log_system_msg(f'Now provide an answer to the initial query: {self.requested_info_arg.val}')
        summary = composition_agent.get_text_response(max_tokens=300)

        return summary


