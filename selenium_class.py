import requests
from urllib import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as SE
import time
import random
from sql_class import SQLiteTool
import gap_detection_cv


# 刷新验证码
def refresh_captcha(browser):
    bigimg_src = browser.find_element(
        By.CSS_SELECTOR, ".JDJRV-bigimg img").get_attribute("src")
    smallimg_src = browser.find_element(
        By.CSS_SELECTOR, ".JDJRV-smallimg img").get_attribute("src")

    button_refresh = browser.find_element(
        By.CLASS_NAME, 'JDJRV-img-refresh')
    button_refresh.click()

    wait = WebDriverWait(browser, 2)
    wait.until_not(EC.element_attribute_to_include(
        (By.CSS_SELECTOR, '.JDJRV-bigimg img'), bigimg_src))
    wait.until_not(EC.element_attribute_to_include(
        (By.CSS_SELECTOR, '.JDJRV-smallimg img'), smallimg_src))


# 获取滑动距离F
def get_offset(browser):
    # 获取滑块验证码的滑块和背景图
    bigimg_src = browser.find_element(
        By.CSS_SELECTOR, ".JDJRV-bigimg img").get_attribute("src")  # 背景图
    smallimg_src = browser.find_element(
        By.CSS_SELECTOR, ".JDJRV-smallimg img").get_attribute("src")  # 滑块图
    # 命名图片
    bigimg = 'bigimg.png'
    smallimg = 'smallimg.png'
    # 下载图片
    request.urlretrieve(url=bigimg_src, filename=bigimg)
    request.urlretrieve(url=smallimg_src, filename=smallimg)
    # 获取滑动距离
    offset = gap_detection_cv.gap_detection()
    print(offset)
    if (offset):
        offset -= 2  # 不知道为什么总是长一点点
    return offset


# 滑动验证码
def slide_captcha(browser, offset):
    button_slide = browser.find_element(
        By.CLASS_NAME, 'JDJRV-slide-btn')
    action = webdriver.ActionChains(browser)
    action.click_and_hold(button_slide).perform()  # 点击并按住
    # action.move_by_offset(offset, 0) # 滑动距离
    # 添加随机抖动
    sum_x = 0
    sum_y = 0
    while (sum_x < offset):
        rand_y = random.randint(-3, 3)  # y轴随机抖动
        while (sum_y+rand_y >= 30):  # 控制y轴移动不超过滑块范围
            rand_y = random.randint(-3, 3)
        rand_x = random.randint(1, 5)  # x轴随机移动
        if (offset-sum_x < 5):
            rand_x = offset-sum_x
        action.move_by_offset(rand_x, rand_y)
        sum_x = sum_x+rand_x
        sum_y = sum_y+rand_y
        # print(rand_x, rand_y, sum_x, sum_y)
    action.release().perform()  # 松开


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
        # time.sleep(30)

        # SQL：从账号池中找出一个可用账号
        db = SQLiteTool('accounts.db')
        query_sql = "SELECT * FROM accounts WHERE occupied = False"
        accounts = db.query_data(query_sql)
        if (len(accounts) == 0):
            print('忙碌中，请稍候再试')
            return False

        update_sql = "UPDATE accounts SET occupied = ? WHERE mobile_number = ?"
        db.update_data(update_sql, (True, accounts[0][0]))  # 标记该账号使用中

        div_sms_login = browser.find_element(By.ID, 'sms-login')
        div_sms_login.click()  # 切换到短信验证码登录
        input_mobile_number = browser.find_element(By.ID, 'mobile-number')
        input_mobile_number.send_keys(accounts[0][0])
        button_send_code = browser.find_element(By.ID, 'send-sms-code-btn')
        button_send_code.click()  # 发送验证码

        wait = WebDriverWait(browser, 2)
        captcha = True
        try:  # 判断是否弹出验证码
            wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'JDJRV-slide')))
        except SE.TimeoutException:
            captcha = False

        while (captcha):  # 弹出验证码，需要验证
            # # 等待验证码弹出
            # wait.until(EC.presence_of_element_located(
            #     (By.CLASS_NAME, 'JDJRV-img-wrap')))
            offset = None
            while (offset == None):
                refresh_captcha(browser)  # 刷新验证码
                time.sleep(0.5)
                offset = get_offset(browser)  # 获取滑动距离
            slide_captcha(browser, offset)

            try:
                wait.until(EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, '.sms-box-error-msg.success-msg'), '验证码已发送'))
                captcha = False
                break
            except SE.TimeoutException:
                continue

        # 每0.5秒检查一次是否收到验证码，等待5秒
        cnt = 10
        verification_code = ''
        while (cnt):
            query_sql = "SELECT * FROM accounts WHERE mobile_number = " + \
                accounts[0][0]
            verification_code = db.query_data(query_sql)[0][1]
            if (verification_code != accounts[0][1]):
                break
            time.sleep(0.5)
            cnt -= 1
        update_sql = "UPDATE accounts SET occupied = ? WHERE mobile_number = ?"
        db.update_data(update_sql, (False, accounts[0][0]))  # 标记该账号空闲
        db.close_connection()
        if (verification_code == accounts[0][1]):
            print('请求验证码超时')
            return False

        input_sms_code = browser.find_element(By.ID, 'sms-code')
        input_sms_code.send_keys(verification_code)  # 输入验证码
        button_login = browser.find_element(By.ID, "sms-login-submit")
        button_login.click()  # 等待登录

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
