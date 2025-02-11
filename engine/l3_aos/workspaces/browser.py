from typing import Optional
from PIL.Image import Image as PILImage
from bs4 import BeautifulSoup
from pyscrape.site import SiteVisitor
from pyscrape.search import SearchEngine
from urllib.parse import urlparse

from engine.l3_aos.workspace import Workspace


# ---------------------------------------------------------

class Browser(Workspace):
    def __init__(self, google_api_key : str, searchengine_id : str):
        super().__init__()
        self.current_dir_path: Optional[str] = None
        self.show_hidden : bool = True
        self.currrent_url : Optional[str] = None
        self.site_visitor : Optional[SiteVisitor] = None
        self.search_engine : SearchEngine = SearchEngine(google_key=google_api_key, searchengine_id=searchengine_id)
        self.search_context : Optional[str] = None

    def open(self, url: str):
        """Opens the specified site. Use url=search://{search_term} to perform a google search insted"""
        if url.startswith('search://'):
            search_tearm = url.replace(f'search://','')
            self.google_search(search_term=search_tearm)
        else:
            self.visit_site(url=url)


    def close(self):
        """Close Browser"""
        self.currrent_url = None
        if self.site_visitor:
            self.site_visitor.quit()
        self.site_visitor = None

    def google_search(self, search_term : str, num_results : int = 4):
        """Googles the search term and displays links/summaries of top results"""
        results = self.search_engine.get_results(search_term=search_term, num_results=num_results)
        self.search_context = f'Results for search term \"{search_term}\"\n'
        for index, site in enumerate(results):
            self.search_context += f'({index}): {site}\n'

    def visit_site(self, url : str):
        """Visits the selected site in the browser"""
        self.currrent_url = url
        self.site_visitor = SiteVisitor(headless=False)

    # ---------------------------------------------------------
    # context

    def get_image(self) -> Optional[PILImage]:
        return None


    def get_text(self) -> str:
        browser_text = ''
        if self.search_context:
            browser_text += f'{self.search_context}\n'
        if self.currrent_url:
            if self.site_visitor.site_exists(url=self.currrent_url):
                browser_text += self._get_site_text()
            else:
                browser_text += f'---> Site does not exist: {self.currrent_url}\n'
        return browser_text

    def _get_site_text(self) -> str:
        info_text = f'---> Currently visiting site: {self.currrent_url}\n'
        page_source = self.site_visitor.get_html(url=self.currrent_url)
        soup = BeautifulSoup(page_source, 'html.parser')
        links = soup.find_all('a')

        def get_repr(link):
            link_text = link.get_text(strip=True)
            content = link.get('href')

            parsed_url = urlparse(self.currrent_url)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

            if not content.startswith('http'):
                prefix = '' if content.startswith('/') else '/'
                content = f'{base_domain}{prefix}{content}'

            return f"[{link_text}]({content})"

        def link_qualifes(link):
            href_content = link.get('href')
            if not href_content:
                return False
            return True

        markdown_links = [get_repr(link) for link in links if link_qualifes(link)]
        links_content = '\n'.join(markdown_links)
        site_text = f'- Site text: \n{self.site_visitor.get_text(url=self.currrent_url)}\n'
        links_text = f'- Links: \n {links_content}'


        return f'{info_text}{site_text}\n{links_text}'


    def get_desc(self) -> str:
        return f"A browser allowing you to perform a google search and visit sites"



#
# # Draft for selenium based browing tool
# import time
#
# import undetected_chromedriver as uc
# from selenium.webdriver import Keys
# from selenium.webdriver.common.by import By
#
#
# # setting the driver path and requesting a page
# driver = uc.Chrome()
#
# w1 = "https://docs.ros.org/en/foxy/index.html"
# w2 = 'https://platform.openai.com/docs/libraries#community-libraries'
# w3 = 'https://www.youtube.com/'
# w4 = 'https://stackexchange.com/'
#
# # stealth(driver,
# #         languages=["en-US", "en"],
# #         platform="Linux",
# #         )
#
# driver.get(w3)
# time.sleep(2)
#
#
# # Recognizing (visible) links
# # links = driver.find_elements(By.TAG_NAME, 'a')
# # visible_links = [link for link in links if link.is_displayed()]
# # invisble_links = [link for link in links if not link.is_displayed()]
# #
# # print(f'- Visible links')
# # for link in visible_links:
# #     print(link.get_attribute('href'))
# #
# # print(f'- Invisible links')
# # for link in invisble_links:
# #     print(link.get_attribute('href'))
#
#
# # Recognizing and interacting with (visible) text inputs
# text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
# visible_text_inputs = [input_box for input_box in text_inputs if input_box.is_displayed()]
#
# search_box = visible_text_inputs[0]
# search_box.send_keys("my_username" + Keys.RETURN)
#
# time.sleep(2)
#
# for input_box in text_inputs:
#     print(input_box.get_attribute('accessible_name'))
#
# print('done')
#
# driver.quit()