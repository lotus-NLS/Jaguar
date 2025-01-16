from typing import Optional
from PIL.Image import Image as PILImage
from bs4 import BeautifulSoup
from pyscrape import SiteVisitor, SearchEngine
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


# Draft for selenium based browing tool
# import time
#
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
#
#
# # Create a new Chrome session
# driver = webdriver.Chrome()
# driver.get("https://www.google.com/")
#
# # Find the search bar, enter text, and submit the search
# # search_bar = driver.find_element(By.NAME, "q")
# # search_bar.send_keys("Selenium WebDriver")  # Change your search query here
# # search_bar.send_keys(Keys.RETURN)  # Pressing the Enter key
#
# # Wait for the cookie message
# time.sleep(1)  # Pause to allow the page and its elements to load fully
#
# # Try to find and click the 'Accept all' button for cookies
# try:
#     accept_cookies_button = driver.find_element(By.XPATH, r'//*[@id="L2AGLb"]/div')
#     accept_cookies_button.click()
# except Exception as e:
#     print("Cookie acceptance button not found:", e)
#
# search_bar = driver.find_element(By.NAME, "q")
# search_bar.send_keys("Selenium WebDriver")  # Change your search query here
# search_bar.send_keys(Keys.RETURN)  # Pressing the Enter key
#
# # Optionally, print the current URL to verify the search
# print(driver.current_url)
#
#
# html_content = driver.page_source
# soup = BeautifulSoup(html_content, 'html.parser')
#
# links = soup.find_all('a', href=True)
#
# # Additionally, find all clickable elements like buttons
# buttons = soup.find_all('button')
# clickable_divs = soup.find_all('button')
#
# # Print all found elements
# print("Links:")
# for link in links:
#     print(link)
#
# print("\nButtons and other clickable elements:")
# for button in buttons:
#     print(button.text)
#
# for div in clickable_divs:
#     print(div)
#
# input()
# driver.quit()
#
#
