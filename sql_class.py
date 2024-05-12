import sqlite3


class SQLiteTool:
    def __init__(self, db_name):
        """
        初始化数据库连接
        :param db_name: 数据库文件名
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_sql):
        """
        创建表
        :param table_sql: 创建表的SQL语句
        :return: None
        """
        try:
            self.cursor.execute(table_sql)
            self.conn.commit()
            print("Table created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")

    def insert_data(self, insert_sql, data_tuple):
        """
        插入数据
        :param insert_sql: 插入数据的SQL语句模板
        :param data_tuple: 插入数据的元组
        :return: None
        """
        try:
            self.cursor.execute(insert_sql, data_tuple)
            self.conn.commit()
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Error inserting data: {e}")

    def query_data(self, query_sql):
        """
        查询数据
        :param query_sql: 查询数据的SQL语句
        :return: 查询结果
        """
        try:
            self.cursor.execute(query_sql)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error querying data: {e}")
            return None

    def update_data(self, update_sql, data_tuple):
        """
        更新数据
        :param update_sql: 更新数据的SQL语句模板
        :param data_tuple: 更新数据的元组
        :return: None
        """
        try:
            self.cursor.execute(update_sql, data_tuple)
            self.conn.commit()
            print("Data updated successfully.")
        except Exception as e:
            print(f"Error updating data: {e}")

    def delete_data(self, delete_sql, data_tuple=None):
        """
        删除数据
        :param delete_sql: 删除数据的SQL语句模板
        :param data_tuple: 可选的元组，用于填充SQL中的占位符
        :return: None
        """
        try:
            if data_tuple:
                self.cursor.execute(delete_sql, data_tuple)
            else:
                self.cursor.execute(delete_sql)
            self.conn.commit()
            print("Data deleted successfully.")
        except Exception as e:
            print(f"Error deleting data: {e}")

    def close_connection(self):
        """
        关闭数据库连接
        :return: None
        """
        if self.conn:
            self.conn.close()
            print("Connection closed.")


# 使用示例
def example():
    db = SQLiteTool("example.db")

    # 创建表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    );
    """
    db.create_table(create_table_sql)

    # 插入数据
    insert_sql = "INSERT INTO users (name, email) VALUES (?, ?)"
    db.insert_data(insert_sql, ("Alice", "alice@example.com"))

    # 查询数据
    query_sql = "SELECT * FROM users"
    users = db.query_data(query_sql)
    for user in users:
        print(user)

    # 更新数据
    update_sql = "UPDATE users SET email = ? WHERE name = ?"
    db.update_data(update_sql, ("alice_updated@example.com", "Alice"))

    # 再次查询，验证更新
    updated_users = db.query_data(query_sql)
    for user in updated_users:
        print(user)

    # 删除数据
    delete_sql = "DELETE FROM users WHERE name = ?"
    db.delete_data(delete_sql, ("Alice",))

    # 最后关闭连接
    db.close_connection()


# 账号池数据库初始化
def accounts_db_init():
    # 账号池
    account_list = [
        '18873273538',
        '15211406057'
    ]

    # 创建数据库
    db = SQLiteTool("accounts.db")
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS accounts (
        mobile_number TEXT PRIMARY KEY,
        verification_code TEXT NOT NULL,
        occupied BOOLEAN NOT NULL
    );
    '''
    db.cursor.execute("DROP TABLE IF EXISTS accounts")
    db.create_table(create_table_sql)

    # 存入账号
    insert_sql = "INSERT INTO accounts VALUES (?, ?, ?)"
    for account in account_list:
        db.insert_data(insert_sql, (account, '000000', False))

    # 关闭连接
    db.close_connection()

# 用户数据库初始化


def users_db_init():

    # 创建数据库
    db = SQLiteTool("users.db")
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS users (
        uid INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email NOT NULL UNIQUE
    );
    '''
    db.create_table(create_table_sql)

    insert_sql = "INSERT INTO users VALUES (?, ?, ?, ?)"
    db.insert_data(insert_sql, (0, 'admin', 'admin', 'admin'))

    # 关闭连接
    db.close_connection()


# DEBUG:
def test():
    # 更新数据
    # db=SQLiteTool('accounts.db')
    # update_sql = "UPDATE accounts SET verification_code = ? , occupied = ? WHERE mobile_number = ?"
    # db.update_data(
    #         update_sql, ('123456', True, '12345678910'))

    # 查询数据
    # db=SQLiteTool('accounts.db')
    # query_sql = "SELECT * FROM accounts WHERE occupied = True"
    # accounts = db.query_data(query_sql)
    # print(len(accounts))
    # for account in accounts:
    #     print(account)
    # mobile_number='12345678910'
    # query_sql = "SELECT * FROM accounts WHERE mobile_number = "
    # accounts = db.query_data(query_sql+mobile_number)
    # for account in accounts:
    #     print(account)

    # 查询数据
    # db = SQLiteTool("users.db")
    # username = 'admin'
    # query_sql = "SELECT * FROM users WHERE username = " + \
    #     f'\'{str(username)}\''
    # user_data = db.query_data(query_sql)
    # print(query_sql)
    # print(user_data)
    pass


if __name__ == '__main__':
    accounts_db_init()
    users_db_init()
    # test()
