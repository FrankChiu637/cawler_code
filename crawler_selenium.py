#%%
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

def Crawler(search_key, pages=1):
    url = 'https://www.sanmin.com.tw/'
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    time.sleep(1)
    actions = ActionChains(driver)
    ad_btn = driver.find_element('css selector', '.bi-x')
    actions.click(ad_btn)
    actions.perform()
    time.sleep(1)
    search_bar = driver.find_element('css selector', '#qu')
    search_bar.send_keys(search_key)
    time.sleep(0.5)
    search_btn = driver.find_element(
        'css selector', '.btn-sanmin-r')
    actions.click(search_btn)
    actions.perform()
    time.sleep(5)

    symbols = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    file_path = f'./{search_key}_Books'

    if not os.path.exists(file_path):
        os.mkdir(file_path)

    for page in range(pages):
        print(f'第{page+1}頁:')
        names = driver.find_elements('css selector', '.Title h3')
        prices = driver.find_elements('css selector', '.Price')

        for idx, name in enumerate(names):
            name_text = name.text
            if idx <len(prices):
                price_text = prices[idx].text.strip()
                price_text= price_text if price_text else '-'
            else:
                price_text='-'

            for j in symbols:
                if j in name_text:
                    name_text = name_text.replace(j, '')

            with open(f'{file_path}/{name_text}.csv', 'w', encoding='utf-8-sig') as file:
                file.write(f'{name_text}\n')
                file.write(f'{price_text[:-1]}')

        print(f'第{page+1}頁爬取完成')

        if page < pages - 1:
            next_btn = driver.find_element('css selector', '.bi-chevron-right')
            actions.click(next_btn)
            actions.perform()
            time.sleep(2)
    driver.quit()

Crawler(input('plz enter your search:'), 2)
# %%
