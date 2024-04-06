from typing import Optional
from PIL.Image import Image as PILImage
from bs4 import BeautifulSoup
from hollarek.web import SiteVisitor
from .workspace import Workspace

# ---------------------------------------------------------

class Browser(Workspace):
    def __init__(self):
        super().__init__()
        self.current_dir_path: Optional[str] = None
        self.show_hidden : bool = True
        self.currrent_url : Optional[str] = None
        self.site_visitor : SiteVisitor = SiteVisitor()

    def open(self, url: str):
        """Opens the specified site"""
        self.currrent_url = url

    def close(self):
        """Close LotusFileExplorer"""
        self.currrent_url = None

    # ---------------------------------------------------------
    # context

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_text(self) -> str:
        page_source = self.site_visitor.get_html(url=self.currrent_url)
        soup = BeautifulSoup(page_source, 'html.parser')
        links = soup.find_all('a')

        def get_repr(link):
            link_text = link.get_text(strip=True)
            content = link.get('href')

            if not content.startswith('http'):
                content = f'{self.currrent_url}/{content}'

            return f"[{link_text}]({content})"

        def link_qualifes(link):
            href_content = link.get('href')
            if not href_content:
                return False
            return True

        markdown_links = [get_repr(link) for link in links if link_qualifes(link)]
        link_content = '\n'.join(markdown_links)
        site_text = self.site_visitor.get_text(url=self.currrent_url)

        return f'{site_text}\n{link_content}'

    def get_desc(self) -> str:
        return f"A file explorer to navigate and display file structures"
