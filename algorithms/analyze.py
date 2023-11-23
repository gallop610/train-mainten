from SchedulingEntities import *
import numpy as np
import copy
from utils import *
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pdb
import matplotlib.pyplot as plt
import math
import pandas as pd
from tqdm import tqdm
import os

# 分析30年内的股道使用数量，以文字的形式输出
def analyze_track(ALL_workpackage, config, s_info):
    # 绘图
    # A股道
    track_limit = {}
    # C股道
    temp_track_limit = {}
    for work in ALL_workpackage:
        track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}
        if len(track_type_priority) == 1:
            if 'A' in track_type_priority:
                track = ('A', work.Train_Number)
            elif 'C' in track_type_priority:
                track = ('C', work.Train_Number)
        elif 'A' in track_type_priority and 'C' in track_type_priority:
            track = ('AC', work.Train_Number)
        else:
            continue
        
        for day_info in work.mainten_day:
            if track[0] == 'A':
                if day_info not in track_limit:
                    track_limit[day_info] = set()
                track_limit[day_info].add(track[1])
            elif track[0] == 'C':
                if day_info not in temp_track_limit:
                    temp_track_limit[day_info] = set()
                temp_track_limit[day_info].add(track[1])
                
    track_limit = dict(sorted(track_limit.items(), key=lambda x: x[0]))
    with open(f'./results/{s_info}_track_limit.txt', 'w') as f:
        for key, value in track_limit.items():
            if len(value) > 3:
                f.write('{},{}\n'.format(key, ','.join([str(v) for v in value])))
    
    temp_track_limit = dict(sorted(temp_track_limit.items(), key=lambda x: x[0]))
    with open(f'./results/{s_info}_temp_track_limit.txt', 'w') as f:
        for key, value in temp_track_limit.items():
            if len(value) > 1:
                f.write('{},{}\n'.format(key, ','.join([str(v) for v in value])))


# 绘制股道使用情况图，时间是1年或者2年 
def draw_track(ALL_workpackage, config, s_info):
    today = convert_str_to_date(config['today'])
    day_len = 1
    end_date = today + relativedelta(days=day_len * 366)
    days_index = [today + relativedelta(days=i) for i in range(day_len * 366)]
    day_worktime_load = {index: 0.0 for index in days_index}
    day_plan = {index: set() for index in days_index}
    train_limit = {index: set() for index in days_index}
    # 检修道数量限制
    track_limit = {index: set() for index in days_index}
    # 临修道数量限制
    temp_track_limit = {index: set() for index in days_index}

    # 统计一年内的每天工时和维修计划
    for work in ALL_workpackage:
        for day_date in work.mainten_day:
            if day_date < end_date:
                day_worktime_load[day_date] += work.Work_Package_Person_Day
                train_limit[day_date].add(work.Train_Number)
            else:
                break

    for work in ALL_workpackage:
        track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}
        if len(track_type_priority) == 1:
            if 'A' in track_type_priority:
                track = ('A', work.Train_Number)
            elif 'C' in track_type_priority:
                track = ('C', work.Train_Number)
        elif 'A' in track_type_priority and 'C' in track_type_priority:
            track = ('AC', work.Train_Number)
        else:
            continue
        
        for day_info in work.mainten_day:
            if day_info < end_date:
                if track[0] == 'A':
                    track_limit[day_info].add(track[1])
                elif track[0] == 'C':
                    temp_track_limit[day_info].add(track[1])
            else:
                break

    t1 = []
    t2 = []
    t3 = []
    t4 = []
    t5 = []
    for info in sorted(days_index)[:day_len * 365]:
        t1.append(day_worktime_load[info])
        t2.append(len(train_limit[info]))
        t3.append(len(track_limit[info]))
        t4.append(len(temp_track_limit[info]))
        t5.append(len(track_limit[info]) + len(temp_track_limit[info]))
    
    plt.clf()
    plt.plot(t1, label=f'{s_info} worktime', color='b')
    y_ticks = [160, 180, 200, 220, 240]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.legend()
    plt.title(f'{s_info}_month_worktime_load')
    plt.savefig(f'./results/{s_info}_month_worktime_load.png')

    plt.clf()
    plt.plot(t2, label=f'{s_info} train number', color='b')
    y_ticks = [2, 3, 4, 5, 6, 7, 14]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.legend()
    plt.title(f'{s_info}_month_train_number')
    plt.savefig(f'./results/{s_info}_month_train_number.png')

    plt.clf()
    plt.plot(t3, label='Only A', color='b')
    plt.plot(t4, label='Only C', color='r')
    # plt.scatter(t1_5, label=' A+C', color='g')
    y_ticks = [1, 2, 3, 4, 5, 6, 7, 14]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.legend()
    plt.title(f'{s_info}_track_number')
    plt.savefig(f'./results/{s_info}_track_number.png')


    