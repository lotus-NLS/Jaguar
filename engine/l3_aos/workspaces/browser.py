from typing import Optional

from PIL.Image import Image as PILImage

from engine.l3_aos.workspace import Workspace

from pyscrape.search import SearchEngine
from pyscrape.browse import BrowserEmulator


# ---------------------------------------------------------

class Browser(Workspace):
    """A browser allowing you to search google and browse sites"""
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
            for index, r in enumerate(results):
                search_results += f'({index}): {r}\n'
            self.search_context = search_results
        else:
            self.emulator.visit(url=url)

    def enter_text(self, input_field_idx : int, content : str):
        self.emulator.type(text_box_idx=input_field_idx, content=content)

    def get_text(self):
        md_text = self.emulator.get_markdown(max_width=150)
        h1 = f'Current site'
        h2 = f'Site content'
        h3 = f'Available text input fields'
        h4 = f'Search engine'
        lines = [line for line in md_text.split('\n')] + [h1, h2, h3, h4]
        longest_line_length = max([len(l) for l in lines])

        text = ''
        text += h1.center(longest_line_length, '-') + '\n'
        text += f'{self.emulator.driver.current_url} \n'


        text += f'{h2.center(longest_line_length, "-")}\n'
        text += f'{md_text}\n'

        textinput_fields  = self.emulator.get_textinputs()
        text += f'{h3.center(longest_line_length, "-")}\n'
        for j, t in enumerate(textinput_fields):
            placeholder = t.get_attribute(name="placeholder")
            text += f'- Input field Index=[{j}]: | {placeholder} | \n'

        if self.search_context:
            text += f'{h4.center(longest_line_length, "-")}\n'
            text += self.search_context

        return text

    def get_image(self) -> Optional[PILImage]:
        return None

if __name__ == "__main__":
    docstring = Browser.__doc__
    print(docstring)