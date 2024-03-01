# from ..application import Tool, ToolArg, Update
#
# from hollarek.io.web import SearchEngine, SiteVisitor
# from engine.l4_singletons.lotus_settings import Settings
# # ---------------------------------------------------------
#
# class WebSearch(Tool):
#     num_results = 2
#     def __init__(self):
#         super().__init__()
#         self.desc : str = "Search engine that provides result URLs and descriptions"
#         self.search_engine : SearchEngine = SearchEngine(google_key=Settings.get_google_apikey(),
#                                                          searchengine_id=Settings.get_searchengine_id())
#
#         self.search_term : ToolArg = ToolArg(name='search_term')
#         self.num_results : ToolArg = ToolArg(name='number_of_results', is_optional=True)
#
#
#     def do(self):
#         kwargs = {}
#         try:
#             if self.num_results.val:
#                 num_results = int(self.num_results.val)
#                 kwargs = {'num_results' : num_results}
#         except:
#             pass
#
#         urls = self.search_engine.get_urls(search_term=self.search_term.val, **kwargs)
#         formatted_url = '\n'.join(urls)
#         self.log(f'Found the following URLs for search term {self.search_term.val}: {formatted_url}',
#                  phase=Update.UPDATE)
#
#
# class ReadSite(Tool):
#     def __init__(self):
#         super().__init__()
#         self.desc = "Browser that lets you read content on pages specified by url"
#         self.url_arg : ToolArg = ToolArg(name=f'url')
#
#
#     def do(self):
#         site_visitor = SiteVisitor()
#         content = site_visitor.get_text(site_url=self.url_arg.val)
#         self.log(f'Content found at {self.url_arg.val}:\n{content}', phase=Update.UPDATE)
#
