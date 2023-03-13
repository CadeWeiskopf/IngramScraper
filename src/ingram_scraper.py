import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

SECRETS_PATH = '/run/secrets/'
with open(os.path.join(SECRETS_PATH, 'url'), 'r') as url_file:
    url = url_file.read()
with open(os.path.join(SECRETS_PATH, 'email'), 'r') as email_file:
    email = email_file.read()
with open(os.path.join(SECRETS_PATH, 'password'), 'r') as password_file:
    password = password_file.read()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--verbose')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

chrome_driver_service = Service('/usr/bin/chromedriver')

driver = webdriver.Chrome(service=chrome_driver_service, options=chrome_options)

# scrape
print(f'do scrape {url} {email} {password}')

driver.quit()