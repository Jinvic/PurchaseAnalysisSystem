# 备用，手动登录保存cookie
from selenium import webdriver
import json

# 启动第一个Chrome浏览器实例
driver1 = webdriver.Chrome()

# 导航至登录页面并完成登录
driver1.get("https://www.gwdang.com/user/login/")
# driver1.get("https://passport.jd.com/new/login.aspx")
# 填写用户名和密码，提交表单等操作...

# 登录成功后保存Cookie
cookies = driver1.get_cookies()
# 将cookies转换为JSON字符串
cookies_json = json.dumps(cookies)

# 将JSON字符串写入文件
with open('cookies_gwd.txt', 'w') as file:
# with open('cookies_jd.txt', 'w') as file:
    file.write(cookies_json)


# 记得关闭第一个浏览器实例（可选）
# driver1.quit()

# 启动第二个Chrome浏览器实例
driver2 = webdriver.Chrome()

# 加载之前保存的Cookie
# 读取cookies文件
with open('cookies_gwd.txt', 'r') as file:
# with open('cookies_jd.txt', 'r') as file:
    cookies_json = file.read()
cookies = json.loads(cookies_json)
for cookie in cookies:
    driver2.execute_cdp_cmd("Network.setCookie", {
        'name': cookie['name'],
        'value': cookie['value'],
        'domain': cookie['domain'],
        'path': cookie['path'],
        'secure': cookie.get('secure', False),
        'httpOnly': cookie.get('httpOnly', False),
        'sameSite': cookie.get('sameSite', 'Lax'),
    })


# 确保路径与你想要保持登录状态的页面一致
driver2.refresh()
driver2.get("https://www.gwdang.com/v2/trend")
# driver2.get("https://www.jd.com")

# 此时，第二个浏览器应已自动登录