from keras.models import load_model
from keras.layers import Bidirectional
from tensorflow import keras
import datetime
import time
import discord
from datetime import date, timedelta, datetime
import seaborn as sns
import pandas as pd
import numpy as np
from keras.layers import Activation, Dense, Dropout, LSTM, GRU
from keras.models import Sequential
import requests
import json


def timestampToDate(timestamp, divide=True):
    if(divide):
        timestamp/=1000
    return datetime.fromtimestamp(timestamp)

def normalise_zero_base(df):
    return df/df.max()

def extract_window_data(df, window_len=20, zero_base=True):
    window_data = []
    for idx in range(len(df) - window_len):
        tmp = df[idx: (idx + window_len)].copy()
        if zero_base:
            tmp = normalise_zero_base(tmp)
        window_data.append(tmp.values)
    return np.array(window_data)

def load_data(length=21):
    response = requests.get(
        "https://api2.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&&limit="+str(length))
    return response.json()


def previousData():
    data=load_data(2)
    data[0][0] = timestampToDate(data[0][0])
    predictionData=load_data(22)
    predictionData=predictionData[:-1]
    [_,predictedClose,_] = predict_close(predictionData)
    predictedClose = predictedClose[0]
    data = data[0][0:5]
    for i in range(1,5):
        data[i]=float(data[i])
    data.append(predictedClose)
    profitsEarned=0
    if(predictedClose >= data[1]):
        profitsEarned=data[4]-data[1]
    else:
        profitsEarned=-data[4]+data[1]
    percentageProfit = (profitsEarned*100)/data[1]
    data.append(percentageProfit)
    return data


def predict_close(data):
    model = load_model('my_model.h5')

    #fetching previous 20 candle stick data
    past_data=data
    openTime = timestampToDate(data[-1][0])
    openPrice = float(data[-1][1])
    #filtering data which is nessasary
    input = []
    for i in past_data:
        temp = []
        for t in range(1, 6):
            temp.append(float(i[t]))
        input.append(temp)

    #predicting close price
    test = pd.DataFrame(input)
    X_test = extract_window_data(test)

    predictedClose = model.predict(X_test).squeeze()
    predictedClose = test[3].values[:-20] * (predictedClose + 1)
    return [openTime, predictedClose, openPrice]

def predictClose():
    data=load_data()
    return predict_close(data)


