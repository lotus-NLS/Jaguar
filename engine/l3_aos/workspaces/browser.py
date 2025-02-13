from typing import Optional

from PIL.Image import Image as PILImage

from engine.l3_aos.workspace import Workspace
from pyscrape.search import SearchEngine
from pyscrape.browse import BrowserEmulator


# ---------------------------------------------------------

class Browser(Workspace):

    def __init__(self, google_api_key : str, searchengine_id : str):
        super().__init__()
        self.search_engine : SearchEngine = SearchEngine(google_api_key=google_api_key, searchengine_id=searchengine_id)
        self.emulator : BrowserEmulator = BrowserEmulator()
        self.search_context : str = ''

    def open(self, url: str):
        """Starts a text based browser and opens the given URL. Use URL=search://{search_term} to perform a google search insted"""
        self.visit(url=url)

    def close(self):
        pass

    def visit(self, url : str):
        """Opens the specified url. Use url=search://{search_term} to perform a google search insted"""
        if url.startswith('search://'):
            search_tearm = url.replace(f'search://','')
            results = self.search_engine.get_results(search_term=search_tearm, num_results=5)
            search_results = f'Results for search term \"{search_tearm}\"\n'
            for index, scrape in enumerate(results):
                search_results += f'({index}): {scrape}\n'
            self.search_context = search_results
        self.emulator.visit(url=url)

    def get_text(self):
        return self.emulator.get_markdown()

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_desc(self) -> str:
        return f"A browser allowing you to search google and browse sites"