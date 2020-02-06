"""
Patient prediction model
"""
import datetime
import pandas as pd
import numpy as np

# Data Processing


def clean_disconti(array, time):
    clean_arr = np.empty((len(array)))
    for i in range(len(array)):
        if (i > 2) & (i < len(array)-2):
            if min(abs(array[i]-array[i+1])/(time[i+1]-time[i]).total_seconds(), abs(array[i]-array[i-1])/(time[i]-time[i-1]).total_seconds()) > 0.3:
                clean_arr[i] = (array[i-1]+array[i+1])/2
            else:
                clean_arr[i] = array[i]
        else:
            clean_arr[i] = array[i]
    return clean_arr


# function clean_disconti( tempeaature, time)
# temperature : ndarray
# time : ndarray
# output : 修掉不正常的點


def mv_avg(data, window_size):
    output_arr = []

    for data_idx in range(0, len(data)):
        if data_idx < window_size-1:
            output_arr.append(np.mean(data[:data_idx+1]))
        elif data_idx == len(data):
            break
        else:
            output_arr.append(np.mean(data[data_idx+1-window_size:data_idx+1]))

    return np.array(output_arr)


# function mv_avg ( temperature, window_size)
# temperature : ndarray
# window_size :　int
# output : 移動平均，光滑的訊號


def find_conti(data, time):
    start = 0
    while data[len(data)-start-1]-data[len(data)-start-2] > 0:
        start += 1
    return time[-start-1], data[len(data)-1]-data[len(data)-start-1]


# function find_conti(temperature)
# temperature : ndarray
# return 開始上升的時間點(距離現在前幾秒) , 在這個區間裡面上升幾度


def data_extraction(raw_data):
    data = pd.DataFrame(raw_data)

    data.columns = ["ID", "date", "time", 'hr', 'temp', 'activity']
    data['time'] = data['date']+' '+data['time']
    data = data.drop(['date'], axis=1)


    data_time = np.array([datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in data['time'].values])

    data_temp = np.array((data['temp'].values)/100)

    modify_temp_watch = clean_disconti(np.copy(data_temp), np.copy(data_time))

    removable_disconti = [i for i, x in enumerate(((modify_temp_watch-data_temp) != 0).astype(int)) if x != 0]

    return data_time, modify_temp_watch, removable_disconti


# function data_extraction(path)
# returns
# data_time : ndarray (時間tag, 陣列)
# modify_temp_watch : ndarray (體溫)
# removable_disconti : ndarray (有問題點的index)


def main(path, cri_temperature, cri_increasing_time, window_size=None):
    data_time, data_temperature, _ = data_extraction(path)

    if window_size is None:
        smooth_data = mv_avg(data_temperature, 4)
    else:
        smooth_data = mv_avg(data_temperature, window_size)

    increasing_ti, _ = find_conti(smooth_data[:-2], data_time)

    rule_1 = (smooth_data[-1] > cri_temperature)& (data_time[-1] - increasing_ti > datetime.timedelta(seconds=cri_increasing_time))
    rule_2 = np.sum(data[(time[-1]-time) <= datetime.timedelta(seconds=60*60)] >= cri_temperature_upper) > 0.7*np.sum(data[(time[-1]-time) <= datetime.timedelta(seconds=60*60)])
    
    time_rule = (time[-1].time() >= datetime.time(hour = 9))&(time[-1].time() <= datetime.time(hour = 18))
    if (time_rule == True)& ((rule_1 == True)|(rule_2 == True)):
    return 0

# function main(data_path, cri_temperature, cri_increasing_time, window_size)
# data_path : format = csv
# rule_1 : 高於多少溫度且升高多少時間
    # cri_temperature : 高於多少溫度
    # cri_increasing_time : 升高多少時間(seconds)
# rule_2 : 在前一個小時內的資料裡，有70%的時候，體溫是大於cri_temperature_upper
    # cri_temperature_upper
#time_rule : 定義時間範圍
# window_size : optional default = 4 移動平均採樣點數
# return : int
# 1:警示
# 0:沒事
