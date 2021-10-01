import urllib.parse as urlparse
import os
import telebot
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

api_telegram = "2004963816:AAGbpzYvHS5TQCzrjovKsEo4YGklmng4P54"
bot = telebot.TeleBot(api_telegram)
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
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
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
fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="/Users/kenil/Desktop/apiV2")

positions = fyers.positions()
positions_data = positions['overall']['pl_total']
print(positions_data)

while True:
    @bot.message_handler(commands='p_pnl')
    def get_pnl(msg):
        positions = fyers.positions()
        positions_data = positions['overall']['pl_total']
        print(positions_data)
        positions_data = str(positions_data)
        bot.reply_to(msg, 'fyers papa pnl:' + positions_data)
        
    def stock_request(stocks):
        request = stocks
        return request

    @bot.message_handler(func=stock_request)
    def get_pnl(stocks):
        request = stocks.text
        request = request.replace("/", "")
        print(request)
        data = {"symbols": "NSE:" + request + "-EQ"}
        quote = fyers.quotes(data)
        x = int
        try:
            x = quote['d'][0]['v']['lp']
            bot.reply_to(stocks, x)
        except:
            bot.reply_to(stocks, "please enter valid symbol")


    bot.polling()
    time.sleep(20)
