import requests
from pyquery import PyQuery as pq
from selenium_class import Selenium
# import selenium_login
import data_process
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as SE
from selenium.webdriver.common.keys import Keys
import time

# index_url_jd = 'https://www.jd.com'
# session, _ = selenium_login.selenium()
# response = session.get(index_url_jd)
# print(response.status_code)
# print(response.url)
# with open("index_jd.html", mode="w", encoding='utf-8', newline='') as f:
#     f.write(response.text)


def get_goods_id_jd(keywords):
    login_url_jd = 'https://passport.jd.com/new/login.aspx'
    index_url_jd = 'https://www.jd.com'
    search_url_jd = 'https://search.jd.com/Search?keyword='

    selenium_jd = Selenium(login_url_jd, index_url_jd, search_url_jd)
    # selenium_jd.selenium_login()
    selenium_jd.selenium_search(keywords)
    # selenium_login.selenium_search(keywords)

    # 解析网页数据
    with open('search_result.html', 'r', encoding='utf-8') as f:
        html = f.read()
    doc = pq(html)
    goodslist = doc('#J_goodsList li')
    id_list = list()
    for goods in goodslist.items():
        id_list.append(goods.attr('data-sku'))
        # print(goods.attr('data-sku'))

    # for id in id_list:
    #     print(id)

    return id_list


def get_history_price_page(goods_id):
    goods_url = 'https://item.jd.com/'+goods_id+'.html'
    print(goods_id)
    print(goods_url)
    # target_url = 'https://www.gwdang.com/v2/trend/'+goods_id+'-'+platform_code+'.html'
    # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    # headers = {'User-Agent': user_agent}
    # response = requests.get(search_url, headers=headers)
    # print(response.status_code)

    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get('https://www.gwdang.com/v2/trend?from=search')
    # 绕过webdriver验证
    script = 'Object.defineProperty(navigator, "webdriver", { get: () => false, });'
    browser.execute_script(script=script)

    # 等待页面加载完成
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'url')))
    input = browser.find_element(By.CSS_SELECTOR, '#url')
    button = browser.find_element(By.CSS_SELECTOR, '#search-button')
    input.send_keys(goods_url)
    input.send_keys(Keys.ENTER)
    time.sleep(0.2)
    # 设定动作链
    action = webdriver.ActionChains(browser)
    # 跳过第一次
    action.send_keys(Keys.TAB).perform()
    time.sleep(0.2)
    action.send_keys(Keys.TAB).perform()
    time.sleep(0.2)
    # 循环一次
    while (button != browser.switch_to.active_element):
        action.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    action.send_keys(Keys.ENTER).perform()

    # 等待页面加载完成
    WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'promotion-item')))

    with open("price_result.html", mode="w", encoding='utf-8', newline='') as f:
        f.write(browser.page_source)


def get_history_price_data():
    with open('price_result.html', 'r', encoding='utf-8') as f:
        html = f.read()
    doc = pq(html)

    # doc = pq(browser.page_source)
    datalist = doc('.promotion-list .promotion-item')
    datalist = datalist.items()
    price_list = list()
    for data in datalist:
        d = list()
        d.append(data.find('.date').text())  # 日期
        d.append(data.find('.ymj span').text()[1:])  # 价格
        price_list.append(d)
        # print(d['date']+'\t'+d['price'])

    print(len(price_list))
    # with open(goods_id+'.txt', mode='w', encoding='utf-8', newline='') as f:
    #     for li in price_list:
    #         f.write(li['date']+'\t'+li['price']+'\n')

    return price_list


def get_history_price(goods_id):
    get_history_price_page(goods_id)
    price_list = get_history_price_data()
    data_process.save_row_data(price_list, goods_id)
    return price_list


# DEBUG:
# if __name__ == '__main__':
#     id_list = get_goods_id_jd(['北通', '手柄'])
#     for id in id_list:
#         print(id)
#         get_history_price(id)
    # get_history_price('https://item.jd.com/4979408.html')

# DEBUG:
if __name__ == '__main__':
    get_history_price(4979408)
