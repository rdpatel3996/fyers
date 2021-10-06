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

chrome_options = Options()
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
fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)

while True:

    @bot.message_handler(commands='pnl')
    def get_pnl(msg1):
        positions = fyers.positions()
        positions_data = positions['overall']['pl_total']
        print(positions_data)
        positions_data = str(positions_data)
        bot.reply_to(msg1, positions_data)


    def r1():
        return "abc"


    @bot.message_handler(func=r1)
    def r2(stocks):
        x = stocks.text
        x1 = x.replace("/", "")
        x2 = x1[:1]
        x3 = x1[:4]
        x4 = x1[1:]
        chat_id = stocks.chat.id
        if x2 == "p":
            data1 = {"symbols": "NSE:" + x1[1:] + "-EQ"}
            quote = fyers.quotes(data1)
            cmp = quote['d'][0]['v']['lp']
            ch = quote['d'][0]['v']['ch']
            chp = quote['d'][0]['v']['chp']
            bid = quote['d'][0]['v']['bid']
            ask = quote['d'][0]['v']['ask']
            open1 = quote['d'][0]['v']['open_price']
            previos_close = quote['d'][0]['v']['prev_close_price']
            low = quote['d'][0]['v']['low_price']
            high = quote['d'][0]['v']['high_price']
            volume = quote['d'][0]['v']['volume']
            bot.reply_to(stocks, "Cmp : " + str('{:n}'.format(cmp)) + "   " + "(" + str(
                '{:n}'.format(ch)) + ")" + "   " + "(" + str('{:n}'.format(chp)) + "%)""\nBid : " + str(
                '{:n}'.format(bid)) + "   Ask : " + str('{:n}'.format(ask)) + "\nHigh : " + str(
                '{:n}'.format(high)) + "   Low : " + str('{:n}'.format(low)) + "\nOpen : " + str(
                '{:n}'.format(open1)) + "   Previos Close : " + str('{:n}'.format(previos_close)) + "\nVolume : " + str(
                '{:n}'.format(volume)))
        else:
            bot.reply_to(stocks, "please enter symbol in valid format")

        if x3 == "o":
            name = x1[4:]
            list1 = name.splitlines()
            symbol = list1[0]
            user_qty = list1[1]
            qty = abs(int(list1[1]))
            if int(user_qty) < 0:
                side = -1
            else:
                side = 1
            side = side
            limitprice = float(list1[2])
            offlineorder = list1[3]

            data = dict(symbol="NSE:" + symbol + "-EQ", qty=qty, type=1, side=side, productType="CNC",
                        limitPrice=limitprice,
                        stopPrice=0, validity="DAY", disclosedQty=0, offlineOrder=offlineorder, stopLoss=0,
                        takeProfit=0)

            response = fyers.place_order(data)
            order_status = response['message']
            bot.reply_to(stocks, order_status)

        else:
            bot.reply_to(stocks, "please enter order form in valid format")

        if x4 == "c":
            url1 = "https://www.google.com/finance/quote/" + x1[1:] + ":NSE"
            url2 = "https://www.web2pdfconvert.com/to/img"
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                      chrome_options=chrome_options)
            driver.get(url2)
            WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//input[@class="js-url-input"]')))
            driver.find_element_by_xpath("//input[@class='js-url-input']").click()
            driver.find_element_by_xpath("//input[@class='js-url-input']").send_keys(url1)
            driver.find_element_by_xpath("//div[@class='convert-icon cursor-pointer js-convert-btn']").click()
            sleep(20)
            pic_url = driver.find_element_by_xpath(
                "//a[@class='btn btn-large btn-primary mt-2 pt-2 js-download-btn']").get_attribute("href")
            driver.close()

            bot.send_photo(photo=pic_url, chat_id=chat_id)

        else:
            bot.reply_to(stocks, "please enter symbol in valid format")


    bot.polling()
