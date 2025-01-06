from engine.l0_engine.settings import LotusCredentials
from engine.l3_os import Browser
from holytools.devtools import Unittest
from pyscrape import SearchEngine, SearchResult

class BrowserTest(Unittest):
    def setUp(self):
        self.beaver_test = 'https://en.wikipedia.org/wiki/Beaver'
        self.lightning_site = 'https://lightning.ai/docs/pytorch/stable'
        self.browser = Browser()

    def test_beaver(self):
        self.browser.open(url=self.beaver_test)
        beaver_text = self.browser.get_text()
        self.assertIn('beaver', beaver_text.lower())
        self.assertIn(f'https://en.wikipedia.org/wiki/Talk:Beaver'.lower(), beaver_text.lower())
        print(f'Beaver text =\n {beaver_text}')

    def test_lightning(self):
        self.browser.open(url=self.lightning_site)
        lightning_text = self.browser.get_text()
        self.assertIn('lightning', lightning_text.lower())
        self.assertIn(self.lightning_site, lightning_text.lower())
        print(f'Lightning text =\n {lightning_text}')


class SearchEngineTester(Unittest):
    @classmethod
    def setUpClass(cls):
        creds = LotusCredentials(use_local=True)
        engine_id = creds.get_searchengine_id()
        api_key = creds.get_google_apikey()
        cls.search_engine = SearchEngine(searchengine_id=engine_id, google_key=api_key)

    def test_urls(self):
        urls = self.search_engine.get_urls(search_term='beavers')
        for url in urls:
            self.assertIsInstance(url, str)

    def test_results(self):
        results = self.search_engine.get_results(search_term = 'beavers')
        for result in results:
            self.assertIsInstance(result, SearchResult)
            print(result)


if __name__ == "__main__":
    # BrowserTest.execute_all()
    SearchEngineTester.execute_all()