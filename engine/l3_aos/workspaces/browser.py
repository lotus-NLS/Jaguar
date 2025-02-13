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
        self.emulator : BrowserEmulator = BrowserEmulator(headless=False)
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
        else:
            self.emulator.visit(url=url)

    def enter_text(self, input_field_idx : int, content : str):
        self.emulator.type(text_box_idx=input_field_idx, content=content)

    def get_text(self):
        text = f'+------------------- {self.__class__.__name__} --------------------+\n'
        text += f'| Current site: {self.emulator.driver.current_url} |\n'
        text += f'+------------------- Site Content: -------------------------+\n'
        text += f'{self.emulator.get_markdown()}\n'


        textinput_fields  = self.emulator.get_textinputs()
        text += f'+------------------- Available text input fields: -------------------------+\n'
        text += f'Available text inputs:\n'
        for j, t in enumerate(textinput_fields):
            placeholder = t.get_attribute(name="placeholder")
            text += f'- Input field Index=[{j}]: | {placeholder} | \n'

        if self.search_context:
            text += f'+-------- Search engine --------+'
            text += self.search_context
        text += f'+------------------- /{self.__class__.__name__} --------------------+\n'

        return text

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_desc(self) -> str:
        return f"A browser allowing you to search google and browse sites"

if __name__ == "__main__":
    from holytools.configs import FileConfigs
    creds = FileConfigs.credentials()

    g_api_key = creds.get(key='google_api_key')
    search_engine_id = creds.get(key='search_engine_id')

    br = Browser(google_api_key=g_api_key, searchengine_id=search_engine_id)
    print(f'Current URL:')
    print(br.emulator.driver.current_url)