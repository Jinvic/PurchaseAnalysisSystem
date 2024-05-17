from flask import Flask, request, session, flash, redirect, url_for, jsonify, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import re
import os
import json
import sql_class
from selenium_class import Selenium
import pandas as pd
from datetime import datetime
import Spider
from data_process import data_process
from LSTM import LSTM_predict
app = Flask(__name__)

# 测试用，实际使用需要更改主机与端口号
host = '172.17.151.119'
# host = '192.168.43.135'
port = '8000'


# 初始化数据库表
def initialize_database():
    sql_class.accounts_db_init()
    sql_class.users_db_init()
    sql_class.queries_db_init()
    sql_class.train_result_db_init()
    sql_class.predict_result_db_init()


# flask-login配置
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'Access denied.'
app.config['SECRET_KEY'] = os.urandom(16).hex()


# 用户模型
class User(UserMixin):
    db_path = 'users.db'

    def __init__(self, uid, username, password, email):
        self.uid = uid
        self.username = username
        self.password = password
        self.email = email

    @classmethod
    def get_by_id(cls, uid):
        db = sql_class.SQLiteTool(cls.db_path)
        query_sql = "SELECT * FROM users WHERE uid = " + str(uid)
        user_data = db.query_data(query_sql)
        db.close_connection()
        if user_data:
            return cls(*user_data[0])
        return None

    @classmethod
    def get_by_username(cls, username):
        db = sql_class.SQLiteTool(cls.db_path)
        query_sql = "SELECT * FROM users WHERE username = " + \
            f'\'{str(username)}\''
        user_data = db.query_data(query_sql)
        db.close_connection()
        if user_data:
            return cls(*user_data[0])
        return None

    @classmethod
    def get_by_email(cls, email):
        db = sql_class.SQLiteTool(cls.db_path)
        query_sql = "SELECT * FROM users WHERE email = " + \
            f'\'{str(email)}\''
        user_data = db.query_data(query_sql)
        db.close_connection()
        if user_data:
            return cls(*user_data[0])
        return None

    @classmethod
    def create_user(cls, username, password, email):
        db = sql_class.SQLiteTool(cls.db_path)
        query_sql = "SELECT MAX(uid) FROM users"
        max_uid = db.query_data(query_sql)[0][0]
        uid = max_uid+1
        insert_sql = "INSERT INTO users VALUES (?, ?, ?, ?)"
        db.insert_data(insert_sql, (uid, username, password, email))
        db.close_connection()
        return cls(uid, username, password, email)

    def get_id(self):
        return str(self.uid)


# 用户加载回调
@login_manager.user_loader
def load_user(uid):
    return User.get_by_id(uid)


# @login_manager.request_loader
# def request_loader(request):
#     pass


# 登录
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.get_by_username(username=username)

    if user and user.password == password:
        login_user(user)
        return redirect(url_for('index'))  # 登录成功后重定向
    else:
        session['error_msg'] = '用户名或密码错误'
        return redirect(url_for('error'))


# 注册
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        session['error_msg'] = '两次密码不匹配'
        return redirect(url_for('error'))

    user1 = User.get_by_username(username=username)
    user2 = User.get_by_email(email=email)

    if user1 or user2:
        session['error_msg'] = '用户名或邮箱已被使用'
        return redirect(url_for('error'))

    # 创建新用户
    new_user = User.create_user(username, password, email)
    # 注册完成直接登录
    login_user(new_user)
    return redirect(url_for('index'))


# 登出
@app.route('/logout')
@login_required  # 确保只有登录用户才能访问此视图
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/error')
def error():
    # 从session中取出并删除msg，防止重放
    msg = session.pop('error_msg', '未知错误')
    return render_template('error.html', msg=msg)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/register_page')
def register_page():
    return render_template('register.html')


@app.route('/history')
# @login_required
def history():
    if not current_user.is_authenticated:
        session['error_msg'] = '请先登录'
        return redirect(url_for('error'))
    # info_list = [
    #     {
    #         'uid': 1,
    #         'qid': 1,
    #         'goods_id': '4979408',
    #         'query_date': '2024-03-28',
    #         'predict_days': 30,
    #     },
    # ]
    uid = current_user.get_id()
    db = sql_class.SQLiteTool('queries.db')
    query_sql = f"SELECT * FROM queries WHERE uid = {uid}"
    res = db.query_data(query_sql)
    db.close_connection()
    info_list = []
    for row in res:
        data_dict = {
            "qid": row[0],
            "uid": row[1],
            "goods_id": row[2],
            "query_date": row[3],
            "predict_days": row[4]
        }
        info_list.append(data_dict)
    # 转换为JSON字符串
    # info_list = json.dumps(info_list, ensure_ascii=False, indent=4)
    return render_template('history.html', info_list=info_list)


@app.route('/predict_history', methods=['POST'])
# @login_required
def predict_history():
    if not current_user.is_authenticated:
        session['error_msg'] = '请先登录'
        return redirect(url_for('error'))

    qid = request.form['rowSelection']

    # 取出训练结果
    db = sql_class.SQLiteTool('train_result.db')
    query_sql = f"SELECT date, actual_price, predict_price FROM train_result WHERE qid = {qid}"
    # res = db.query_data(query_sql)
    df1 = pd.read_sql_query(query_sql, db.conn)
    db.close_connection()

    # 取出预测结果
    db = sql_class.SQLiteTool('predict_result.db')
    query_sql = f"SELECT date, predict_price FROM predict_result WHERE qid = {qid}"
    # res = db.query_data(query_sql)
    df2 = pd.read_sql_query(query_sql, db.conn)
    db.close_connection()

    return predict_result(df1, df2)


# 搜索功能 接收关键词返回搜索结果
@app.route('/search', methods=['POST'])
def search():
    # 使用get方法获取'keywords'字段的值，并去除首尾空白
    keywords_input = request.form.get('keywords', '').strip()
    keywords_list = keywords_input.split()  # 使用split方法按空格分割字符串，得到关键词列表
    info_list = Spider.get_goods_info_jd(keywords_list)
    # print(info_list)
    return render_template('search_result.html', info_list=info_list)


# TEST:
@app.route('/predict', methods=['POST'])
def predict():
    selected_goods_id = request.form['rowSelection']  # 获取商品id
    predict_days = request.form['Days']  # 获取预测天数
    print(f"goods id: {selected_goods_id}")
    print(f"predict days: {predict_days}")
    if current_user.is_authenticated:
        # TODO:存入queries数据库
        uid = current_user.get_id()
        db = sql_class.SQLiteTool('queries.db')
        query_sql = "SELECT MAX(qid) FROM queries"
        max_qid = db.query_data(query_sql)[0][0]
        qid = max_qid+1
        insert_sql = "INSERT INTO queries VALUES (?, ?, ?, ?, ?)"
        current_date = datetime.now().strftime('%Y-%m-%d')
        db.insert_data(
            insert_sql, (qid, uid, selected_goods_id, current_date, predict_days))
        db.close_connection()
    else:
        qid = None

    # if selected_goods_id:
    #     print(f"Selected goods id: {selected_goods_id}")
    #     print(f"predict days: {predict_days}")
    #     # 读取CSV文件
    #     df = pd.read_csv('data/processed_data/4979408.csv')
    #     # 将日期列转换为字符串格式，便于在HTML中直接使用
    #     df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    #     # 准备数据为JSON格式，但这里直接传递DataFrame给模板更直观
    #     return render_template('predict_result.html', data=df.to_dict(orient='records'))
    # else:
    #     print("No row was selected.")

    # 获取原始数据
    price_list = Spider.get_history_price(selected_goods_id)
    processed_data = data_process(price_list)  # 数据处理
    train_result, future_predictions = LSTM_predict(
        processed_data, int(predict_days), qid)  # LSTM进行时间序列预测

    return predict_result(train_result, future_predictions)


def predict_result(df1, df2):
    # 将日期列转换为字符串格式，便于在HTML中直接使用
    # df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    # 准备数据为JSON格式，但这里直接传递DataFrame给模板更直观
    return render_template('predict_result.html', data1=df1.to_dict(orient='records'), data2=df2.to_dict(orient='records'))


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
    # Selenium.refresh_cookies()
    initialize_database()
    app.run(port=port, host=host, debug=True)
