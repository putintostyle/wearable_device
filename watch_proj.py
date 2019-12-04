#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
# import selenium 
import wget
import os
import sys
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
# from scipy.ndimage.filters import gaussian_filter1d
# from scipy.ndimage import gaussian_filter


# In[2]:


token_respon = requests.get("http://54.163.150.6:8002/shmain/model/token")
token_list = token_respon.json()


# In[3]:


token_list


# In[4]:


for i in token_list:
    if os.path.isdir(os.path.join('src/', i)) == False:
        os.mkdir(os.path.join('src/', i))
        wget.download("http://54.163.150.6:8002/shmain/model/data?token="+str(i), os.path.join('src/', i))
    else:
        wget.download("http://54.163.150.6:8002/shmain/model/data?token="+str(i), os.path.join('src/', i))



# # Data Processing


def clean_disconti(array, time): 
    clean_arr = np.empty((len(array)))
    for i in range(len(array)):
        if (i>2) & (i<len(array)-2):
            if min(abs(array[i]-array[i+1])/(time[i+1]-time[i]).total_seconds(), abs(array[i]-array[i-1])/(time[i]-time[i-1]).total_seconds()) > 0.3:
                clean_arr[i] = (array[i-1]+array[i+1])/2
            else:
                clean_arr[i] = array[i]
        else:
            clean_arr[i] = array[i]
    return clean_arr


# function clean_disconti( tempeaature, time)
# 
# temperature : ndarray
# 
# time : ndarray
# 
# output : 修掉不正常的點

# In[6]:


def mv_avg(x, window_size):
    output_arr = []
    for data_idx in range(0, len(x)):
        if data_idx < window_size-1:
            output_arr.append(np.mean(x[:data_idx+1]))
        elif data_idx == len(x):
            break
        else:
            output_arr.append(np.mean(x[data_idx+1-window_size:data_idx+1]))
    return np.array(output_arr)        


# function mv_avg ( temperature, window_size)
# 
# temperature : ndarray
# 
# window_size :　int
# 
# output : 移動平均，光滑的訊號
# 

# In[12]:


def find_conti(x, time):
    start = 0
    while x[len(x)-start-1]-x[len(x)-start-2] > 0:
        start += 1
    return time[-start-1], x[len(x)-1]-x[len(x)-start-1]


# function find_conti(temperature)
# 
# temperature : ndarray
#     
# return 開始上升的時間點(距離現在前幾秒) , 在這個區間裡面上升幾度

# In[8]:


def data_extraction(path):
    data = pd.read_csv(path)

    data.columns = ["ID", "date", "time", 'hr', 'temp', 'activity']

    data['time'] = data['date']+' '+data['time']

    data = data.drop(['date'], axis = 1)


    data_time = np.array([datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in data['time'].values])

    data_temp = np.array((data['temp'].values)/100)

    modify_temp_watch = clean_disconti(np.copy(data_temp), np.copy(data_time))

    removable_disconti = [i for i, x in enumerate(((modify_temp_watch-data_temp)!=0).astype(int)) if x != 0]
    
    return data_time, modify_temp_watch, removable_disconti


# function data_extraction(path)
# 
# return 
# 
# data_time : ndarray (時間tag, 陣列)
# 
# modify_temp_watch : ndarray (體溫)
# 
# removable_disconti : ndarray (有問題點的index)

# In[9]:


# plt.clf()
# plt.figure(figsize=(16,9))
# plt.plot(data_time[:-increasing_ti], smooth_data[:-increasing_ti] ,'grey')
# plt.plot(data_time[-increasing_ti-1:], smooth_data[-increasing_ti-1:], 'r')
# plt.xlabel('time')
# plt.ylabel('temperature')
# plt.legend(['regular temperature', 'increasing temperature'])
# plt.title("Your temperature is higher then usual and has been increased for "+str(increasing_ti)+" minutes")
# # plt.xticks([datetime.datetime.strftime(data_time[0]+i*datetime.timedelta(seconds = 30), "%H:%M:%S") for i in range(0,5)], rotation = 20)
# plt.xticks(rotation = 60)

# plt.savefig('tmp.png')
# plt.show()


# In[19]:


def main(path, cri_temperature, cri_increasing_time, window_size=None):
    data_time, data_temperature, index_of_remove = data_extraction(path)
    if window_size == None:
        smooth_data = mv_avg(data_temperature, 4)
    else:
        smooth_data = mv_avg(data_temperature, window_size)
    increasing_ti, increasing_temp = find_conti(smooth_data[:-2], data_time)
    if (smooth_data[-1] > cri_temperature) & (data_time[-1] - increasing_ti > datetime.timedelta(seconds = cri_increasing_time)) :
#         print(data_time[-1] - increasing_ti)
        return 1
    else:
        return 0


# function main(data_path, cri_temperature, cri_increasing_time, window_size)
# 
# data_path : format = csv
# 
# cri_temperature : 高於多少溫度
# 
# cri_increasing_time : 升高多少時間(seconds)
# 
# window_size : optional default = 4 移動平均採樣點數
# 
# return : int 
# 
# 1:警示
# 0:沒事

# In[20]:


main(os.path.join('src/', token_list[1], token_list[1]+'.csv'), 36, 15)
