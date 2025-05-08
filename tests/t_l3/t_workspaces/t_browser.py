import os

from engine.l3_aos import Browser
from tests.basetests import CredTest

# ----------------------------------------------------------------

class BrowserTest(CredTest):
    def setUp(self):
        self.beaver_test = 'https://en.wikipedia.org/wiki/Beaver'
        self.lightning_site = 'https://lightning.ai/docs/pytorch/stable'
        self.browser : Browser = Browser(google_api_key=self.google_api_key,
                                         searchengine_id=self.searchengine_id,
                                         headless=True)

    def test_visit(self):
        self.browser.open(url=self.beaver_test)
        beaver_text = self.browser.get_text()
        print(f'Browser context after opening wikipedia {beaver_text[:1000]}...')
        self.assertIn('beaver', beaver_text.lower())
        self.assertTrue(f'/wiki/Talk:Beaver'.lower() in beaver_text.lower())

        self.browser.open(url=self.lightning_site)
        lightning_text = self.browser.get_text()
        self.assertIn('lightning', lightning_text.lower())
        self.assertIn(self.lightning_site, lightning_text.lower())

    def test_search(self):
        self.browser.open(url=f'search://wikipedia beavers')
        browser_context = self.browser.get_text()
        print(f'Browser context after search =\n {browser_context}')
        self.assertIn('Search engine', browser_context)
        self.assertTrue(f'https://en.wikipedia.org/wiki/Beaver' in browser_context)

    @staticmethod
    def has_graphic_capabilities() -> bool:
        try:
            _ = os.environ['DISPLAY']
            return True
        except:
            return False

    def tearDown(self):
        self.browser.emulator.quit()


if __name__ == "__main__":
    BrowserTest.execute_all()