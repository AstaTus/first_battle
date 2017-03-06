# auther = 'chenjunqi'
# -*- coding: utf-8 -*-
import base
import datetime
import pandas as pd
import numpy as np

def initWeekDate(start_time, week_num):
    time_ranges = []
    while(week_num > 0):
        end_time = start_time + datetime.timedelta(days=6)
        time_ranges.append([start_time, end_time])

        week_num = week_num - 1;
        start_time = start_time + datetime.timedelta(weeks=1)

    return time_ranges


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

def predictPayCountByTwoWeek(shop_id, day_type, time_ranges, shop_open_dates, user_pay_counts, calenders):

    real_week_means = []
    predict_one_week_means = []
    predict_two_week_means = []
    predict_mix_week_means = []

    for i, tr in enumerate(time_ranges):
        holiday_df = base.getHolidayPayCount(
            shop_id, day_type, shop_open_dates, user_pay_counts, calenders, tr[0], tr[1])

        #检测holiday_df是否有效

        real_week_means.append(np.mean(holiday_df['count']))
        if i >= 2:
            predict_one_week_means.append((real_week_means[i - 2] + real_week_means[i - 1]) / 2)

        if i >= 2:
            if (i % 2) == 0:
                predict_mix_week_means.append((real_week_means[i - 2] + real_week_means[i - 1]) / 2)
            else:
                predict_mix_week_means.append((real_week_means[i - 2] + predict_one_week_means[i - 1 - 2]) / 2)

        if i >= 2:
            if (i % 2) == 0:
                predict_two_week_means.append((real_week_means[i - 2] + real_week_means[i - 1]) / 2)
            else:
                predict_two_week_means.append((real_week_means[i - 3] + real_week_means[i - 2]) / 2)

    return predict_mix_week_means, predict_two_week_means


def combinePredict(pred_dict, calenders, by_week_num, time_ranges):

    valid_time_ranges = time_ranges[by_week_num:]
    y_Pred = []
    for i, vtr in enumerate(valid_time_ranges):
        for date in pd.date_range(start=vtr[0], end=vtr[1], freq='D', normalize=True):
            daytype = calenders.loc[date.strftime('%Y-%m-%d')]['daytype']
            y_Pred.append(pred_dict[daytype][i]);

    return y_Pred