from flask import Flask, request, jsonify
import re
import sql_class
app = Flask(__name__)

# 测试用，实际使用需要更改主机与端口号
host = '172.17.148.62'
port = '8000'


@app.route('/')
def index():
    return 'Hello, World!'


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
