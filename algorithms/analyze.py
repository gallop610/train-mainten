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
    today = convert_str_to_date(config['today'])
    days_index = [today + relativedelta(days=i) for i in range(366 * 30)]
    track_limit={track:{index: set()  for index in days_index} for track in ['A','B','C','AC','E']}
    need_track_limie = {}
    
    for work in ALL_workpackage:
        if work.Work_Package_Interval_Conversion_Value <= 16:
            continue
        track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}
        if len(work.Track_Type_Priority) == 1 and 'A' in track_type_priority:
            track_type = 'A'
        elif len(work.Track_Type_Priority) == 1 and 'B' in track_type_priority:
            track_type = 'B'
        elif len(work.Track_Type_Priority) == 1 and 'C' in track_type_priority:
            track_type = 'C'
        elif 'A' in work.Track_Type_Priority and 'C' in track_type_priority:
            track_type = 'AC'
        else:
            track_type = 'A'

        for day_info in work.mainten_day:
            track_limit[track_type][day_info].add(work.Train_Number)
            if work.Need_Trial_Run == '是':
                if day_info not in need_track_limie:
                    need_track_limie[day_info] = set()
                need_track_limie[day_info].add(work.Train_Number)
            
    track_A = track_limit['A']
    track_A = dict(sorted(track_A.items(), key=lambda x: x[0]))
    with open(f'./results/{s_info}_track_limit.txt', 'w') as f:
        for key, value in track_A.items():
            if len(value) > 4:
                f.write('{},{}\n'.format(key, ','.join([str(v) for v in value])))
                
    with open(f'./results/{s_info}_track_limit_tmp.txt', 'w') as f:
        for key, value in track_A.items():
            if len(value) == 4:
                f.write('{},{}\n'.format(key, ','.join([str(v) for v in value])))

    track_C = track_limit['C']
    track_C = dict(sorted(track_C.items(), key=lambda x: x[0]))
    with open(f'./results/{s_info}_temp_track_limit.txt', 'w') as f:
        for key, value in track_C.items():
            if len(value) > 1:
                f.write('{},{}\n'.format(key, ','.join([str(v) for v in value])))
    
    need_track_limie = dict(sorted(need_track_limie.items(), key=lambda x: x[0]))
    with open(f'./results/{s_info}_need_track_limie.txt', 'w') as f:
        for key, value in need_track_limie.items():
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
                if work.Work_Package_Number != '1505-01':
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


def analyze_interval(ALL_workpackage, config, s_info):
    today = convert_str_to_date(config['today'])
    days_index = [today + relativedelta(days=i) for i in range(30 * 366)]
    day_worktime_load = {index: 0.0 for index in days_index}
    day_plan = {index: set() for index in days_index}

    for index, work in enumerate(ALL_workpackage):
        for day_date in work.mainten_day:
            if work.Work_Package_Number != '1505-01':
                day_worktime_load[day_date] += work.Work_Package_Person_Day
            day_plan[day_date].add(index)
            
    for day in days_index:
        # 统计维修天数之差和工时间隔
        interval_list = []
        for work_id in day_plan[day]:
            mainten_index = ALL_workpackage[work_id].mainten_day.index(day)
            if mainten_index == 0:
                last_mainten_day = ALL_workpackage[work_id].Online_Date
            interval_day = (day-last_mainten_day).days
            interval_list.append((interval_day, ALL_workpackage[work_id].Work_Package_Interval_Value))
            
        
        
        
        day_worktime_load[day] = day_worktime_load[day] / 8.0