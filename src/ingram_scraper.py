import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

start_time = time.time()
print(f'start {start_time}')

# Get Secrets
SECRETS_PATH = '/run/secrets/'

with open(os.path.join(SECRETS_PATH, 'origin'), 'r') as origin_file:
    origin = origin_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'login_url'), 'r') as login_url_file:
    login_url = login_url_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'post_url'), 'r') as post_url_file:
    post_url = post_url_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'email'), 'r') as email_file:
    email = email_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'password'), 'r') as password_file:
    password = password_file.read().strip()

if not origin:
    raise ValueError('Origin is empty or None')
if not login_url:
    raise ValueError('Login URL is empty or None')
if not post_url:
    raise ValueError('POST URL is empty or None')
if not email:
    raise ValueError('Email is empty or None')
if not password:
    raise ValueError('Password is empty or None')

print('got secrets')

# Initialize Driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--verbose')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage') 
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0')

chrome_driver_service = Service('/usr/bin/chromedriver')

driver = webdriver.Chrome(service=chrome_driver_service, options=chrome_options)

print('driver opened')

# Go to url & generate cookies
driver.get(login_url)

print('driver got url , waiting for elements')

SECONDS_BEFORE_TIMEOUT = 60

email_element = WebDriverWait(driver, SECONDS_BEFORE_TIMEOUT).until(EC.element_to_be_clickable((By.NAME, 'email')))
email_element.send_keys(email)

password_element = WebDriverWait(driver, SECONDS_BEFORE_TIMEOUT).until(EC.element_to_be_clickable((By.NAME, 'password')))
password_element.send_keys(password)

print('signing in')
#submit_button = WebDriverWait(driver, SECONDS_BEFORE_TIMEOUT).until(EC.element_to_be_clickable((By.ID, 'idInputSubmit')))
#submit_button.click()
driver.execute_script("document.getElementById('idInputSubmit').click()")
print('clicked sign in')

leads_tab = WebDriverWait(driver, SECONDS_BEFORE_TIMEOUT).until(EC.presence_of_element_located((By.ID, "lead")))

print('loaded, getting cookies')

# build cookies
cookies = {}
for cookie in driver.get_cookies():
    cookies[cookie['name']] = str(cookie['value'])
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': origin,
    'Connection': 'keep-alive',
    'Referer': post_url,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}
params = {
    'getResultsJSON': '',
    'timestamp': [
        int(time.time()),
        int(time.time() + 300),
    ],
}
data = {
    'status': '-1',
    'saleRepId': '-1',
    'saleRep': '',
    'isPaid': 'false',
    'dateFrom': '',
    'dateTo': '',
    'source': '-1',
    'activationEst': '-1',
    'm2mEst': '-1',
    'companySize': '',
    'industry': '',
}

# Get data
print('posting')
response = requests.post(
    post_url,
    params=params,
    cookies=cookies,
    headers=headers,
    data=data,
)
print(f'response {response.text}')

driver.quit()

end_time = time.time()
print(f'complete time: {end_time - start_time}')