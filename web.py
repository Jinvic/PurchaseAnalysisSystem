from flask import Flask, request, jsonify, render_template
import re
import sql_class
import Spider
app = Flask(__name__)

# 测试用，实际使用需要更改主机与端口号
host = '172.17.148.62'
port = '8000'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


# TEST:
@app.route('/search', methods=['POST'])
def process_keywords():
    keywords_input = request.form.get('keywords', '').strip()  # 使用get方法获取'keywords'字段的值，并去除首尾空白
    keywords_list = keywords_input.split()  # 使用split方法按空格分割字符串，得到关键词列表
    for keyword in keywords_list:
        print(keyword)
    # id_list=Spider.get_goods_id_jd(keywords_list)
    info_list = [
        {
            'image_url': 'https://img13.360buyimg.com/n7/jfs/t1/217829/35/40208/131284/662619bcF69949721/aeb0076a7ec2a215.jpg',
            'title': '北通阿修罗2无线游戏手柄xbox线性扳机震动PC电脑steam电视特斯拉即插即玩双人成行原神胡闹厨房NBA 黑',
            'price': '159.90',
            'row_addr': 'https://item.jd.com/4979408.html'
        },
        {
            'image_url': 'https://img11.360buyimg.com/n7/jfs/t1/245828/39/6930/120005/66151861F073dc22d/3a43149cd4683822.jpg',
            'title': '北通斯巴达3多模无线游戏手柄xbox蓝牙体感NS霍尔线性扳机switch电脑PC手机电视车机steam小小梦魇原神',
            'price': '239.00',
            'row_addr': 'https://item.jd.com/100068057171.html'
        }
    ]
    # display_info(info_list)
    # 返回响应给前端，这里简单返回一个确认信息
    # return '完成'
    return render_template('display_data.html', info=info_list)


# def display_info(info_list):
#     return render_template('display_data.html', info=info_list)


# 获取SmsForwarder转发的验证码
@app.route('/receive_sms', methods=['POST'])
def receive_sms():
    # 获取并解析请求中的数据
    data = request.get_json()
    # print(data)
    message = data.get('msg')
    print(message)

    if message:
        # 处理短信内容,通过正则匹配6位数字验证码
        pattern = r"【京东】(\d{6})"
        match = re.search(pattern, message)
        verification_code = match.group(1)
        # 正则匹配接收信息的号码
        pattern = r"\+86(\d{11})"
        match = re.search(pattern, message)
        mobile_number = match.group(1)
        print(mobile_number, verification_code)

        db = sql_class.SQLiteTool('accounts.db')
        update_sql = "UPDATE accounts SET verification_code = ? WHERE mobile_number = ?"
        db.update_data(
            update_sql, (verification_code, mobile_number))

        return jsonify({"status": "success", "message": "SMS received"}), 200
    else:
        return jsonify({"status": "error", "message": "No message found in the request"}), 400


if __name__ == '__main__':
    sql_class.accounts_db_init()
    app.run(port=port, host=host, debug=True)
