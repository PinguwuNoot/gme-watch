# import pathlib
import json
from json.decoder import JSONDecodeError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


# PATH = pathlib.Path('chromedriver.exe').absolute()
# driver = webdriver.Chrome(PATH)
url = "https://tradingview.com"
driver = webdriver.Chrome() # path of chromedriver already in current working directory
driver.get(url)

search = driver.find_element_by_name("query")
search.send_keys("GME")
search.send_keys(Keys.RETURN)
time.sleep(1)

data = {}
price = float(driver.find_element_by_xpath('//*[@id="anchor-page-1"]/div/div[3]/div[1]/div/div/div/div[1]/div[1]/span').text)
with open('data.json') as file:
    try:
        stored_data = json.load(file)
        prices = stored_data.get('prices')
        last_price = prices[len(prices) - 1]
        if price <= last_price * 0.95 or price >= last_price * 1.05:
            prices.append(price)
            data['prices'] = prices
            with open('data.json', 'w') as file:
                json.dump(data, file)
    except JSONDecodeError:
        data['prices'] = [price]
        with open('data.json', 'w') as file:
            json.dump(data, file)
driver.quit()