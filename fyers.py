import urllib.parse as urlparse
import pandas as pd
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from fyers_api import fyersModel
from fyers_api import accessToken
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


app_id = "XP24BBRDLI-100"
app_secret = "IDQR179FY1"
redirect_url = 'https://trade.fyers.in/api-login/redirect-uri/index.html'
user_id = "XT01730"
password = "Amazon@123"
pancard = "AGRPK7630H"


# noinspection PyTypeChecker
def get_token():
    session = accessToken.SessionModel(secret_key=app_secret,
                                       client_id=app_id,
                                       redirect_uri=redirect_url,
                                       response_type="code",
                                       grant_type="authorization_code")
    url = session.generate_authcode()
    options = Options()
    # options.add_argument('headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome()
    driver.get(url)
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//div[@class="container login-main-start"]')))
    driver.find_element_by_xpath("//input[@id='fyers_id']").send_keys(user_id)
    driver.find_element_by_xpath("//input[@id='password']").send_keys(password)
    driver.find_element_by_xpath("//input[@id='pancard']").send_keys(pancard)
    driver.find_element_by_class_name('login-submit-button').click()
    sleep(2)
    current_url = driver.current_url
    driver.close()
    parsed = urlparse.urlparse(current_url)
    auth_code = urlparse.parse_qs(parsed.query)['auth_code'][0]
    session.set_token(auth_code)
    response = session.generate_token()
    return response['access_token']


access_token = get_token()
fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)

positions = fyers.positions()
positions_data = positions['netPositions']
length = len(positions_data)
x = 1
symbol = []
netQty = []
avgPrice = []
realized_profit = []

while 0 <= x <= length - 1:
    data = positions_data[x]
    if data['netQty'] != 0:
        # final_data = data['id'], data['netQty'], data['avgPrice'], data['realized_profit']
        symbol.append(data['id'])
        netQty.append(data['netQty'])
        avgPrice.append(data['avgPrice'])
        realized_profit.append(data['realized_profit'])
    x = x + 1
final_data = {'symbol': symbol,
              'netQty': netQty,
              'avgPrice': avgPrice,
              'realized_profit': realized_profit,
              }

df = pd.DataFrame(final_data)
print(df)
