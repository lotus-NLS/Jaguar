# from ..application import Tool, ToolArg, Update
#
# from hollarek.io.web import SearchEngine, SiteVisitor
# from engine.l5_settings.lotus_settings import Settings
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



# from playwright.async_api import async_playwright
#
#
# async def list_all_links_texts_and_focusable_elements():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#         await page.goto('https://example.com')
#
#         # Getting all links
#         links = await page.evaluate('''() => {
#             return Array.from(document.querySelectorAll('a')).map(link => link.href);
#         }''')
#
#         focusable_elements_selector = 'input:not([disabled]), textarea:not([disabled]), a[href]:not([tabindex="-1"]), select:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])'
#         focusable_elements = await page.locator(focusable_elements_selector).element_handles()
#
#         # Extracting details of focusable elements
#         focusable_details = []
#         for element in focusable_elements:
#             tag = await element.evaluate('(element) => element.tagName.toLowerCase()')
#             type_attr = await element.get_attribute('type')
#             value_or_placeholder = await element.input_value() if tag in ['input',
#                                                                           'textarea'] else await element.get_attribute(
#                 'placeholder')
#             focusable_details.append({'tag': tag, 'type': type_attr, 'value_or_placeholder': value_or_placeholder})
#
#         print("Focusable Elements:", focusable_details)
#
#         # Getting all text on the page
#         all_text = await page.evaluate('''() => {
#             return document.body.innerText;
#         }''')
#
#         print("Links:", links)
#         print("Focusable Fields:", focusable_fields)
#         print("All Text on Page:", all_text)
# 
#         await browser.close()
#
#
# # Execute the modified function
# import asyncio
#
# asyncio.run(list_all_links_texts_and_focusable_elements())
#
# from playwright.async_api import async_playwright
#
#
# async def list_focusable_elements():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#         await page.goto('https://example.com')
#
#         # Locating focusable elements by checking if they can be focused by keyboard
#         # This includes elements that are inputs, buttons, links with hrefs, or have a tabindex that's not negative.
#         focusable_elements_selector = 'input:not([disabled]), textarea:not([disabled]), a[href]:not([tabindex="-1"]), select:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])'
#         focusable_elements = await page.locator(focusable_elements_selector).element_handles()
#
#         # Extracting details of focusable elements
#         focusable_details = []
#         for element in focusable_elements:
#             tag = await element.evaluate('(element) => element.tagName.toLowerCase()')
#             type_attr = await element.get_attribute('type')
#             value_or_placeholder = await element.input_value() if tag in ['input',
#                                                                           'textarea'] else await element.get_attribute(
#                 'placeholder')
#             focusable_details.append({'tag': tag, 'type': type_attr, 'value_or_placeholder': value_or_placeholder})
#
#         print("Focusable Elements:", focusable_details)
#
#         await browser.close()
#
#
# # Execute the function
# import asyncio
#
# asyncio.run(list_focusable_elements())
