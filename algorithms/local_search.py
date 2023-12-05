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
from algorithms.analyze import analyze_track, draw_track


def adjust(ALL_workpackage, config):
    # 调整A股道
    analyze_track(ALL_workpackage, config, 'not adjust')
    draw_track(ALL_workpackage, config, 'not adjust')
    # ALL_workpackage = adjust_A_workpackage(ALL_workpackage, config)
    # analyze_track(ALL_workpackage, config, 'adjust')
    # draw_track(ALL_workpackage, config, 'adjust')
    return ALL_workpackage

# 调整试车工作包
def adjust_E_workpackage(ALL_workpackage, config):
    pass

def adjust_A_workpackage(ALL_workpackage, config):
    today = convert_str_to_date(config['today'])
    day_len = 10
    end_date = today + relativedelta(days=day_len * 366)
    days_index = [today + relativedelta(days=i) for i in range(day_len * 366)]
    day_worktime_load = {index: 0.0 for index in days_index}
    day_plan = {index: set() for index in days_index}
    train_limit = {index: set() for index in days_index}
    # 列车股道限制
    track_limit={track:{index: set()  for index in days_index} for track in ['A','B','C','AC','E']}
    
    # 统计一年内的每天工时和维修计划
    for index, work in enumerate(ALL_workpackage):
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
        for day_date in work.mainten_day:
            if day_date < end_date:
                day_worktime_load[day_date] += work.Work_Package_Person_Day
                day_plan[day_date].add(index)
                train_limit[day_date].add(work.Train_Number)
                track_limit[track_type][day_date].add(work.Train_Number)
            else:
                break
                
    # 调整A股道超出的工作包
    
    adjust_A_range = [info for info in days_index if len(track_limit[info]) > 4 ]
    print(adjust_A_range)
    for info_day in adjust_A_range:
        print(info_day)
        # 查看这一天维修了超过30日以上的工作包有哪些
        work_list = [index for index in day_plan[info_day] if ALL_workpackage[index].Work_Package_Interval_Conversion_Value > 30]
        # 查看维修的列车有哪些
        train_list_geater_30 = set([ALL_workpackage[index].Train_Number for index in work_list])
        
        work_list = [index for index in day_plan[info_day] if ALL_workpackage[index].Work_Package_Interval_Conversion_Value <= 30]
        # 查看维修的列车有哪些
        train_list_less_30 = set([ALL_workpackage[index].Train_Number for index in work_list])
        
        # 获得这天维修间隔只有大于30天的列车
        train_list = list(train_list_geater_30 - train_list_less_30)
        # 获得每个列车需要维修的工作包数量
        train_workpackage_num = {train:0 for train in train_list}
        for index in day_plan[info_day]:
            if ALL_workpackage[index].Train_Number in train_list:
                train_workpackage_num[ALL_workpackage[index].Train_Number] += 1

        # 按照工作包需要维修的数量从小到大排序train_list
        train_list = sorted(train_list, key=lambda x:train_workpackage_num[x])
        print(train_list)
        
        # 按照列车来进行调节A股道的工作包
        for train in train_list:
            print(train)
            # 判断该天的股道是否已经符合约束
            track_limit={track:{index: set()  for index in days_index} for track in ['A','B','C','AC','E']}
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
            
        
            # 获得这个列车需要维修的工作包
            work_list = [index for index in day_plan[info_day] if ALL_workpackage[index].Train_Number == train]
            
            # 在可选区间内调整这个工作包
            for work_id in work_list:
                # 获得该工作的上一次维修记录
                last_mainten_date, next_mainten_date = get_last_mainten_date(ALL_workpackage[work_id], info_day)
                # 维修间隔
                interval_days = int(ALL_workpackage[work_id].Work_Package_Interval_Conversion_Value)

                # 根据历史维修信息，计算下一次维修的日期
                this_mainten_date = last_mainten_date + relativedelta(days=interval_days)
                # 如果下次维修的日期小于当前日期，说明已经欠修，需要将当前日期置为第一次维修
                if this_mainten_date < today:
                    this_mainten_date = today

                # 确定这次维修的上下界
                if interval_days <= 90:
                    upper_bound_1 = this_mainten_date + relativedelta(days=int(interval_days * 0.05))
                    lower_bound_1 = this_mainten_date - relativedelta(days=int(interval_days * 0.05))
                else:
                    upper_bound_1 = this_mainten_date + relativedelta(days=int(interval_days * 0.10))
                    lower_bound_1 = this_mainten_date - relativedelta(days=int(interval_days * 0.10))

                # 根据下一次维修的日期，反推出上一次可接受的维修日期
                if 30 < interval_days <= 90:
                    upper_bound_2 = next_mainten_date - relativedelta(days=int(interval_days * 0.95))
                    lower_bound_2 = next_mainten_date - relativedelta(days=int(interval_days * 1.05))
                else:
                    upper_bound_2 = next_mainten_date - relativedelta(days=int(interval_days * 0.90))
                    lower_bound_2 = next_mainten_date - relativedelta(days=int(interval_days * 1.05))

                # 获得这两个区间的一个交集天数
                upper_bound = min(upper_bound_1, upper_bound_2, today + relativedelta(days=day_len *364))
                lower_bound = max(today, lower_bound_1, lower_bound_2)
                print(upper_bound, lower_bound)
                # 获得这个区间内的所有天数，python的日期格式
                current_day = lower_bound
                range_days = []

                while current_day <= upper_bound:
                    range_days.append(current_day)
                    current_day += relativedelta(days=1)  # 使用timedelta来增加一天
                    
                # 寻找一天列车A股道满足约束
                all = {}
                for day_info in range_days:
                    if len(track_limit[day_info]) < 4 or train in track_limit[day_info]:
                        all[day_info] = day_worktime_load[day_info]
                print(range_days)
                print(all)
                if len(all) != 0:
                    min_day = min(all, key=all.get)
                    print(train, work_id, min_day)
                    index = ALL_workpackage[work_id].mainten_day.index(info_day)
                    ALL_workpackage[work_id].mainten_day[index] = min_day
                    day_worktime_load[min_day] += ALL_workpackage[work_id].Work_Package_Person_Day
                    day_worktime_load[info_day] -= ALL_workpackage[work_id].Work_Package_Person_Day
                    track_limit[min_day].add(train)
                    
    return ALL_workpackage
                        

def adjust_worktime_load_balance(ALL_workpackage, config):
    analyze_track(ALL_workpackage, config, 'not adjust')
    draw_track(ALL_workpackage, config, 'not adjust')
    return ALL_workpackage
    # exit(0)

    # 绘图
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
    cnt = 0
    for index, work in enumerate(ALL_workpackage):
        for day_date in work.mainten_day:
            if day_date < end_date:
                day_worktime_load[day_date] += work.Work_Package_Person_Day
                day_plan[day_date].add(index)
                if work.Work_Package_Interval_Conversion_Value > 30:
                    cnt += 1
                train_limit[day_date].add(work.Train_Number)
            else:
                break
    print(f'一年内月计划工作共执行次数为{cnt}')

    for key, value in day_plan.items():
        track = set()
        for index in value:
            track_type_priority = {track[0]: track[1] for track in ALL_workpackage[index].Track_Type_Priority}
            if len(track_type_priority) == 1:
                if 'A' in track_type_priority:
                    track.add(('A', ALL_workpackage[index].Train_Number))
                elif 'C' in track_type_priority:
                    track.add(('C', ALL_workpackage[index].Train_Number))
            elif 'A' in track_type_priority and 'C' in track_type_priority:
                track.add(('AC', ALL_workpackage[index].Train_Number))
        for info in track:
            if info[0] == 'A':
                track_limit[key].add(info[1])
            elif info[0] == 'C':
                temp_track_limit[key].add(info[1])

    t1_1 = []
    t1_2 = []
    t1_3 = []
    t1_4 = []
    t1_5 = []
    for info in sorted(days_index)[:day_len * 365]:
        t1_1.append(day_worktime_load[info])
        t1_2.append(len(train_limit[info]))
        t1_3.append(len(track_limit[info]))
        t1_4.append(len(temp_track_limit[info]))
        t1_5.append(len(track_limit[info]) + len(temp_track_limit[info]))

    # 首先处理工时较大的天数
    number_of_local_adjustments = int(config['number_of_local_adjustments'])
    mainten_set = set()

    print('正在调整工时较大的天数...')
    # 开始执行local search
    for _ in tqdm(range(number_of_local_adjustments)):
        today = convert_str_to_date(config['today'])
        end_date = today + relativedelta(days=365 * day_len)
        days_index = [today + relativedelta(days=i) for i in range(day_len * 365)]
        day_worktime_load = {index: 0 for index in days_index}
        day_plan = {index: set() for index in days_index}
        train_limit = {index: set() for index in days_index}

        # 统计一年内的每天工时和维修计划

        # 一年内的所有月计划包的维修计划
        mainten_list = []

        for index, work in enumerate(ALL_workpackage):
            if work.Work_Package_Number in ['1505-01', '1505-02']:
                continue
            for indexx, day_date in enumerate(work.mainten_day):
                if day_date < end_date:
                    day_worktime_load[day_date] += work.Work_Package_Person_Day
                    day_plan[day_date].add(index)
                    train_limit[day_date].add(work.Train_Number)
                    if work.Work_Package_Interval_Conversion_Value <= 30:
                        continue
                    mainten_list.append((day_date, index, indexx))
                else:
                    break

        mainten_list.sort(key=lambda x: (day_worktime_load[x[0]], ALL_workpackage[x[1]].Work_Package_Person_Day), reverse=True)

        for info in mainten_list:
            max_day, max_work_id, index_tmp = info
            if (max_work_id, index_tmp) not in mainten_set:
                break

        mainten_set.add((max_work_id, index_tmp))

        # 获得该工作的上一次维修记录
        last_mainten_date, next_mainten_date = get_last_mainten_date(ALL_workpackage[max_work_id], max_day)
        # 维修间隔
        interval_days = int(ALL_workpackage[max_work_id].Work_Package_Interval_Conversion_Value)

        # 根据历史维修信息，计算下一次维修的日期
        this_mainten_date = last_mainten_date + relativedelta(days=interval_days)
        # 如果下次维修的日期小于当前日期，说明已经欠修，需要将当前日期置为第一次维修
        if this_mainten_date < today:
            this_mainten_date = today

        # 确定这次维修的上下界
        if interval_days <= 90:
            upper_bound_1 = this_mainten_date + relativedelta(days=int(interval_days * 0.05))
            lower_bound_1 = this_mainten_date - relativedelta(days=int(interval_days * 0.05))
        else:
            upper_bound_1 = this_mainten_date + relativedelta(days=int(interval_days * 0.10))
            lower_bound_1 = this_mainten_date - relativedelta(days=int(interval_days * 0.10))

        # 根据下一次维修的日期，反推出上一次可接受的维修日期
        if 30 < interval_days <= 90:
            upper_bound_2 = next_mainten_date - relativedelta(days=int(interval_days * 0.95))
            lower_bound_2 = next_mainten_date - relativedelta(days=int(interval_days * 1.05))
        else:
            upper_bound_2 = next_mainten_date - relativedelta(days=int(interval_days * 0.90))
            lower_bound_2 = next_mainten_date - relativedelta(days=int(interval_days * 1.05))

        # 获得这两个区间的一个交集天数
        upper_bound = min(upper_bound_1, upper_bound_2, today + relativedelta(days=364))
        lower_bound = max(today, lower_bound_1, lower_bound_2)

        # 获得这个区间内的所有天数，python的日期格式
        current_day = lower_bound
        range_days = []

        while current_day <= upper_bound:
            range_days.append(current_day)
            current_day += relativedelta(days=1)  # 使用timedelta来增加一天

        # 在这个区间内，选择一天工时最小，且列车约束满足的条件,暂时未考虑月计划的天数
        min_worktime = float('inf')
        min_day = -1
        for day_info in range_days:
            if ALL_workpackage[max_work_id].Train_Number in train_limit[day_info] or len(train_limit[day_info]) <= 5:
                if min_worktime >= day_worktime_load[day_info]:
                    min_worktime = day_worktime_load[day_info]
                    min_day = day_info

        # 将这个工作安排到这天
        # 查找max_day对应的索引
        if min_day != -1:
            index = ALL_workpackage[max_work_id].mainten_day.index(max_day)
            ALL_workpackage[max_work_id].mainten_day[index] = min_day

    print(f'共调整月计划工作包{len(mainten_set)}次')

    # 绘图
    today = convert_str_to_date(config['today'])
    end_date = today + relativedelta(days=day_len * 365)
    days_index = [today + relativedelta(days=i) for i in range(day_len * 365)]
    day_worktime_load = {index: 0.0 for index in days_index}
    day_plan = {index: set() for index in days_index}
    train_limit = {index: set() for index in days_index}

    # 统计一年内的每天工时和维修计划
    for index, work in enumerate(ALL_workpackage):
        for day_date in work.mainten_day:
            if day_date < end_date:
                day_worktime_load[day_date] += work.Work_Package_Person_Day
                day_plan[day_date].add(index)
                train_limit[day_date].add(work.Train_Number)
            else:
                break

    for key, value in day_plan.items():
        track = set()
        for index in value:
            track_type_priority = {track[0]: track[1] for track in ALL_workpackage[index].Track_Type_Priority}
            if len(track_type_priority) == 1:
                if 'A' in track_type_priority:
                    track.add(('A', ALL_workpackage[index].Train_Number))
                elif 'C' in track_type_priority:
                    track.add(('C', ALL_workpackage[index].Train_Number))
            elif 'A' in track_type_priority and 'C' in track_type_priority:
                track.add(('AC', ALL_workpackage[index].Train_Number))
        for info in track:
            if info[0] == 'A':
                track_limit[key].add(info[1])
            elif info[0] == 'C':
                temp_track_limit[key].add(info[1])

    t2_1 = []
    t2_2 = []
    t2_3 = []
    t2_4 = []
    t2_5 = []
    for info in sorted(days_index)[:day_len * 365]:
        t2_1.append(day_worktime_load[info])
        t2_2.append(len(train_limit[info]))
        t2_3.append(len(track_limit[info]))
        t2_4.append(len(temp_track_limit[info]))
        t2_5.append(len(track_limit[info]) + len(temp_track_limit[info]))

    plt.clf()
    plt.plot(t1_1, label='not adjust worktime', color='b')
    plt.plot(t2_1, label='adjust worktime', color='r')
    y_ticks = [160, 180, 200, 220, 240]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.legend()
    plt.title(f'month_worktime_load_{number_of_local_adjustments}')
    plt.savefig(f'./results/month_worktime_load.png')

    plt.clf()
    plt.plot(t1_2, label='not adjust train number', color='b')
    plt.plot(t2_2, label='adjust train number', color='r')
    y_ticks = [2, 3, 4, 5, 6, 7, 14]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.legend()
    plt.title(f'month_train_number_{number_of_local_adjustments}')
    plt.savefig(f'./results/month_train_number.png')

    plt.clf()
    plt.plot(t1_3, label='Only A', color='b')
    plt.plot(t1_4, label='Only C', color='r')
    # plt.scatter(t1_5, label=' A+C', color='g')
    y_ticks = [1, 2, 3, 4, 5, 6, 7, 14]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.legend()
    plt.title(f'track_noadjust_{number_of_local_adjustments}')
    plt.savefig(f'./results/track_noadjust_{number_of_local_adjustments}.png')

    plt.clf()
    plt.plot(t2_3, label='Only A', color='b')
    plt.plot(t2_4, label='Only C', color='r')
    # plt.scatter(t2_5, label=' A+C', color='g')
    y_ticks = [1, 2, 3, 4, 5, 6, 7, 14]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.legend()
    plt.title(f'track_adjust_{number_of_local_adjustments}')
    plt.savefig(f'./results/track_adjust_{number_of_local_adjustments}.png')

    return ALL_workpackage


def get_last_mainten_date(workpackage, this_mainten_date):
    # 寻找上一次维修的日期
    last_mainten_date = workpackage.last_mainten_time
    for date in workpackage.mainten_day:
        if date < this_mainten_date:
            last_mainten_date = date
        else:
            break
    # 寻找本次维修的下一次维修的日期
    next_mainten_date = None
    for date in workpackage.mainten_day:
        if date > this_mainten_date:
            next_mainten_date = date
            break
        else:
            continue
    return last_mainten_date, next_mainten_date


def _draw(day_worktime_load, train_limit, index, str_name):
    t1 = []
    t2 = []
    for info in sorted(index)[:365]:
        t1.append(day_worktime_load[info])
        t2.append(len(train_limit[info]))
    plt.clf()
    plt.scatter(t1, label='work time', color='r')
    y_ticks = [20 * i for i in range(1, 13)]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.savefig(f'./results/{str_name}_month_worktime_load.png')

    plt.clf()
    plt.scatter(t2, label='train number', color='b')
    y_ticks = [2, 3, 4, 7, 14]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.savefig(f'./results/{str_name}_train_number.png')
