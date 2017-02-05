# auther = 'chenjunqi'
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

 #读取user_pay_count
def ReadUserPayCountCSV():
    user_pay_count_df = pd.read_csv("./data/dataset/dataset/user_pay_count.txt", sep='\t', encoding='UTF-8', parse_dates=True, index_col=0)
    user_pay_count_df.columns = user_pay_count_df.columns.map(lambda str_date:datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S"))
    return user_pay_count_df;

#读取开店时间数据
def ReadShopOpenDateCSV():
    shop_open_date = pd.read_csv("./data/dataset/dataset/shop_open_date.txt", sep='\t', index_col=0,encoding='UTF-8',parse_dates=[1])
    return shop_open_date;

###读取商家信息
def ReadShopInfoCSV():
    shop_infos = pd.read_csv("./data/dataset/dataset/shop_info.txt",
                         encoding='UTF-8',header=None,
                        names=['id','city','loc','per_pay','score',
                               'comment_cnt','shop_level','cate_1_name','cate_2_name','cate_3_name'], index_col=0, converters={'cate_3_name':np.str})
    return shop_infos;


##读取城市名称对照表
def ReadCityNameCSV():
    city_names = pd.read_csv("./data/dataset/dataset/city_name.txt", index_col=0, encoding='UTF-8',parse_dates=True)
    return city_names;

#读取休假表
def ReadCalendarCSV():
    calendar = pd.read_csv('./data/dataset/dataset/calendar.txt', sep='\t', encoding='UTF-8', index_col=0, parse_dates=True)
    calendar.index = calendar.index.format()
    return calendar;

#读取天气信息
def ReadWeatherCSV(pinyin_name):
    weather_info = pd.read_csv("./data/dataset/dataset/" + pinyin_name, index_col=0, encoding='UTF-8',parse_dates=True)
    return weather_info;

#读取处理过的天气信息
def readWeatherData(city):
    weather_info = pd.read_csv("./data/dataset/dataset/weather/process_" + city['pinyin'],
                               index_col=0, encoding='UTF-8',parse_dates=True, dtype={'desc':object, 'wind_level':object})
    return weather_info

#读取浏览信息
def ReadUserViewCSV():
    user_view_count_df = pd.read_csv("./data/dataset/dataset/user_view_count.txt", sep='\t', encoding='UTF-8', parse_dates=True, index_col=0)
    user_view_count_df.columns = user_view_count_df.columns.map(lambda str_date:datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S"))
    return user_view_count_df

#读取Arima的预测数据
def ReadArimaPayCountCSV():
    arima_pay_count_df = pd.read_csv("./data/dataset/dataset/arima/result", encoding='UTF-8', index_col=0)
    return arima_pay_count_df;
###=======================================================================================================================================================
def getShopPayTimeSeries(user_pay_counts, shop_id, date_range):
     return user_pay_counts.ix[shop_id][date_range[0]:(date_range[1] + datetime.timedelta(hours=23))]

def getShopPayTimePeriods(user_pay_counts, shop_id, date_range, time_range):
    ts = getShopPayTimeSeries(user_pay_counts, shop_id, date_range)
    period_start = pd.date_range(start=date_range[0], end=date_range[1],freq='D')
    period_end = pd.date_range(start=date_range[0], end=date_range[1],freq='D')
    period_start = period_start + time_range[0];
    period_end = period_end + time_range[1];
    #range(len(period_start))
    #period_start[i]:period_end[i]

    periods = None
    for i in range(len(period_start)):
        if i == 0:
            periods = ts[period_start[i]:period_end[i]]
        else:
            print('%d a'%(i))
            periods = periods.append(ts[period_start[i]:period_end[i]])
            print(periods)
    return periods;

def getShopViewTimeSeries(user_view_count_df, shop_id, date_range):
     return user_view_count_df.ix[shop_id][date_range[0]:(date_range[1] + datetime.timedelta(hours=23))]

def countShopViewTimePeriods(shop_id, date_range, time_range):
    ts = getShopViewTimeSeries(shop_id, date_range)
    period_start = pd.date_range(start=date_range[0], end=date_range[1],freq='D')
    period_end = pd.date_range(start=date_range[0], end=date_range[1],freq='D')
    period_start = period_start + time_range[0];
    period_end = period_end + time_range[1];
    periods = pd.Series();
    for i in range(len(period_start)):
        count = ts[period_start[i]:period_end[i]].sum()
        periods[period_start[i]] = count;
        #print('%d %s %d a'%(i, period_start[i], count))
    return periods;

def countShopPayTimePeriods(user_pay_counts, shop_id, date_range, time_range):
    ts = getShopPayTimeSeries(user_pay_counts, shop_id, date_range)
    period_start = pd.date_range(start=date_range[0], end=date_range[1],freq='D')
    period_end = pd.date_range(start=date_range[0], end=date_range[1],freq='D')
    period_start = period_start + time_range[0];
    period_end = period_end + time_range[1];
    #range(len(period_start))
    #period_start[i]:period_end[i]
    periods = pd.Series();
    for i in range(len(period_start)):
        count = ts[period_start[i]:period_end[i]].sum()
        periods[period_start[i]] = count;
        #print('%d %s %d a'%(i, period_start[i], count))

    df = periods.to_frame()
    df = df.rename(columns = {0:'count'})

    return df;
###=======================================================================================================================================================

def testAverageCount(df, last):
    m = df.shape[0]
    if m == 0:
        return 0;
    elif m == 1:
        return df.loc[0]['count'];
    elif m < last:
        return df.loc[0:m]['count'].sum() / m;
    else:
        arg = df.iloc[-last:]['count'].sum() / last;
        return arg


def testStdCount(df, last):
    m = df.shape[0]
    if m < 2:
        return 0;
    elif m < last:
        return df.loc[0:m]['count'].std();
    else:
        return df.iloc[-last:]['count'].std();

def testExtremeCount(df, last):
    m = df.shape[0]
    if m == 0:
        return 0;
    elif m < last:
        return df.loc[0:m]['count'].max(), df.loc[0:m]['count'].min();
    else:
        return df.iloc[-last:]['count'].max(), df.loc[-last:]['count'].min();

def average_count(df, last):
    column_name = 'avg_count' + str(last);
    average_df = pd.DataFrame();
    average_df[column_name] = 0;
    data = []
    for i in range(df.shape[0]):
        if i == 0:
            data.append(df.loc[0:i]['count'].sum())
        elif i < last:
            data.append(df.loc[0:(i - 1)]['count'].sum() / i)
        else:
            data.append(df.loc[(i-last):(i - 1)]['count'].sum() / last)

    average_df[column_name] = data;
    return average_df;

def extreme_count(df, last):
    max_column_name = 'max_count' + str(last);
    min_column_name = 'min_count' + str(last);

    extreme_df = pd.DataFrame();
    extreme_df[max_column_name] = 0;
    extreme_df[min_column_name] = 0;

    max_data = []
    min_data = []

    for i in range(df.shape[0]):
        if i == 0:
            max_data.append(df.loc[0]['count']);
            min_data.append(df.loc[0]['count']);
        else:
            max_data.append(df.loc[(i-last):(i - 1)]['count'].max())
            min_data.append(df.loc[(i-last):(i - 1)]['count'].min())

    extreme_df[max_column_name] = max_data;
    extreme_df[min_column_name] = min_data;
    return extreme_df;

def std_count(df, last):
    column_name = 'std_count' + str(last);

    std_df = pd.DataFrame();
    std_df[column_name] = 0;

    data = []
    for i in range(df.shape[0]):
        if i < 2:
            data.append(0);
        else:
            data.append(df.loc[(i-last):(i - 1)]['count'].std())

    std_df[column_name] = data
    return std_df;
###=======================================================================================================================================================
def evaluation(y_test, y_pred):
    n = y_test.shape[0]
    return np.sum(np.abs(y_test - y_pred) / (y_test + y_pred)) / n

def evaluation_tm(y_test, train_mean):
    n = y_test.shape[0]
    return np.sum(np.abs(y_test - train_mean) / (y_test + train_mean)) / n

def getTestCount(user_pay_counts, id, start, end):
    df = countShopPayTimePeriods(user_pay_counts, id, date_range=[start, end],
                                 time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])
    return df['count'];
#清理userpaycount
def WipeInvalidUserPayCount(user_pay_count):
    nonzero_user_pay_count = user_pay_count[user_pay_count['count'] != 0];

    count_max = nonzero_user_pay_count['count'].quantile(0.95)
    count_min = nonzero_user_pay_count['count'].quantile(0.05)
    valid_df = nonzero_user_pay_count[(nonzero_user_pay_count['count'] <= count_max) & (nonzero_user_pay_count['count'] >= count_min)]

    return valid_df;
###=======================================================================================================================================================