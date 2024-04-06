from engine.l2_os import Browser
from hollarek.devtools import Unittest

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

if __name__ == "__main__":
    BrowserTest.execute_all()