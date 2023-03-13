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

driver.quit()