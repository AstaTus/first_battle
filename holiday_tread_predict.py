# auther = 'chenjunqi'
# -*- coding: utf-8 -*-

import base
import datetime
import pandas as pd
import numpy as np

def trainSingleHolidayMeanData(id, shop_open_dates, user_pay_counts, calenders, start_time, end_time):
    open_time = shop_open_dates.loc[id]['date'];
    if open_time > start_time:
        start_time = open_time
    df = base.countShopPayTimePeriods(user_pay_counts, id,
                                      date_range=[start_time, end_time], time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])

    df['holiday'] = calenders.loc[df.index.strftime('%Y-%m-%d')]['daytype'].values

    mean_dict = {}
    for i in range(1, 6):
        if i != 4:
            temp_df = df[df['holiday'] == i];
            mean_dict[i] = [temp_df['count'].mean(), temp_df['count'].std()]

    #print(mean_dict)
    result_df = pd.DataFrame(mean_dict).T
    result_df.rename(columns={0: 'mean', 1: 'std'}, inplace=True)

    return result_df


def trainHolidayMeansData(shop_open_dates, user_pay_counts, calenders, start_time, end_time):
    holiday_mean_df = pd.DataFrame()
    for id in range(1,2001):
        print(id)
        df = trainSingleHolidayMeanData(id, shop_open_dates, user_pay_counts, calenders, start_time, end_time)
        holiday_mean_df[id] = df['mean'].T


    holiday_mean_df = holiday_mean_df.T
    holiday_mean_df.index.name = 'id'
    holiday_mean_df = holiday_mean_df.astype(np.int)

    return holiday_mean_df;