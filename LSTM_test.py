import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# 读取数据
df = pd.read_csv('data/processed_data/4979408.csv')
df['Date'] = pd.to_datetime(df['Date'])  # 确保为datetime类型
df.set_index('Date', inplace=True)

# 数据预处理：归一化
prices = df['Price'].values.reshape(-1, 1)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_prices = scaler.fit_transform(prices)

# 划分训练集和测试集,80%训练集，20%测试集
train_size = int(len(scaled_prices) * 0.8)
train_data, test_data = scaled_prices[:train_size], scaled_prices[train_size:]


# 创建时间序列数据
def create_dataset(data, look_back=10):
    X, Y = [], []
    for i in range(len(data)-look_back-1):
        X.append(data[i:(i+look_back), 0])
        Y.append(data[i + look_back, 0])
    return np.array(X), np.array(Y)


look_back = 10  # 用过去10天的价格预测未来一天
X_train, y_train = create_dataset(train_data, look_back)
X_test, y_test = create_dataset(test_data, look_back)

# 重塑输入以适应LSTM模型
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

# 2. 构建并训练LSTM模型
model = Sequential()
# model = keras.models.Sequential()

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
    batch_size=1,  # 调整批量大小
    # validation_data=(X_test, y_test),
    verbose=2,
    # shuffle=False
)

#预测未来价格
predicted_prices = model.predict(X_test)
# 反标准化预测结果
predicted_prices = scaler.inverse_transform(predicted_prices)

#可视化预测结果
import matplotlib.pyplot as plt
plt.plot(df.index[-len(y_test):], scaler.inverse_transform(y_test.reshape(-1, 1)), label='Actual Price')
plt.plot(df.index[-len(y_test):], predicted_prices, label='Predicted Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# # 使用模型对未来价格进行预测（假设要预测未来5天）
# future_days_to_predict = 5
# last_train_index = len(train_data) - look_back
# input_sequence = scaled_prices[last_train_index:last_train_index + look_back]
# print(input_sequence.shape)
# prediction_sequence = []

# for _ in range(future_days_to_predict):
#     prediction = model.predict(input_sequence[np.newaxis, :, :])[0, 0]
#     prediction_sequence.append(prediction)
#     input_sequence = np.concatenate((input_sequence[1:], [prediction]))

# # 反标准化未来预测结果
# future_predicted_prices = scaler.inverse_transform(
#     np.array(prediction_sequence).reshape(-1, 1))
