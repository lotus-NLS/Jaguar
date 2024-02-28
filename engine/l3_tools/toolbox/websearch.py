from ..tool import Tool, ToolArg, Phase

from hollarek.io.web import SearchEngine, SiteVisitor
from engine.l4_singletons.lotus_settings import Settings
# ---------------------------------------------------------

class WebSearch(Tool):
    num_results = 2
    def __init__(self):
        super().__init__()
        self.desc : str = "Search engine that provides result URLs and descriptions"
        self.search_engine : SearchEngine = SearchEngine(google_key=Settings.get_google_apikey(),
                                                         searchengine_id=Settings.get_searchengine_id())

        self.search_term : ToolArg = ToolArg(name='search_term')
        self.num_results : ToolArg = ToolArg(name='number_of_results', is_optional=True)


    def do(self):
        kwargs = {}
        try:
            if self.num_results.val:
                num_results = int(self.num_results.val)
                kwargs = {'num_results' : num_results}
        except:
            pass

        urls = self.search_engine.get_urls(search_term=self.search_term.val, **kwargs)
        formatted_url = '\n'.join(urls)
        self.log(f'Found the following URLs for search term {self.search_term.val}: {formatted_url}',
                 phase=Phase.UPDATE)

    # --------------------------------------------
    #
    # def do(self):
    #     self.search_engine
    #
    #
    #     try:
    #         with ThreadPoolExecutor() as executor:
    #             url_list = self.webtools.get_search_urls(search_term=self.requested_info_arg.val, num_results=WebSearch.num_results)
    #             self.update_log(f'The following URLs were found: {url_list}')
    #
    #             site_reports = list(executor.map(self.get_site_report, url_list))
    #             logging.info(f'Site reports done')
    #
    #         logging.info(f'Requesting summarization')
    #         self.update_log(f'The following information was obtained from web search:'
    #                         f'{self.make_composition_report(site_report_list=site_reports)}')
    #
    #     except Exception as e:
    #         self.exception_log(f'An error occured while trying to browse for sites and summarize information on query: {e}')
    #

# class Browse(Tool):
#     def __init__(self):
#         super().__init__()
#         self.desc = "Browser that lets you read content on pages specified by url"
#         self.url_arg : ToolArg = ToolArg(name=f'url')
#
#     def do(self):
#
