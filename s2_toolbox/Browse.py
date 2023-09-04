from s3_agent.Tool import Tool

# ---------------------------------------------------------

# Search engine idea
#
# from googlesearch import search
# import requests
# from bs4 import BeautifulSoup
#
# def fetch_title(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
#
#         # Fetch the title
#         title = soup.find('title').text if soup.find('title') else 'No title found'
#
#         return f"title: {title}"
#     else:
#         return "Could not fetch the title or description."
#
# # To search
# query = "OpenAI GPT-4"
#
# text_result = ''
# for result_link_str in search(query, num_results=5):
#     text_result += f'{result_link_str}\n'
#     text_result += f'{fetch_title(result_link_str)}\n'
#
# print(text_result)
#
# # url = "https://openai.com/blog/gpt-4-api-general-availability"
# # title_and_desc = fetch_title_and_description(url)
#
# # if title_and_desc:
# #     print(f"The title of the page is: {title_and_desc}")
# # else:
# #     print("Could not fetch the title.")
#
#
# # for result_link in search(query, num_results=10):
# #     print(result_link)
# #     print(fetch_title_and_description(result_link))
#
#
#



# Website scraping
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
# import time  # Import the time module
#
# # Initialize Selenium with headless mode
# chrome_options = Options()
# # Uncomment below line to run Chrome in headless mode
# # chrome_options.add_argument("--headless")
# driver = webdriver.Chrome(options=chrome_options)
#
# # Load the website
# driver.get("https://furtive-point-c71.notion.site/GPT-pyWriter-Lotus-7a44993ddb1b42edbba4d6275d7c9628")
#
# # Wait for the page to load
# time.sleep(10)  # Waits for 10 seconds
#
# # Get the page source
# page_source = driver.page_source
#
# # Parse the page source with BeautifulSoup
# soup = BeautifulSoup(page_source, 'html.parser')
#
# # Extract and print all visible text elements
# texts = [element for element in soup.stripped_strings]
# for text in texts:
#     print(text)
#
# # Close the Selenium browser
# driver.quit()
