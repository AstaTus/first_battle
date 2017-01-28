# auther = 'chenjunqi'
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import datetime
import time
import matplotlib
from sklearn import ensemble
from sklearn import datasets
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error


myfont = matplotlib.font_manager.FontProperties(fname=r'C:/Windows/Fonts/msyh.ttf')
matplotlib.use('qt4agg')
#指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False

#读取user_pay_count
user_pay_count_df = pd.read_csv("./data/dataset/dataset/user_pay_count.txt", sep='\t', encoding='UTF-8', parse_dates=True, index_col=0)
user_pay_count_df.columns = user_pay_count_df.columns.map(lambda str_date:datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S"))
#读取开店时间数据
shop_open_date = pd.read_csv("./data/dataset/dataset/shop_open_date.txt", sep='\t', index_col=0, header=None, encoding='UTF-8',parse_dates=[1])

###读取商家信息
shop_infos = pd.read_csv("./data/dataset/dataset/shop_info.txt",
                         encoding='UTF-8',header=None,
                        names=['id','city','loc','per_pay','score',
                               'comment_cnt','shop_level','cate_1_name','cate_2_name','cate_3_name'], index_col=0, converters={'cate_3_name':np.str})

#dtype={'id':np.int,'city':np.str,'loc':np.int,'per_pay':np.int,'score':np.int,
#                               'comment_cnt':np.int,'shop_level':np.int,'cate_1_name':np.str,'cate_2_name':np.str,'cate_3_name':np.str}

##经查看，只有cate_1_name 是超市便利店的项 cate_3_name 为NULL score为NULL comment_cnt 为NULL 且shop_level <= 1
shop_infos['cate_3_name'] = shop_infos['cate_3_name'].astype(str)

##读取城市名称对照表
city_names = pd.read_csv("./data/dataset/dataset/city_name.txt", index_col=0, encoding='UTF-8',parse_dates=True)

#读取休假表
calendar = pd.read_csv('./data/dataset/dataset/calendar.txt', sep='\t', encoding='UTF-8', index_col=0, parse_dates=True)
calendar.index = calendar.index.format()

#读取天气信息
def readWeatherCsv(city):
    city_pinyin = city_names.loc[city]['pinyin']
    weather_info = pd.read_csv("./data/dataset/dataset/" + city_pinyin, index_col=0, encoding='UTF-8',parse_dates=True)
    return weather_info;

def getShopPayTimeSeries(shop_id, date_range):
     return user_pay_count_df.ix[shop_id][date_range[0]:(date_range[1] + datetime.timedelta(hours=23))]

def getShopPayTimePeriods(shop_id, date_range, time_range):
    ts = getShopPayTimeSeries(shop_id, date_range)
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

def countShopPayTimePeriods(shop_id, date_range, time_range):
    ts = getShopPayTimeSeries(shop_id, date_range)
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
    return periods;

def plotShopPayCounts(shop_id, date_range, time_range):
    counts = countShopPayTimePeriods(shop_id, date_range, time_range)

    f, (ax) = plt.subplots(1, 1, figsize=(10, 5))

    ax.plot(counts.index, counts.values)
    info = shop_infos.ix[shop_id]
    print(type(info.cate_3_name))
    plt.title(info.cate_1_name + ' ' + info.cate_2_name + ('' if info.cate_3_name is None else info.cate_3_name), fontproperties=myfont)
    mean_value = np.mean(counts)
    ax.axhline(y=mean_value, linewidth=1, color='r')
    holiday_counts = choiceCalendarDay(counts, 0)
    #calendar.ix[s.index.strftime('%Y-%m-%d')][1]
    #calendar_filter = calendar.ix[counts.index.strftime('%Y-%m-%d')][1] == 1]
    #print(holiday_counts)
    ax.scatter(holiday_counts.index, holiday_counts.values, c='r')
    #ax.plot(holiday_counts.index, holiday_counts.values, 'r')
    plt.show()

#筛选出休息日或者工作日
def choiceCalendarDay(df, t):
    df.index = df.index.strftime('%Y-%m-%d')
    temp = calendar[calendar[1] == t]
    intersection = list(set(df.index.values) & set(temp.index.values))
    result = df[intersection];
    #print(result)
    result = pd.DataFrame(result)
    result.set_index(pd.to_datetime(result.index))
    result=result.sort_index()
    return result

def plotShopPayDayInfos(shop_id, start, count):

    info = shop_infos.ix[shop_id]

    f, (ax) = plt.subplots(1, 1, figsize=(15, 5))
    plt.title(info.cate_1_name + ' ' + info.cate_2_name + ('' if info.cate_3_name is None else info.cate_3_name), fontproperties=myfont)

    for i in range(count):
        start_time = start
        end_time = start_time + datetime.timedelta(1)
        s = getShopPayTimeSeries(id, date_range=[start_time, end_time])
        ax.plot(s.index, s.values, label=('holiday' if calendar.loc[start_time.strftime('%Y-%m-%d')][1] == 0 else 'workday'))
        start = end_time

    ax.legend()
    plt.show()

# date（index） | holiday | rain | count | from_open_date_day_count
#时间维度：月份、节假日明细，周几、
#天气维度：气温、天气、风力
#历史维度：近（3,7,13,21）天均值、方差、最大值、最小值
#口碑维度：浏览量

id = 4
open_time = shop_open_date.loc[id][1];
print(open_time)
start_time = open_time;
end_time = pd.to_datetime('2016-10-16')
series = countShopPayTimePeriods(id, date_range=[start_time, end_time], time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])
df = series.to_frame()

df=df.rename(columns = {0:'count'})
df['holiday'] = calendar.loc[df.index.strftime('%Y-%m-%d')]['daytype'].values

#获取（1、3、7）天的（均值avg 、标准差std、最大值max、最小值min）

count_max = df['count'].quantile(0.95)
count_min = df['count'].quantile(0.05)

valid_df = df[(df['count'] <= count_max) & (df['count'] >= count_min)]
temp_df = valid_df.reset_index(drop=True)

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

#df['count'][0:3].sum() / 3
temp_df = pd.concat([average_count(temp_df, 1), temp_df], axis=1)
temp_df = pd.concat([average_count(temp_df, 3), temp_df], axis=1)
temp_df = pd.concat([average_count(temp_df, 7), temp_df], axis=1)
#average_count(temp_df, 3)
#average_count(temp_df, 7)

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

temp_df = pd.concat([extreme_count(temp_df, 3), temp_df], axis=1)

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

temp_df = pd.concat([std_count(temp_df, 3), temp_df], axis=1)
temp_df = pd.concat([std_count(temp_df, 7), temp_df], axis=1)
temp_df = pd.concat([std_count(temp_df, 11), temp_df], axis=1)

result_df = temp_df.set_index(valid_df.index)

offset = pd.to_datetime('2016-10-17')
X_train = result_df[:offset].drop('count',axis=1)
y_train = result_df[:offset]['count']
X_test = result_df[offset:].drop('count',axis=1)
y_test = result_df[offset:]['count']

def evaluation(y_test, y_pred):
    n = y_test.shape[0]
    return np.sum(np.abs(y_test - y_pred) / (y_test + y_pred)) / n

def getShopOpenDate(id):
    return shop_open_date.loc[id - 1][1];

def initTrainData(index):
    open_time = shop_open_date.loc[index][1];
    series = countShopPayTimePeriods(index + 1, date_range=[start_time, end_time], time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])
    df = series.to_frame()
    df=df.rename(columns = {0:'count'})
    df['holiday'] = calendar.loc[df.index.strftime('%Y-%m-%d')]['daytype'].values
    count_max = df['count'].quantile(0.95)
    count_min = df['count'].quantile(0.05)
    valid_df = df[(df['count'] <= count_max) & (df['count'] >= count_min)]
    temp_df = valid_df.reset_index(drop=True)

    temp_df = pd.concat([average_count(temp_df, 1), temp_df], axis=1)
    temp_df = pd.concat([average_count(temp_df, 3), temp_df], axis=1)
    temp_df = pd.concat([average_count(temp_df, 7), temp_df], axis=1)
    temp_df = pd.concat([extreme_count(temp_df, 3), temp_df], axis=1)
    temp_df = pd.concat([std_count(temp_df, 3), temp_df], axis=1)
    temp_df = pd.concat([std_count(temp_df, 7), temp_df], axis=1)
    temp_df = pd.concat([std_count(temp_df, 11), temp_df], axis=1)

    #result_df = temp_df.set_index(valid_df.index)

    return temp_df

def trainModel(X_train, y_train):
    params = {'n_estimators': 500, 'max_depth': 2, 'min_samples_split': 3,
          'learning_rate': 0.02, 'loss': 'ls'}
    clf = ensemble.GradientBoostingRegressor(**params)
    clf.fit(X_train, y_train)
    return clf;

def predictNextDay(X_test):
    return clf.predict(X_test)

def initNextDayData(date, train_df):

    avg_count1 = testAverageCount(train_df, 1)
    avg_count3 = testAverageCount(train_df, 3)
    avg_count7 = testAverageCount(train_df, 7)

    max_count, min_count = testExtremeCount(train_df, 3)

    std_count3 = testStdCount(train_df, 3)
    std_count7 = testStdCount(train_df, 7)
    std_count11 = testStdCount(train_df, 11)

    holiday = calendar.loc[date.strftime('%Y-%m-%d')]['daytype']
    return pd.Series([avg_count1, avg_count3, avg_count7, max_count, min_count, std_count3, std_count7, std_count11, holiday],
              index=['avg_count1','avg_count3','avg_count7','max_count3','min_count3','std_count3','std_count7','std_count11', 'holiday']);

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

evaluations = []
predict_date = pd.date_range(start='10/17/2016', end='10/18/2016', freq='D', normalize=True)
m = shop_open_date.shape[0];


temp = 0
for id in range(1, 2):
    train_df = initTrainData(id)
    for date in predict_date:
        X_train, y_train = train_df.drop('count',axis=1), train_df['count']
        clf = trainModel(X_train, y_train)
        series = initNextDayData(date, train_df)
        next_dataframe = series.to_frame().T
        next_dataframe['holiday'] = next_dataframe['holiday'].astype(np.int32);
        print(next_dataframe)
        count = predictNextDay(next_dataframe)
        series['count'] = count;
        temp = series.to_frame()
        train_df = train_df.append(series, ignore_index = True)
        train_df['count'] = train_df['count'].astype(np.int32);
        train_df['holiday'] = train_df['holiday'].astype(np.int32);



