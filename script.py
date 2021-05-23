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
URL = "https://ca.finance.yahoo.com"
OPTIONS = Options()
# OPTIONS.add_argument("--headless")
DRIVER = webdriver.Chrome(options=OPTIONS)
DELAY = 1.5
# stock name, baseline percentage difference for notification
GME, GME_PCT = 'GME', 5
VTI, VTI_PCT = 'VTI', 2
ETH, ETH_PCT = 'ETH-USD', 5

def check_stocks():
    try:
        DRIVER.get(URL)
        check_stock(GME, GME_PCT)
        check_stock(VTI, VTI_PCT)
        check_stock(ETH, ETH_PCT)
        DRIVER.quit()
    except Exception as e:
        DRIVER.quit()
        print(e)
        send_message("An error has occurred.")

def check_stock(name, percentage):
    time.sleep(DELAY)
    search = DRIVER.find_element_by_xpath('//*[@id="yfin-usr-qry"]')
    search.send_keys(name)
    time.sleep(DELAY)
    search.send_keys(Keys.RETURN)
    time.sleep(DELAY)
    curr_price = float(DRIVER.find_element_by_xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div/span[1]').text.replace(",", ""))
    try:
        last_price = data[name][ list(data[name])[-1] ][0]
        pct_change = 100*(curr_price/last_price - 1) # actual percentage difference between current and last noted price
        if curr_price <= last_price * (100 - percentage)/100:
            data[name][str(datetime.now())] = [curr_price, pct_change]
            send_message(f"{name} has dropped by {pct_change:.2f}%")
            # CLIENT.messages.create(from_=config.PHONE_FROM, to=config.PHONE_TO, body=f"{name} has dropped by {pct_change:.2f}%")
        elif curr_price >= last_price * (100 + percentage)/100:
            data[name][str(datetime.now())] = [curr_price, pct_change]
            send_message(f"{name} has increased by {pct_change:.2f}%")
            # CLIENT.messages.create(from_=config.PHONE_FROM, to=config.PHONE_TO, body=f"{name} has increased by {pct_change:.2f}%")
    except KeyError:
        data[name] = {str(datetime.now()): [curr_price, 0]}

def send_message(message):
    CLIENT.messages.create(from_=config.PHONE_FROM, to=config.PHONE_TO, body=message)

def print_data():
    print(json.dumps(data, indent=4, sort_keys=True))

def main():
    global data
    data = {}
    try:
        with open(os.path.join(config.CUR_DIR, 'data.json'), 'r') as file:
            data = json.load(file)
    except (JSONDecodeError, FileNotFoundError):
        data = {}
    check_stocks()
    with open(os.path.join(config.CUR_DIR, 'data.json'), 'w') as file:
        json.dump(data, file)

if __name__ == "__main__":
    main()