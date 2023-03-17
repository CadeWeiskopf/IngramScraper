import json
import oauth2 as oauth
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sys
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
with open(os.path.join(SECRETS_PATH, 'token_key'), 'r') as token_key_file:
    token_key = token_key_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'token_secret'), 'r') as token_secret_file:
    token_secret = token_secret_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'consumer_key'), 'r') as consumer_key_file:
    consumer_key = consumer_key_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'consumer_secret'), 'r') as consumer_secret_file:
    consumer_secret = consumer_secret_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'restlet_url'), 'r') as restlet_url_file:
    restlet_url = restlet_url_file.read().strip()
with open(os.path.join(SECRETS_PATH, 'ns_realm'), 'r') as ns_realm_file:
    ns_realm = ns_realm_file.read().strip()

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
if not token_key:
    raise ValueError('Token Key is empty or None')
if not token_secret:
    raise ValueError('Token Secret is empty or None')
if not consumer_key:
    raise ValueError('Consumer Key is empty or None')
if not consumer_secret:
    raise ValueError('Consumer Secret is empty or None')
if not restlet_url:
    raise ValueError('RESTlet URL is empty or None')
if not ns_realm:
    raise ValueError('NS Realm is empty or None')

print('got secrets')

# used to get existing lead ids in ns
def generate_get_request_url_and_headers(page_index):
    url = f'{restlet_url}&index={page_index}'
    token = oauth.Token(key=token_key, secret=token_secret)
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    params = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': token.key,
        'oauth_consumer_key': consumer.key
    }
    req = oauth.Request(method='GET', url=url, parameters=params)
    signatureMethod = oauth.SignatureMethod_HMAC_SHA256()
    req.sign_request(signatureMethod, consumer, token)
    header = req.to_header(ns_realm)
    headery = header['Authorization'].encode('ascii', 'ignore')
    headerx = {'Authorization': headery, 'Content-Type':'application/json'}
    return [url, headerx]

# used to post the new lead ids
def generate_post_request_url_and_headers():
    token = oauth.Token(key=token_key, secret=token_secret)
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    params = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': token.key,
        'oauth_consumer_key': consumer.key
    }
    req = oauth.Request(method='POST', url=restlet_url, parameters=params)
    signatureMethod = oauth.SignatureMethod_HMAC_SHA256()
    req.sign_request(signatureMethod, consumer, token)
    header = req.to_header(ns_realm)
    headery = header['Authorization'].encode('ascii', 'ignore')
    headerx = {'Authorization': headery, 'Content-Type':'application/json'}
    return [restlet_url, headerx]

#  get the Ingram PRM Lead IDs from a page of data
def extract_lead_id(data):
    page_lead_ids = []
    for row in data:
        page_lead_ids.append(row['values']['custrecord_ingram_leadid'])
    return page_lead_ids

# main loop
while True:
    print('Taking a nap...')
    time.sleep(300)
    
    # Get all current Lead IDs (used to check for new lead ids)
    # this section gets number of pages + data from the first page
    url, headerx = generate_get_request_url_and_headers(0)
    conn = requests.get(url, headers=headerx)
    conn_json = conn.json()
    num_of_pages = len(conn_json['pagedData']['pageRanges'])
    print(f'{num_of_pages} pages')
    lead_ids = []
    leads_extension = extract_lead_id(conn_json['data'])
    conn.close()
    lead_ids.extend(leads_extension)

    # then for [1, num_of_pages] repeat extracting data
    for i in range(1, num_of_pages):
        print(f'(total: {len(lead_ids)}) + iterate page {i}')
        url, headerx = generate_get_request_url_and_headers(i)
        conn = requests.get(url, headers=headerx)
        conn_json = conn.json()
        leads_extension = extract_lead_id(conn_json['data'])
        conn.close()
        lead_ids.extend(leads_extension)

    print(f'length of lead_ids at start={len(lead_ids)}')

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

    SECONDS_BEFORE_TIMEOUT = 600

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
    print(f'response {len(response.text)}')
    response_json = json.loads(response.text.replace('\ufffd', ''))
    response_json = sorted(response_json, key=lambda x: str(x['col2']), reverse=True)
    new_leads = []
    exclude_columns = ['col1', 'col3', 'col37', 'col38', 'col39', 'col40']
    for row in response_json:
        if len(new_leads) >= 200:
            # TODO: do this better
            # to prevent char limits for MapReduce param
            # ^ refers to NetSuite backend process going from RESTlet->MapReduce
            break
        if row['col2'] == None:
            continue
        if row['col2'] in lead_ids:
            continue
        new_lead = {}
        for col in row:
            if col in exclude_columns:
                continue
            new_lead[col] = str(row[col])
        print(f'new_lead: {new_lead}')
        new_leads.append(new_lead)
        
    if len(new_leads) <= 0:
        print ('no new leads')
        continue

    url, headerx = generate_post_request_url_and_headers()
    ns_payload = {'leads': new_leads}
    #print(f'ns_payload: {ns_payload}')
    conn = requests.post(url=url, headers=headerx, data=json.dumps(ns_payload).encode(encoding='utf-8'))
    print(conn.text)
    conn.close()

    driver.quit()

    end_time = time.time()
    print(f'complete time: {end_time - start_time}')