import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sql_class
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


# 输入清洗后的数据，进行时间序列预测
def LSTM_predict(df, future_days, qid=None):
    # 读取数据
    # DEBUG:
    if df == None:
        df = pd.read_csv('pro.csv')
    df['Date'] = pd.to_datetime(df['Date'])  # 确保为datetime类型
    df.set_index('Date', inplace=True)

    # 数据预处理：归一化
    prices = df['Price'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)

    # 划分训练集和测试集,80%训练集，20%测试集
    train_size = int(len(scaled_prices) * 0.8)
    train_data, test_data = scaled_prices[:
                                          train_size], scaled_prices[train_size:]

    # 创建时间序列数据
    def create_dataset(data, look_back=10):
        X, Y = [], []
        for i in range(len(data)-look_back-1):
            X.append(data[i:(i+look_back), 0])
            Y.append(data[i + look_back, 0])
        return np.array(X), np.array(Y)

    look_back = 7  # 用过去若干天的价格预测未来一天
    X_train, y_train = create_dataset(train_data, look_back)
    X_test, y_test = create_dataset(test_data, look_back)

    # 重塑输入以适应LSTM模型
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    # 2. 构建并训练LSTM模型
    model = Sequential()

    # 添加LSTM层，设置隐藏单元数为50
    model.add(LSTM(units=50, return_sequences=True, input_shape=(1, look_back)))
    model.add(LSTM(units=50))
    # 添加全连接层以输出预测值
    model.add(Dense(1))

    # 编译模型，选择优化器（Adam），损失函数（均方误差MSE）
    model.compile(optimizer='adam', loss='mean_squared_error')

    # 训练模型
    model.fit(
        X_train,
        y_train,
        epochs=100,  # 调整训练轮数
        batch_size=32,  # 调整批量大小
        validation_data=(X_test, y_test),  # 指定验证数据集，监控过拟合，不参与更新。
        verbose=2,
        # shuffle=False
    )

    # 预测未来价格
    predict_price = model.predict(X_test)
    # 反标准化预测结果
    actual_price = scaler.inverse_transform(y_test.reshape(-1, 1))
    predict_price = scaler.inverse_transform(predict_price)
    predict_price=predict_price.astype(np.float64)

    # # 可视化预测结果
    # plt.plot(df.index[-len(y_test):],
    #          actual_price, label='Actual Price')
    # plt.plot(df.index[-len(y_test):],
    #          predicted_prices, label='Predicted Price')
    # plt.xlabel('Date')
    # plt.ylabel('Price')
    # plt.legend()
    # plt.show()

    # 保存训练结果
    data_to_insert = []  # 准备插入数据
    for i in range(len(y_test)):
        single_date_str = df.index[-len(y_test) + i].strftime('%Y-%m-%d')
        data_to_insert.append(
            (qid, single_date_str, actual_price[i][0], predict_price[i][0]))

    db = sql_class.SQLiteTool('train_result.db')
    insert_sql = '''INSERT INTO train_result (
        qid, 
        date, 
        actual_price, 
        predict_price) 
        VALUES (?, ?, ?, ?)'''
    db.insert_many_data(insert_sql, data_to_insert)
    db.close_connection()


    # 获取训练数据的最后look_back天作为预测新数据的基底
    last_known_data = train_data[-look_back:]
    future_input = last_known_data.reshape(1, 1, look_back)

    # 预测未来若干天的价格
    # future_days = 30
    # future_days=int(future_days)
    predicted_future_prices = []

    for _ in range(future_days):
        forecast = model.predict(future_input)[0]
        # 将预测值加入到输入序列中，以便预测下一天
        future_input = np.concatenate(
            (future_input[:, :, 1:], forecast.reshape(1, 1, 1)), axis=2)
        # 反标准化预测值
        predicted_future_price = scaler.inverse_transform(
            forecast.reshape(-1, 1))
        predicted_future_prices.append(predicted_future_price[0][0])

    # 将预测的价格转换为适合绘图的格式
    last_date = df.index[-1]
    predicted_future_dates = pd.date_range(df.index[-1] + pd.DateOffset(
        1), periods=future_days, end=last_date + pd.DateOffset(future_days))

    # 绘制的预测价格
    # plt.plot(predicted_future_dates, predicted_future_prices,
    #          label='Predicted Future Price', linestyle='--')

    # plt.title('Price Prediction')
    # plt.xlabel('Date')
    # plt.ylabel('Price')
    # plt.legend()
    # plt.tight_layout()  # 自动调整子图参数, 使之填充整个图像区域
    # plt.show()

    # 保存预测结果
    # 构造 (qid, 日期, 价格) 的元组列表
    # predicted_future_prices.astype(np.float64)
    prediction_tuples = [(qid, date.strftime('%Y-%m-%d'), price.astype(np.float64)) for date, price in zip(
        predicted_future_dates, predicted_future_prices)]
    # for tuple_item in prediction_tuples:
    #     print(tuple_item)
    db = sql_class.SQLiteTool('predict_result.db')
    insert_sql = '''INSERT INTO predict_result (
        qid, 
        date, 
        predict_price) 
        VALUES (?, ?, ?)'''
    db.insert_many_data(insert_sql, prediction_tuples)
    db.close_connection()

    # 将训练集实际价格保存到CSV
    # train_results = pd.DataFrame(
    #     {'Date': df.index[:train_size], 'Price': scaler.inverse_transform(prices[:train_size]).flatten()})
    # train_results.to_csv('train_results.csv', index=False)

    # # 将测试集实际与预测价格合并并保存到CSV
    # print(df.index[-len(y_test):].shape)
    # # print(y_test.shape)
    # # print(y_test.reshape(-1, 1).shape)
    # print(scaler.inverse_transform(y_test.reshape(-1, 1)).flatten().shape)
    # # print(predicted_prices.shape)
    # print(predicted_prices.flatten().shape)

    # test_results = pd.DataFrame({'Date': df.index[-len(y_test):], 'Actual_Price': scaler.inverse_transform(
    #     y_test.reshape(-1, 1)).flatten(), 'Predicted_Price': predicted_prices.flatten()})
    # test_results.to_csv('test_results.csv', index=False)

    # # 将未来预测价格保存到CSV
    # future_predictions = pd.DataFrame(
    #     {'Date': predicted_future_dates, 'Predicted_Future_Price': predicted_future_prices})
    # future_predictions.to_csv('future_predictions.csv', index=False)

    # 将未来预测价格转换为合适的dataframe格式
    future_predictions = pd.DataFrame(
        {'Date': predicted_future_dates, 'Predicted_Future_Price': predicted_future_prices})

    return future_predictions

    


if __name__ == '__main__':
    LSTM_predict(None, 30, None)
