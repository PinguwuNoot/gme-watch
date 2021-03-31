# import pathlib
import os
import json
from json.decoder import JSONDecodeError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import config
from twilio.rest import Client

# PATH = pathlib.Path('chromedriver.exe').absolute()
# DRIVER = webdriver.Chrome(PATH)
CLIENT = Client(config.ACCOUNT_SID, config.AUTH_TOKEN)
URL = "https://tradingview.com"
OPTIONS = Options()
OPTIONS.add_argument("--headless")
DRIVER = webdriver.Chrome(options=OPTIONS) # path of chromedriver already in current working directory
DELAY = 1
# stock name, baseline percentage difference for notification
GME, GME_PCT = 'GME', 5
VTI, VTI_PCT = 'VTI', 2
ETH, ETH_PCT = 'ETHUSD', 5

def check_stocks():
    DRIVER.get(URL)
    check_stock(GME, GME_PCT)
    check_stock(VTI, VTI_PCT)
    check_stock(ETH, ETH_PCT)
    DRIVER.quit()

def check_stock(name, percentage):
    search = DRIVER.find_element_by_name("query")
    search.send_keys(name)
    search.send_keys(Keys.RETURN)
    time.sleep(DELAY)
    curr_price = float(DRIVER.find_element_by_xpath('//*[@id="anchor-page-1"]/div/div[3]/div[1]/div/div/div/div[1]/div[1]').text)
    try:
        last_price = data[name][ list(data[name])[-1] ][0]
        pct_change = 100*(curr_price/last_price - 1) # actual percentage difference between current and last noted price
        if curr_price <= last_price * (100 - percentage)/100:
            data[name][str(datetime.now())] = [curr_price, pct_change]
            CLIENT.messages.create(from_=config.PHONE_FROM, to=config.PHONE_TO, body=f"{name} has dropped by {pct_change:.2f}%")
        elif curr_price >= last_price * (100 + percentage)/100:
            data[name][str(datetime.now())] = [curr_price, pct_change]
            CLIENT.messages.create(from_=config.PHONE_FROM, to=config.PHONE_TO, body=f"{name} has increased by {pct_change:.2f}%")
    except KeyError:
        data[name] = {str(datetime.now()): [curr_price, 0]}

def print_data():
    print(json.dumps(data, indent=4, sort_keys=True))

def main():
    global data
    data = {}
    with open(os.path.join(config.CUR_DIR, 'data.json'), 'r+') as file:
        try:
            data = json.load(file)
        except JSONDecodeError:
            data = {}
    check_stocks()
    with open(os.path.join(config.CUR_DIR, 'data.json'), 'w') as file:
        json.dump(data, file)

if __name__ == "__main__":
    main()