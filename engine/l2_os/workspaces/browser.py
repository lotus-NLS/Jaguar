from typing import Optional
from PIL.Image import Image as PILImage
from bs4 import BeautifulSoup
from hollarek.web import SiteVisitor, SearchEngine
from engine.l5_settings import LotusSettings
from urllib.parse import urlparse
from .workspace import Workspace

# ---------------------------------------------------------

class Browser(Workspace):
    def __init__(self):
        super().__init__()
        self.current_dir_path: Optional[str] = None
        self.show_hidden : bool = True
        self.currrent_url : Optional[str] = None
        self.site_visitor : Optional[SiteVisitor] = None
        google_key, searchengine_id = LotusSettings.get_google_apikey(), LotusSettings.get_searchengine_id()
        self.search_engine : SearchEngine = SearchEngine(google_key=google_key, searchengine_id=searchengine_id)
        self.search_context : Optional[str] = None

    def open(self, url: str):
        """Opens the specified site. Use url=search://{search_term} to perform a google search insted"""
        if url.startswith('search://'):
            search_tearm = url.replace(f'search://','')
            self.search(search_term=search_tearm)
        else:
            self.visit_site(url=url)


    def close(self):
        """Close LotusFileExplorer"""
        self.currrent_url = None
        self.site_visitor= None

    def search(self, search_term : str, num_results : int = 4):
        """Googles the search_term and displays results"""
        urls = self.search_engine.get_urls(search_term=search_term, num_results=num_results)
        self.search_context = f'Results for search term \"{search_term}\"\n'
        for index, site in enumerate(urls):
            self.search_context += f'({index}): {site}\n'

    def visit_site(self, url : str):
        """Visit another site"""
        self.currrent_url = url
        self.site_visitor = SiteVisitor(headless=False)

    # ---------------------------------------------------------
    # context

    def get_image(self) -> Optional[PILImage]:
        return None


    def get_text(self) -> str:
        browser_text = ''
        if self.search_context:
            browser_text += self.search_context
        if self.currrent_url:
            browser_text += self._get_site_text()
        return browser_text


    def _get_site_text(self) -> str:
        info_text = f'---> Currently visiting site: {self.currrent_url}\n\n'
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
        return f"A browser to google for and visit sites"
