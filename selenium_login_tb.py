import requests
from urllib import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as SE
import time
import random

import gap_detection_cv


# 输入账号密码并点击登录
def login(browser, username, password):
    # MARK:
    input_username = browser.find_element(By.ID, "fm-login-id")
    input_username.send_keys(username)
    input_password = browser.find_element(By.ID, "fm-login-password")
    input_password.send_keys(password)
    button_login = browser.find_element(By.CLASS_NAME, "fm-button.fm-submit.password-login")
    button_login.click()


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


# 获取滑动距离
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
        rand_y = random.randint(-5, 5)  # y轴随机抖动
        while (sum_y+rand_y >= 30):  # 控制y轴移动不超过滑块范围
            rand_y = random.randint(-5, 5)
        rand_x = random.randint(1, 5)  # x轴随机移动
        if (offset-sum_x < 5):
            rand_x = offset-sum_x
        action.move_by_offset(rand_x, rand_y).perform()
        sum_x = sum_x+rand_x
        sum_y = sum_y+rand_y
        # print(rand_x, rand_y, sum_x, sum_y)
    action.release().perform()  # 松开


def selenium():
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 5)
    target_url = "https://login.taobao.com/"
    browser.get(url=target_url)

    username = "15211406057"
    password = "2528976435JWB"
    login(browser, username, password)  # 输入账号密码并点击登录
    captcha = False
    try:
        # print(browser.current_url)
        wait.until(EC.url_to_be('https://www.taobao.com/'))  # 判断是否直接跳转主页
        # print(browser.current_url)
    except SE.TimeoutException:
        # MARK:
        # msg_error = browser.find_element(By.CLASS_NAME, 'msg-error').text
        msg_error = browser.find_element(By.CLASS_NAME, 'login-error-msg').text
        if (msg_error != ''):
            print(msg_error)
        else:
            captcha = True

    time.sleep(1000)

    while (captcha):  # 没有跳转，需要验证
        # 等待验证码弹出
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'JDJRV-img-wrap')))
        offset = None
        while (offset == None):
            refresh_captcha(browser)  # 刷新验证码
            time.sleep(1)
            offset = get_offset(browser)  # 获取滑动距离
        slide_captcha(browser, offset)

        try:
            wait.until(EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'JDJRV-slide-bar-center'),'拼接成功'))
        except SE.TimeoutException:
            break

    cookies = browser.get_cookies()
    # print(cookies)
    browser.close()

    session = requests.session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    print(session)

    return session, cookies


if __name__ == '__main__':
    selenium()
