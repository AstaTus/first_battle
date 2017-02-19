# auther = 'chenjunqi'
# -*- coding: utf-8 -*-

import base
import datetime
import pandas as pd
import numpy as np



#COMMON
###=======================================================================================================================================================
def findPrevMatchDayTypeCount(id, start_time, daytype,shop_open_dates,user_pay_counts, calenders):

    open_time = shop_open_dates.loc[id]['date'];
    while True:
        end_time = start_time - datetime.timedelta(days=6)

        if open_time > end_time:
           end_time = open_time;

        if start_time <= end_time:
            return 0

        df = base.countShopPayTimePeriods(user_pay_counts, id,
                date_range=[end_time, start_time], time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])
        df['holiday'] = calenders.loc[df.index.strftime('%Y-%m-%d')]['daytype'].values
        temp_df = df[df['holiday'] == daytype];
        values = temp_df['count'].values;
        #print(values)
        for i in range(len(values)-1, -1, -1):
            if values[i] != 0:
                return values[i];

        start_time = start_time - datetime.timedelta(weeks=1)

def findNextMatchDayTypeCount(id, start_time, limit_time, daytype,shop_open_dates,user_pay_counts, calenders):

    open_time = shop_open_dates.loc[id]['date'];

    if open_time > start_time:
        start_time = open_time;

    while True:
        end_time = start_time + datetime.timedelta(days=6)

        if end_time > limit_time:
            end_time = limit_time;

        if start_time >= end_time:
            return 0;

        df = base.countShopPayTimePeriods(user_pay_counts, id,
                date_range=[start_time, end_time], time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])
        df['holiday'] = calenders.loc[df.index.strftime('%Y-%m-%d')]['daytype'].values
        temp_df = df[df['holiday'] == daytype];
        values = temp_df['count'].values;
        #print(values)
        for i in range(len(values)-1, -1, -1):
            if values[i] != 0:
                return values[i];

        start_time = start_time + datetime.timedelta(weeks=1)

def findNearestMatchDayTypeCount(id, start_time, limit_time, daytype,shop_open_dates,user_pay_counts, calenders):
    # count = findNextMatchDayTypeCount(id, start_time, limit_time, daytype,shop_open_dates,user_pay_counts, calenders);
    #
    # if count == 0:
    #     return findPrevMatchDayTypeCount(id, start_time, daytype,shop_open_dates,user_pay_counts, calenders)
    # else:
    #     return  count;
    return findPrevMatchDayTypeCount(id, start_time, daytype,shop_open_dates,user_pay_counts, calenders)

#ARIMA
###=======================================================================================================================================================
def initTrainSingleArimaData(id, shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time):
    open_time = shop_open_dates.loc[id]['date'];
    if open_time > start_time:
        start_time = open_time
    df = base.countShopPayTimePeriods(
        user_pay_counts, id, date_range=[start_time, end_time], time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])

    df['holiday'] = calenders.loc[df.index.strftime('%Y-%m-%d')]['daytype'].values

    #如果这一周有销售额为0的情况，则根据当前的daytype向前找，第一个有效且匹配的值填上
    # for time in df.index:
    #     if df.loc[time]['count'] == 0:
    #         df.ix[time]['count'] = findNearestMatchDayTypeCount(id, time, limit_time, df.loc[time]['holiday'], shop_open_dates,user_pay_counts, calenders)

    return df['count']

def initTrainArimasData(shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time):
    for id in range(1, 2001):
        print(id)
        arima_df = initTrainSingleArimaData(id, shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time)
        arima_df.to_csv("./data/dataset/dataset/shop_classify/arima/" + str(id), index=False, encoding='UTF-8')


def initPredictArimasData(shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time):
    for id in range(1, 2001):
        print(id)
        arima_df = initTrainSingleArimaData(id, shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time)
        arima_df.to_csv("./data/dataset/dataset/shop_classify/predict/arima/" + str(id), index=False, encoding='UTF-8')

def initCheckArimasData(shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time):
    for id in range(1, 2001):
        print(id)
        arima_df = initTrainSingleArimaData(id, shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time)
        arima_df.to_csv("./data/dataset/dataset/shop_classify/check/arima/" + str(id), index=False, encoding='UTF-8')

def initWeekDate(start_time, week_num):
    time_ranges = []
    while(week_num > 0):
        end_time = start_time + datetime.timedelta(days=6)
        time_ranges.append([start_time, end_time])

        week_num = week_num - 1;
        start_time = start_time + datetime.timedelta(weeks=1)

    return time_ranges

def calculateSingleHolidayMeanData(id, shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time):
    #open_time = shop_open_dates.loc[id]['date'];

    df = base.countShopPayTimePeriods(user_pay_counts, id,
                                      date_range=[start_time, end_time], time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])

    df['holiday'] = calenders.loc[df.index.strftime('%Y-%m-%d')]['daytype'].values

    #如果这一周有销售额为0的情况，则根据当前的daytype向前找，第一个有效且匹配的值填上
    for time in df.index:
        if df.loc[time]['count'] == 0:
            df.ix[time]['count'] = findNearestMatchDayTypeCount(id, time, limit_time, df.loc[time]['holiday'], shop_open_dates,user_pay_counts, calenders)

    means = {}
    for i in range(1, 6):
        if i != 4:
            temp_df = df[df['holiday'] == i];
            means[i] = temp_df['count'].mean()

    return means


def calculateHolidayMeansData(shop_open_dates, user_pay_counts, calenders, time_ranges):
    shop_mean_dict = {}
    for id in range(1,2001):
        print(id)
        mean_dict = {}
        for i, tr in enumerate(time_ranges):
            means = calculateSingleHolidayMeanData(id, shop_open_dates, user_pay_counts, calenders, tr[0], tr[1])
            mean_dict[i] = means

        shop_mean_dict[id] = mean_dict;

    return shop_mean_dict;

def calculatePeriodParams(shop_open_dates, user_pay_counts, calenders, start_time, end_time, limit_time):
    calculate_result = {}
    for shop_id in range(1, 2001):
        print(shop_id)
        df = base.countShopPayTimePeriods(user_pay_counts, shop_id,
                                              [start_time, end_time], [datetime.timedelta(hours=0), datetime.timedelta(hours=23)])

        df['holiday'] = calenders.loc[df.index.strftime('%Y-%m-%d')]['daytype'].values
        #如果这一周有销售额为0的情况，则根据当前的daytype向前找，第一个有效且匹配的值填上
        for time in df.index:
            if df.loc[time]['count'] == 0:
                df.ix[time]['count'] = findNearestMatchDayTypeCount(shop_id, time, limit_time, df.loc[time]['holiday'], shop_open_dates,user_pay_counts, calenders)

        calculate_result[shop_id] = [df['count'].mean(), df['count'].std(), df['count'].max(), df['count'].min()]


    result_df = pd.DataFrame(calculate_result);
    result_df = result_df.T;
    result_df = result_df.rename(columns={0:'mean', 1:'std', 2:'max', 3:'min'})
    return result_df

def getHolidayMeanCount(id, day_type, shop_mean_dict, start_real, end_real, pred_mean=None):
    count = 0;
    for i in range(start_real, end_real):
        count = count + shop_mean_dict[id][i][day_type]

    if pred_mean != None:
        count = count + pred_mean[id][day_type]

    if pred_mean != None:
        return count / (end_real - start_real  + 1);
    else:
        return count / (end_real - start_real)