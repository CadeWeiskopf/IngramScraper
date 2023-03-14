import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

start_time = time.time()

# Get Secrets
SECRETS_PATH = '/run/secrets/'

with open(os.path.join(SECRETS_PATH, 'url'), 'r') as url_file:
    url = url_file.read()
with open(os.path.join(SECRETS_PATH, 'email'), 'r') as email_file:
    email = email_file.read()
with open(os.path.join(SECRETS_PATH, 'password'), 'r') as password_file:
    password = password_file.read()

if not url:
    raise ValueError('URL is empty or None')
if not email:
    raise ValueError('Email is empty or None')
if not password:
    raise ValueError('Password is empty or None')

# Initialize Driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--verbose')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage') 

chrome_driver_service = Service('/usr/bin/chromedriver')

driver = webdriver.Chrome(service=chrome_driver_service, options=chrome_options)

# Go to url & scrape
driver.get(url)

SECONDS_BEFORE_TIMEOUT = 900

email_element = WebDriverWait(driver, SECONDS_BEFORE_TIMEOUT).until(EC.element_to_be_clickable((By.NAME, 'email')))
email_element.send_keys(email)

password_element = WebDriverWait(driver, SECONDS_BEFORE_TIMEOUT).until(EC.element_to_be_clickable((By.NAME, 'password')))
password_element.send_keys(password)

submit_button = WebDriverWait(driver, SECONDS_BEFORE_TIMEOUT).until(EC.element_to_be_clickable((By.ID, 'idInputSubmit')))
submit_button.click()

driver.quit()

end_time = time.time()
print(f'complete time {end_time - start_time}')