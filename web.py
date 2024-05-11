from flask import Flask, request, jsonify, render_template
import re
import sql_class
import pandas as pd
import Spider
app = Flask(__name__)

# 测试用，实际使用需要更改主机与端口号
host = '172.17.151.119'
port = '8000'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


# TEST:
@app.route('/search', methods=['POST'])
def search():
    # 使用get方法获取'keywords'字段的值，并去除首尾空白
    keywords_input = request.form.get('keywords', '').strip()
    keywords_list = keywords_input.split()  # 使用split方法按空格分割字符串，得到关键词列表
    for keyword in keywords_list:
        print(keyword)
    # id_list=Spider.get_goods_id_jd(keywords_list)
    info_list = [
        {
            'image_url': 'https://img13.360buyimg.com/n7/jfs/t1/217829/35/40208/131284/662619bcF69949721/aeb0076a7ec2a215.jpg',
            'title': '北通阿修罗2无线游戏手柄xbox线性扳机震动PC电脑steam电视特斯拉即插即玩双人成行原神胡闹厨房NBA 黑',
            'price': '159.90',
            'goods_id': '4979408',
            'row_addr': 'https://item.jd.com/4979408.html'
        },
        {
            'image_url': 'https://img11.360buyimg.com/n7/jfs/t1/245828/39/6930/120005/66151861F073dc22d/3a43149cd4683822.jpg',
            'title': '北通斯巴达3多模无线游戏手柄xbox蓝牙体感NS霍尔线性扳机switch电脑PC手机电视车机steam小小梦魇原神',
            'price': '239.00',
            'goods_id': '100068057171',
            'row_addr': 'https://item.jd.com/100068057171.html'
        }
    ]
    return render_template('search_result.html', info=info_list)


# TEST:
@app.route('/pridict', methods=['POST'])
def pridict():
    selected_goods_id = request.form.get('rowSelection')  # 直接获取商品id
    if selected_goods_id:
        print(f"Selected goods id: {selected_goods_id}")
        # 读取CSV文件
        df = pd.read_csv('data/processed_data/4979408.csv')
        # 将日期列转换为字符串格式，便于在HTML中直接使用
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        # 准备数据为JSON格式，但这里直接传递DataFrame给模板更直观
        return render_template('pridict_result.html', data=df.to_dict(orient='records'))
    else:
        print("No row was selected.")
    # 根据需要返回响应
    # return redirect(url_for('show_table'))
    # return selected_goods_id

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
