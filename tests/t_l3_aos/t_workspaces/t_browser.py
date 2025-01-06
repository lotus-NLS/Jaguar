from pyscrape import SearchEngine, SearchResult

from engine.l3_aos import Browser
from tests.credtest import CredTest

# ----------------------------------------------------------------

class BrowserTest(CredTest):
    def setUp(self):
        self.beaver_test = 'https://en.wikipedia.org/wiki/Beaver'
        self.lightning_site = 'https://lightning.ai/docs/pytorch/stable'
        self.browser = Browser(google_api_key=self.google_apikey, searchengine_id=self.searchengine_id)

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


class SearchEngineTests(CredTest):
    def setUp(self):
        self.search_engine = SearchEngine(searchengine_id=self.searchengine_id, google_key=self.google_apikey)

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
    BrowserTest.execute_all()
    SearchEngineTests.execute_all()
