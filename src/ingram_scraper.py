import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--verbose')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')


chrome_driver_path = '/usr/bin/chromedriver'
chrome_driver_service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=chrome_driver_service, options=chrome_options)

# scrape
print('do scrape')
print('secrets'+str(os.listdir('/run/secrets/')))
SECRETS_PATH = '/run/secrets/'
# iterate over files in the directory
for file_name in os.listdir(SECRETS_PATH):
    if os.path.isfile(os.path.join(SECRETS_PATH, file_name)):
        with open(os.path.join(SECRETS_PATH, file_name), 'r') as f:
            file_contents = f.read()
            print(f"newFilr: {file_name}\nnewContents:\n{file_contents}\n")

driver.quit()