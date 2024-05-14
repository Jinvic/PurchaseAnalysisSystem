import os
import csv
import shutil
import pandas as pd


# 创建存放数据的文件夹
# def init():
#     if (os.path.exists('data')):
#         shutil.rmtree('data')
#     os.makedirs('data/row_data')
#     os.makedirs('data/processed_data')


# # 将网页爬取的原始数据以csv格式存放
# def save_row_data(price_list, goods_id):
#     path = './data/row_data/'
#     filename = str(goods_id)+'.csv'
#     with open(path+filename, 'w', encoding='utf-8', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['Date', 'Price'])
#         for row in price_list:
#             writer.writerow(row)


# 读取原始数据，并进行数据清洗
def data_process(price_list):
    # path = './data/row_data/'
    # filename = str(goods_id)+'.csv'
    # df = pd.read_csv(path+filename, delimiter=',')

    # print(price_list)
    # DEBUG:
    # if price_list==None:
    #     df=pd.read_csv('row.csv')
    # DEBUG:
    # df.to_csv('row.csv', index=False)
    
    df = pd.DataFrame(price_list, columns=['Date', 'Price'])
    # 原始数据没有年份，稍微处理一下
    from datetime import datetime
    year = datetime.now().year  # 获取当前年份
    pre = 13
    for i in range(df.shape[0]):
        mouth, _ = df.loc[i, 'Date'].split('-')
        if (int(mouth) > pre):
            year -= 1
        pre = int(mouth)
        df.loc[i, 'Date'] = pd.to_datetime(
            df.loc[i, 'Date']+'-'+str(year), format='%m-%d-%Y')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.date
    # print(df.head)

    # 去重
    df.drop_duplicates(inplace=True)
    print(df.head(15))

    # 用前一天的数据填补空缺日期
    df.sort_values('Date', inplace=True)  # 排序
    df.reset_index(drop=True, inplace=True)  # 重置索引
    # 创建一个连续日期的索引
    date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max())
    # 用date列当索引 | 用date_range重设索引 | 前向填充空数据 | 重设索引
    df = df.set_index('Date').reindex(
        date_range).fillna(method='ffill').reset_index()
    df = df.rename(columns={'index': 'Date'})  # 将新增的列名'index'改回'Date'
    # print(df.head)

    # 保存处理完成的数据
    # DEBUG
    # df.to_csv('pro.csv', index=False)
    print('data process clear.')
    return df


if __name__ == '__main__':
    data_process(None)
