import requests
from urllib import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as SE
import time


class Selenium:
    login_url = ''
    index_url = ''
    search_url = ''
    cookies = list[dict]

    def __init__(self, login_url, index_url, search_url) -> None:
        self.login_url = login_url
        self.index_url = index_url
        self.search_url = search_url
        self.cookies = list[dict]

    def selenium_login(self):
        login_url = self.login_url
        browser = webdriver.Chrome()
        browser.get(url=login_url)
        time.sleep(30)
        cookies = browser.get_cookies()
        # print(cookies, type(cookies))
        # print(cookies[0], type(cookies[0]))
        # with open("cookies.txt", mode="w", encoding='utf-8', newline='') as f:
        #     f.write(str(cookies))

        browser.close()

        # 将 cookie 转换为 requests 库可用的格式
        # cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        # session = requests.Session()
        # for cookie in cookies:
        #     session.cookies.set(cookie['name'], cookie['value'])
        # print("session", type(session))
        # with open("session.txt", mode="w", encoding='utf-8', newline='') as f:
        #     f.write(str(session))

        # return cookies
        self.cookies = cookies

    def selenium_search(self, keywords):
        index_url = self.index_url
        search_url = self.search_url
        for keyword in keywords:
            search_url = search_url+keyword+'%20'  # 空格分割关键字

        browser = webdriver.Chrome()
        browser.get(index_url)
        for cookie in self.cookies:
            browser.add_cookie(cookie)
        browser.get(search_url)
        time.sleep(5)
        print(browser.page_source)
        with open("search_result.html", mode="w", encoding='utf-8', newline='') as f:
            f.write(browser.page_source)
        browser.close()


if __name__ == '__main__':
    selenium_jd = Selenium(login_url='https://passport.jd.com/new/login.aspx',
                           index_url='https://www.jd.com',
                           search_url='https://search.jd.com/Search?keyword=')
    selenium_jd.selenium_login()
    selenium_jd.selenium_search(['北通', '手柄'])
