# auther = 'chenjunqi'
# -*- coding: utf-8 -*-
import base
import datetime
import pandas as pd
import numpy as np
#HolidayMean
###=======================================================================================================================================================
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

def predictHolidayMeans(train_df, calenders, start_time, end_time):
    predict_date = pd.date_range(start=start_time, end=end_time, freq='D', normalize=True)
    pridicts = {}
    evaluations = {}
    for id in range(1, 2001):
        print(id)
        y_Pred = []
        for date in predict_date:
            daytype = calenders.loc[date.strftime('%Y-%m-%d')]['daytype']
            y_Pred.append(train_df.loc[id][daytype]);

        pridicts[id] = y_Pred

    predict_df = pd.DataFrame(pridicts)
    predict_df = predict_df.T
    return predict_df;


#ARIMA
###=======================================================================================================================================================
def initTrainSingleArimaData(id, shop_open_dates, user_pay_counts, start_time, end_time):
    open_time = shop_open_dates.loc[id]['date'];
    if open_time > start_time:
        start_time = open_time
    df = base.countShopPayTimePeriods(
        user_pay_counts, id, date_range=[start_time, end_time], time_range=[datetime.timedelta(hours=0), datetime.timedelta(hours=23)])

    return df

def initTrainArimasData(type, shop_open_dates, user_pay_counts, start_time, end_time):
    for id in range(1, 2001):
        print(id)
        arima_df = initTrainSingleArimaData(id, shop_open_dates, user_pay_counts, start_time, end_time)
        if type == 'predict':
            arima_df.to_csv("./data/dataset/dataset/predict/arima/" + str(id), index=False, encoding='UTF-8')
        else:
            arima_df.to_csv("./data/dataset/dataset/arima/" + str(id), index=False, encoding='UTF-8')

def predictArimas(type):
    predict_df = 0;
    if type == 'predict':
        predict_df = pd.read_csv("./data/dataset/dataset/predict/arima_prediction.txt", sep='\t', encoding='UTF-8', index_col=0)
    else:
        predict_df = pd.read_csv("./data/dataset/dataset/validation/arima_prediction.txt", sep='\t', encoding='UTF-8', index_col=0)
    predict_df = predict_df.astype(np.int)
    predict_df = predict_df.applymap(lambda x : 0 if x < 0 else x);

    return predict_df;

#读取evaluations
###=======================================================================================================================================================
def ReadEvaluationsCSV(type):
    path = "./data/dataset/dataset/validation/"
    if type == 'holiday_mean':
        path = path + 'holiday_mean_evaluation.txt'
    elif type == 'arima':
        path = path + 'arima_evaluation.txt'

    return  pd.read_csv(path, sep='\t', encoding='UTF-8', parse_dates=True, index_col=0)

def ReadHolidayMeanPredictCSV():
    return pd.read_csv( "./data/dataset/dataset/predict/holiday_mean_prediction.txt", sep='\t', header=None, encoding='UTF-8', index_col=0)

def FixFinalPredict(predict_df):
    predict_df = predict_df.astype(np.int)
    predict_df = predict_df.applymap(lambda x : 0 if x < 0 else x);
    predict_df.fillna(0);
    return predict_df;
