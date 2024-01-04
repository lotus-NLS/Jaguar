import trafilatura, logging
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests


def get_website_text_bs4(site_url):
    start_time = time.time()
    response = requests.get(site_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    web_text = soup.stripped_strings
    web_text = ' '.join(web_text)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return web_text, elapsed_time


def fetch_main_body_text_trafilatura(the_url):
    start_time = time.time()
    try:
        downloaded = trafilatura.fetch_url(the_url)
        text = trafilatura.extract(downloaded)
        end_time = time.time()
        elapsed_time = end_time - start_time

        if text:
            return text, elapsed_time
        else:
            return "Main body text could not be extracted.", elapsed_time
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        return str(e), elapsed_time

def fetch_with_scrapy(the_url):
    start_time = time.time()
    try:
        response = requests.get(the_url)
        selector = Selector(text=response.text)
        text_nodes = selector.xpath('//body//text()').extract()  # Using just the XPath selector here
        text = ' '.join([t.strip() for t in text_nodes if t.strip() != ''])  # Cleaning the text
        end_time = time.time()
        elapsed_time = end_time - start_time
        return text, elapsed_time
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        return str(e), elapsed_time


def fetch_dynamic_content(site_url: str, wait_for_load_in_sec: float = 2) -> str:

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(site_url)
    time.sleep(wait_for_load_in_sec)
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    site_text = ''.join(element for element in soup.stripped_strings)

    driver.quit()

    return site_text

# List of URLs for testing
urls = [
    "https://agresearch.montana.edu/wtarc/producerinfo/entomology-insect-ecology/EasternHeathSnail/GermanFactSheet.pdf",
    "https://en.wikipedia.org/wiki/Snail",
    "https://www.youtube.com/",
    "https://www.youtube.com/watch?v=jQuEKLiEANs",
    "https://github.com/Significant-Gravitas/Auto-GPT"
]


def get_url_text(site_url: str, mode: str, wait_for_load_in_sec: float = 2) -> (str, float):
    start_time = time.time()

    if mode == 'dynamic':
        site_text = fetch_dynamic_content(site_url, wait_for_load_in_sec)

    elif mode == 'static-bs4':
        site_text, _ = get_website_text_bs4(site_url)

    elif mode == 'static-trafilatura':
        site_text, _ = fetch_main_body_text_trafilatura(site_url)

    elif mode == 'static-scrapy':
        site_text, _ = fetch_with_scrapy(site_url)

    else:
        return "Invalid mode specified", 0.0

    end_time = time.time()
    elapsed_time = end_time - start_time

    return site_text, elapsed_time


# Fetch and compare
for url in urls:
    logging.info(f"\nFetching from URL: {url}\n")

    # Dynamic scraping
    dynamic_text, dynamic_time = get_url_text(url, 'dynamic')
    logging.info(f"Elapsed Time with Dynamic mode: {dynamic_time} seconds")
    logging.info(f"Extracted Text with Dynamic mode:\n{dynamic_text}")

    # Static scraping with BeautifulSoup
    static_bs4_text, bs4_time = get_url_text(url, 'static-bs4')
    logging.info(f"\nElapsed Time with Static BS4 mode: {bs4_time} seconds")
    logging.info(f"Extracted Text with Static BS4 mode:\n{static_bs4_text}")

    # Static scraping with Trafilatura
    static_trafilatura_text, trafilatura_time = get_url_text(url, 'static-trafilatura')
    logging.info(f"\nElapsed Time with Static Trafilatura mode: {trafilatura_time} seconds")
    logging.info(f"Extracted Text with Static Trafilatura mode:\n{static_trafilatura_text}")

    # Static scraping with Scrapy
    static_scrapy_text, scrapy_time = get_url_text(url, 'static-scrapy')
    logging.info(f"\nElapsed Time with Static Scrapy mode: {scrapy_time} seconds")
    logging.info(f"Extracted Text with Static Scrapy mode:\n{static_scrapy_text}")

    logging.info('-' * 40)
