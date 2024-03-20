import requests
from pyquery import PyQuery as pq
from selenium_class import Selenium

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

    # selenium_jd = Selenium(login_url_jd, index_url_jd, search_url_jd)
    # selenium_jd.selenium_login()
    # selenium_jd.selenium_search(keywords)

    # 解析网页数据
    with open('search_result.html', 'r', encoding='utf-8') as f:
        html = f.read()
    doc = pq(html)
    goodslist = doc('#J_goodsList li')
    id_list = list()
    for goods in goodslist.items():
        id_list.append(goods.attr('data-sku'))
        # print(goods.attr('data-sku'))

    for id in id_list:
        print(id)


if __name__ == '__main__':
    get_goods_id_jd(['北通', '手柄'])
