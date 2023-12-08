from SchedulingEntities import *
import numpy as np
import copy
from utils import *
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import pdb
import matplotlib.pyplot as plt
import math
import pandas as pd
from tqdm import tqdm


def month_plan(month_plan_workpackage, year_plan_workpackage, config):
    # 初始化参数
    today = convert_str_to_date(config['today'])
    current_day = today
    days_index = [today + relativedelta(days=i) for i in range(366 * 30)]
    month_overtake_percentage = float(config['year_overtake_percentage'])
    alpha = float(config['month_alpha'])

    sum_interval = 0
    # 初始化日期负载工时
    day_worktime_load = {index: {'all': 0.0} for index in days_index}
    # 维修列车数量限制
    train_limit = {index: set() for index in days_index}
    # 维修列车股道限制
    track_limit = {track: {index: set() for index in days_index} for track in ['A', 'B', 'C', 'AC', 'E']}
    track_limit_number = {'A': 4, 'B': 28, 'C': 2, 'AC': 5}

    # lock限制在某天不能再修某辆车，用于1505-01工作包
    train_lock = {index: {i: False for i in range(1, 29)} for index in days_index}
    # 周转件数量限制
    turnover_limit = _day_turnover_package(year_plan_workpackage, days_index)

    for work in month_plan_workpackage:
        # 寻找维修间隔为8的工作包，开始直接排列
        if work.Work_Package_Interval_Conversion_Value == 8:
            work.mainten_day = []
            start_mainten_date = work.Online_Date
            end_mainten_date = start_mainten_date + relativedelta(days=366 * 30)

            next_mainten_date = work.last_mainten_time + relativedelta(days=8)
            while next_mainten_date <= end_mainten_date:
                work.mainten_day.append(next_mainten_date)
                # 统计天维修工时负载
                day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
                # 统计列车维修工时负载
                if work.Train_Number not in day_worktime_load[next_mainten_date]:
                    day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
                train_limit[next_mainten_date].add(work.Train_Number)  # 维修的列车数量
                track_limit['B'][next_mainten_date].add(work.Train_Number)  # 维修的列车的股道
                next_mainten_date = next_mainten_date + relativedelta(days=8)

    # 处理16日工作包
    for work in month_plan_workpackage:
        # 寻找维修间隔为16的工作包，开始直接排列
        if work.Work_Package_Interval_Conversion_Value == 16:
            work.mainten_day = []
            start_mainten_date = work.Online_Date
            end_mainten_date = start_mainten_date + relativedelta(days=366 * 30)

            next_mainten_date = work.last_mainten_time + relativedelta(days=16)
            while next_mainten_date <= end_mainten_date:
                work.mainten_day.append(next_mainten_date)
                day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
                # 统计列车维修工时负载
                if work.Train_Number not in day_worktime_load[next_mainten_date]:
                    day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
                train_limit[next_mainten_date].add(work.Train_Number)  # 维修的列车数量
                track_limit['B'][next_mainten_date].add(work.Train_Number)  # 维修的列车的股道
                next_mainten_date = next_mainten_date + relativedelta(days=16)

    for work in year_plan_workpackage:
        if work.Work_Package_Interval_Conversion_Value == 45:
            work.mainten_day = []
            start_mainten_date = work.Online_Date
            end_mainten_date = start_mainten_date + relativedelta(days=366 * 30)
            interval_days = 45

            next_mainten_date = work.last_mainten_time + relativedelta(days=45)
            while next_mainten_date <= end_mainten_date:
                float_range_ub = 3
                upper_bound = next_mainten_date + relativedelta(days=int(float_range_ub))
                float_range_lb = 4
                lower_bound = next_mainten_date - relativedelta(days=int(float_range_lb))

                # 判断上界和下界的日期会不会超出边界，满足调节则置为边界值
                if upper_bound >= end_mainten_date:
                    upper_bound = end_mainten_date - relativedelta(days=1)

                if lower_bound < current_day:
                    lower_bound = current_day
                date_difference = (upper_bound - lower_bound).days
                date_range = [lower_bound + relativedelta(days=i) for i in range(date_difference + 1)]
                for date_info in date_range:
                    if work.Train_Number in train_limit[date_info]:
                        next_mainten_date = date_info
                        break
                work.mainten_day.append(next_mainten_date)
                day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
                # 统计列车维修工时负载
                if work.Train_Number not in day_worktime_load[next_mainten_date]:
                    day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
                train_limit[next_mainten_date].add(work.Train_Number)  # 维修的列车数量
                track_limit['B'][next_mainten_date].add(work.Train_Number)  # 维修的列车的股道
                next_mainten_date = next_mainten_date + relativedelta(days=45)

    # 处理30日工作包
    for work in month_plan_workpackage:
        # 寻找维修间隔为30的工作包，开始直接排列
        if work.Work_Package_Interval_Conversion_Value == 30:
            work.mainten_day = []
            start_mainten_date = work.Online_Date
            end_mainten_date = start_mainten_date + relativedelta(days=366 * 30)

            # 将股道优先级按字典存储并根据优先级排序
            track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}

            next_mainten_date = work.last_mainten_time + relativedelta(days=30)
            if next_mainten_date < today:
                next_mainten_date = today
            while next_mainten_date <= end_mainten_date:
                work.mainten_day.append(next_mainten_date)
                day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
                # 统计列车维修工时负载
                if work.Train_Number not in day_worktime_load[next_mainten_date]:
                    day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
                train_limit[next_mainten_date].add(work.Train_Number)  # 维修的列车数量
                track_limit['A'][next_mainten_date].add(work.Train_Number)  # 维修的列车的股道
                next_mainten_date = next_mainten_date + relativedelta(days=30)

    turnover_package, not_turnover_package, special_package = _select_turnover_package(year_plan_workpackage)
    #对于1505-01和1505-02两个包，存在可能为train_lock的原因导致后续的周转包无法排开问题（不一定会出现，当数据量增大时出现的概率增大），现有两种方案
    #方案1：将对该两个包的处理放在对周转件处理之后，同时对该两个包的维修日期范围进行扩展（防止出现因为找不到合适的时间而不能排的情况）
    #方案2：对周转件包的处理进行适当的左右扩展，现有的周转件的周转间隔存在缝隙，比如cd为7的工作包会导致在一个月30天的月份存在2天的扩展缝隙
    #但当数据量不大时，现有的代码已可以满足情况
    #现处理方案：将两个包独立于年计划，根据间隔设置上下限，通过控制上下限扩大或缩小范围（避免初期拥塞情况），通过选择函数选择接近于维修日期的天

    for work in tqdm(special_package, desc="处理1505-01工作包"):
        #如果把这段处理放在周转包前会出现因为lock的原因导致周转包无法排开（无解）的情况
        #这段代码注释掉了周转件处理中的检测lock所以可以正常运行，后续考虑如何解决或者把这段处理放在周转件处理之后
        if work.Work_Package_Number == "1505-01" or work.Work_Package_Number == "1505-02":
            combind_work_package = [info for info in special_package if info.Work_Package_Number == work.Combined_Work_Package_Number]
            #暂时先不管1505-02
            if (work.Work_Package_Number == "1505-02"):
                work.mainten_day = []
                continue

            # 将股道优先级按字典存储并根据优先级排序
            track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}
            # work.mainten_track_type = {index:set() for index in days_index}

            work.mainten_day = []
            start_mainten_date = work.Online_Date
            end_mainten_date = start_mainten_date + relativedelta(days=366 * 30)
            last_mainten_date = work.last_mainten_time
            interval_days = int(work.Work_Package_Interval_Conversion_Value)
            # 根据历史维修信息，计算下一次维修的日期
            next_mainten_date = last_mainten_date + relativedelta(days=interval_days)
            if next_mainten_date < current_day:
                next_mainten_date = current_day
            while next_mainten_date < end_mainten_date:
                #考虑上下限之间的周末情况
                #min_day_range = _select_less_day_turnover_worktime_load(day_worktime_load, range_days, next_mainten_date, alpha)
                float_range_ub = interval_days * 0.1
                upper_bound = next_mainten_date + relativedelta(days=int(float_range_ub))
                #上限原本为0.05，此处为了避免初期拥塞导致排不开的情况，将其改为0.1
                float_range_lb = interval_days * 0.1
                lower_bound = next_mainten_date - relativedelta(days=int(float_range_lb))

                # 判断上界和下界的日期会不会超出边界，满足调节则置为边界值
                if upper_bound >= end_mainten_date:
                    upper_bound = end_mainten_date - relativedelta(days=1)

                if lower_bound < current_day:
                    lower_bound = current_day
                range_days = _generate_weekend_days(lower_bound, upper_bound)
                flag_min_day = False
                next_mainten_date = _select_weekend_1505(work, range_days, train_limit, turnover_limit, next_mainten_date)
                # 确定当前维修日期之后，将当前维修日期添加到工作包维修日期列表，日期工时负载增加，并获取下次维修日期
                if next_mainten_date - relativedelta(days=7) >= current_day:
                    turnover_limit[work.Work_Package_Number][next_mainten_date - relativedelta(days=7)] = False
                turnover_limit[work.Work_Package_Number][next_mainten_date] = False
                #该包的冷却时间为14，故下周的周转情况应该也置为false
                turnover_limit[work.Work_Package_Number][next_mainten_date + relativedelta(days=7)] = False

                #周六处理
                train_limit[next_mainten_date].add(work.Train_Number)
                work.mainten_day.append(next_mainten_date)
                train_lock[next_mainten_date][work.Train_Number] = True
                track_limit['C'][next_mainten_date].add(work.Train_Number)  # 维修的列车的股道

                #周日处理
                week_end = next_mainten_date + relativedelta(days=1)
                train_limit[week_end].add(work.Train_Number)
                train_lock[week_end][work.Train_Number] = True
                track_limit['C'][week_end].add(work.Train_Number)  # 维修的列车的股道
                if work.Need_Trial_Run == '是':
                    track_limit['E'][week_end].add(work.Train_Number)

                # 统计列车维修工时负载,暂时好像还没用上？
                if work.Train_Number not in day_worktime_load[next_mainten_date]:
                    day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day

                if work.Train_Number not in day_worktime_load[week_end]:
                    day_worktime_load[week_end][work.Train_Number] = 0.0
                day_worktime_load[week_end][work.Train_Number] += work.Work_Package_Person_Day

                next_mainten_date = next_mainten_date + relativedelta(days=interval_days)

    # 平均分配每天周转件的数量
    # 提取出所有的周转件
    # 后续该处代码还需要优化，给出一个通用解决方案
    turnover_start_day = defaultdict(set)
    for work in turnover_package:
        if work.Shared_Cooling_Work_Package_Number == 'None':
            key = (work.Work_Package_Number, work.Cooling_Time)
            turnover_start_day[key] = 0
        else:
            key = (work.Shared_Cooling_Work_Package_Number, work.Cooling_Time)
            turnover_start_day[key] = 0
    # 平均分配每天的工作量
    cnt1 = 1
    cnt2 = 1
    for info in sorted(turnover_start_day, key=lambda x: (x[1], x[0]), reverse=False):
        if info[1] == 14:
            turnover_start_day[info] = cnt1
            cnt1 += 1
            if cnt1 == 15:
                cnt1 = 1
        else:
            turnover_start_day[info] = cnt2
            cnt2 += 1
            if cnt2 == 8:
                cnt2 = 1

    for work in tqdm(turnover_package, desc='处理周转件'):
        work.mainten_day = []
        # 初始化基本信息
        # 确定这辆列车可以维修的轨道
        track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}
        if len(work.Track_Type_Priority) == 1 and 'A' in track_type_priority:
            track_type = 'A'
        elif len(work.Track_Type_Priority) == 1 and 'B' in track_type_priority:
            track_type = 'B'
        elif len(work.Track_Type_Priority) == 1 and 'C' in track_type_priority:
            track_type = 'C'
        elif 'B' in track_type_priority and track_type_priority['B'] == 1:
            track_type = 'B'
        elif 'A' in track_type_priority and 'C' in track_type_priority:
            track_type = 'AC'
        # elif 'A' in track_type_priority and 'C' not in track_type_priority:
        #     track_type = 'A'
        # elif 'A' not in track_type_priority and 'C' in track_type_priority:
        #     track_type = 'C'
        else:
            track_type = 'A'
            
        start_mainten_date = work.Online_Date
        end_mainten_date = start_mainten_date + relativedelta(days=366 * 30)

        # 上次维修的date
        last_mainten_date = work.last_mainten_time
        # 维修间隔
        interval_days = int(work.Work_Package_Interval_Conversion_Value)

        # 根据历史维修信息，计算下一次维修的日期
        next_mainten_date = last_mainten_date + relativedelta(days=interval_days)
        # 如果下次维修的日期小于当前日期，说明已经欠修，需要将当前日期置为第一次维修
        if next_mainten_date < current_day:
            next_mainten_date = current_day

        if work.Shared_Cooling_Work_Package_Number == 'None':
            initial_number = turnover_start_day[(work.Work_Package_Number, work.Cooling_Time)]
        else:
            initial_number = turnover_start_day[(work.Shared_Cooling_Work_Package_Number, work.Cooling_Time)]

        for month in work.mainten_month:
            range_days = _generate_month_days(month)

            if work.Cooling_Time == 7:
                # initial_number = turnover_start_day[(work.Work_Package_Number, work.Cooling_Time)]
                result = [initial_number + i * 7 for i in range(4)]
                range_days = [info for info in range_days if info.day in result]
            elif work.Cooling_Time == 14:
                # initial_number = turnover_start_day[(work.Work_Package_Number, work.Cooling_Time)]
                result = [initial_number + i * 14 for i in range(2)]
                range_days = [info for info in range_days if info.day in result]
            elif work.Cooling_Time == 25:
                # initial_number = turnover_start_day[(work.Work_Package_Number, work.Cooling_Time)]
                result = [initial_number]
                range_days = [info for info in range_days if info.day in result]

            min_day_range = _select_less_day_turnover_worktime_load(day_worktime_load, range_days, next_mainten_date, alpha)

            flag_min_day = False
            for min_day in min_day_range:
                # 判断周转件是否符合
                if turnover_limit[work.Work_Package_Number][min_day] == False or train_lock == True:
                    continue
                next_mainten_date = min_day
                flag_min_day = True
                break
            if not flag_min_day:
                print('无法找到合适的周转件，工作包编号为：', work.Work_Package_Number)
                exit(-1)

            if next_mainten_date > end_mainten_date:
                break

            # 确定当前维修日期之后，将当前维修日期添加到工作包维修日期列表，日期工时负载增加，并获取下次维修日期
            turnover_limit[work.Work_Package_Number][next_mainten_date] = False
            train_limit[next_mainten_date].add(work.Train_Number)
            track_limit[track_type][next_mainten_date].add(work.Train_Number)  # 维修的列车的股道
            if work.Need_Trial_Run == '是':
                track_limit['E'][next_mainten_date].add(work.Train_Number)
            work.mainten_day.append(next_mainten_date)
            day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
            # 统计列车维修工时负载
            if work.Train_Number not in day_worktime_load[next_mainten_date]:
                day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
            day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
            next_mainten_date = next_mainten_date + relativedelta(days=interval_days)

    def trial_run_value(trial_run):
        return 0 if trial_run == '是' else 1

    not_turnover_package.sort(key=lambda x: (x.Work_Package_Interval_Conversion_Value, x.Train_Number, trial_run_value(x.Need_Trial_Run), x.Work_Package_Person_Day), reverse=False)

    for work in tqdm(not_turnover_package, desc="处理非周转件"):
        if work.Work_Package_Number == '0502-01':
            continue
        # 确定这辆列车可以维修的轨道
        track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}
        if len(work.Track_Type_Priority) == 1 and 'A' in track_type_priority:
            track_type = 'A'
        elif len(work.Track_Type_Priority) == 1 and 'B' in track_type_priority:
            track_type = 'B'
        elif len(work.Track_Type_Priority) == 1 and 'C' in track_type_priority:
            track_type = 'C'
        elif 'A' in track_type_priority and 'C' in track_type_priority:
            track_type = 'AC'
        else:
            track_type = 'A'
            
        work.mainten_day = []
        # 初始化基本信息
        # 股道优先级
        # work.mainten_track_type = {index:set() for index in days_index}

        start_mainten_date = work.Online_Date
        end_mainten_date = start_mainten_date + relativedelta(days=366 * 30)

        # 上次维修的date
        last_mainten_date = work.last_mainten_time
        # 维修间隔
        interval_days = int(work.Work_Package_Interval_Conversion_Value)

        # 根据历史维修信息，计算下一次维修的日期
        next_mainten_date = last_mainten_date + relativedelta(days=interval_days * 1.05)
        # 如果下次维修的日期小于当前日期，说明已经欠修，需要将当前日期置为第一次维修
        if next_mainten_date < current_day:
            next_mainten_date = current_day
        else:
            next_mainten_date = last_mainten_date + relativedelta(days=interval_days)

        for month in work.mainten_month:
            float_range_ub = interval_days * 0.05
            upper_bound = next_mainten_date + relativedelta(days=int(float_range_ub))

            if work.Work_Package_Interval_Conversion_Value > 90:
                float_range_lb = interval_days * 0.1
            else:
                float_range_lb = interval_days * month_overtake_percentage
            lower_bound = next_mainten_date - relativedelta(days=int(float_range_lb))

            # 判断上界和下界的日期会不会超出边界，满足调节则置为边界值
            if upper_bound >= end_mainten_date:
                upper_bound = end_mainten_date - relativedelta(days=1)

            if lower_bound < current_day:
                lower_bound = current_day

                # 按年计划的月份生成日期范围
            range_days = _generate_month_days(month)
            range_days = [day for day in range_days if lower_bound <= day <= upper_bound]
            # 如果根据日期计算时，发现日期不在年计划的月份当中，说明月份排程比较粗糙，可能需要进行修正
            # 方案一：考虑修正，根据日期进行月份修正，暂时不采用年计划的月份
            # 方案二：不考虑修正，按月份选日期

            # 如果[lower_bound, upper_bound]不在当前月份
            # upper_bound比当前月份小的时候，取当前月份前面的天数
            # lower_bound比当前月份大的时候，取当前月份后面的天数
            if range_days == []:
                range_days = _generate_month_days(month)
                if upper_bound < range_days[0]:
                    range_days = range_days[:10]
                elif lower_bound > range_days[-1]:
                    range_days = range_days[-10:]

            min_day = _select_less_day_worktime_load(work, day_worktime_load, range_days, next_mainten_date, alpha, train_limit, track_limit, track_limit_number, track_type, train_lock)
            sum_interval += (min_day - next_mainten_date).days
            next_mainten_date = min_day

            # 确定当前维修日期之后，将当前维修日期添加到工作包维修日期列表，日期工时负载增加，并获取下次维修日期
            work.mainten_day.append(next_mainten_date)
            day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
            # 统计列车维修工时负载
            if work.Train_Number not in day_worktime_load[next_mainten_date]:
                day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
            day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
            train_limit[next_mainten_date].add(work.Train_Number)
            track_limit[track_type][next_mainten_date].add(work.Train_Number)  # 维修的列车的股道
            if work.Need_Trial_Run == '是':
                track_limit['E'][next_mainten_date].add(work.Train_Number)
            next_mainten_date = next_mainten_date + relativedelta(days=interval_days)

    return turnover_package + not_turnover_package + special_package + month_plan_workpackage


def _select_less_day_turnover_worktime_load(day_worktime_load, range_days, next_mainten_date, alpha):
    all = {}

    for i in range_days:
        all[i] = day_worktime_load[i]['all'] + abs((i - next_mainten_date).days) * alpha

    return [k for k, v in sorted(all.items(), key=lambda item: item[1])]


def _select_less_day_worktime_load(work, day_worktime_load, day_range, next_mainten_date, alpha, train_limit, track_limit, track_limit_number, track_type_priority, train_lock):
    """
    从日期负载工时中选择最小的日期。
    
    Args:
        day_worktime_load: 字典类型，包含每个日期的工时负载。
        day_range: list of str
            日期列表，包含所有的日期。
        next_mainten_date: str
            下次维修的季度。
    
    Returns:
        min_day: str
            工时负载最小的日期。
    """
    work_time  = 280
    tmp_day_range = copy.deepcopy(day_range)
    tmp = []
    for info in day_range:
        if len(train_limit[info]) > 7:
            continue
        if track_type_priority == 'A':
            if len(track_limit['A'][info]) > 4:
                continue
        elif track_type_priority == 'C':
            if len(track_limit['C'][info]) > 2:
                continue
        elif track_type_priority == 'AC':
            if len(track_limit['A'][info]) + len(track_limit['C'][info]) + len(track_limit['AC'][info]) > 5:
                continue
        if train_lock[info][work.Train_Number] == True:
            continue
        tmp.append(info)
    day_range = tmp
    # 判断是否需要试车道
    if work.Need_Trial_Run == '是':
        # 1. 维修间隔内存在一天使用对应试车股道的车
        all = {}
        for info in day_range:
            if len(train_limit[info]) >= 7 and work.Train_Number not in train_limit[info]:
                continue
            if work.Train_Number in track_limit['E'][info] and day_worktime_load[info]['all'] < work_time:
                all[info] = day_worktime_load[info]['all'] + abs((info - next_mainten_date).days) * alpha
        if all != {}:
            return min(all, key=all.get)
        # 2. 维修间隔内不存在某天使用对应试车股道的车
        all = {}
        for info in day_range:
            # 尽量不去股道切换
            if len(train_limit[info]) >= 7 and work.Train_Number not in train_limit[info]:
                continue
            if track_type_priority == 'B' and (work.Train_Number in track_limit['A'][info] or work.Train_Number in track_limit['C'][info] or work.Train_Number in track_limit['AC'][info]):
                continue
            elif (track_type_priority == 'A' or track_type_priority == 'C' or track_type_priority == 'AC') and (work.Train_Number in track_limit['B'][info]):
                continue
            elif track_type_priority == 'A' and work.Train_Number in track_limit['C'][info]:
                continue
            elif track_type_priority == 'C' and work.Train_Number in track_limit['A'][info]:
                continue
            if day_worktime_load[info]['all'] > work_time:
                continue
            if (track_type_priority =='A' or track_type_priority =='C') and len(track_limit[track_type_priority][info]) < track_limit_number[track_type_priority]\
                 and len(track_limit['A'][info]) + len(track_limit['C'][info]) + len(track_limit['AC'][info]) < track_limit_number['AC'] and track_limit['E'][info] == set():
                all[info] = day_worktime_load[info]['all'] + abs((info - next_mainten_date).days) * alpha + len(train_limit[info])*100
            if track_type_priority =='AC' and len(track_limit['A'][info]) + len(track_limit['C'][info]) + len(track_limit['AC'][info]) < track_limit_number[track_type_priority] and track_limit['E'][info] == set():
                all[info] = day_worktime_load[info]['all'] + abs((info - next_mainten_date).days) * alpha + len(train_limit[info])*100

        if all != {}:
            return min(all, key=all.get)
    else:
        # 1. 维修间隔内存在一天正好使用该股道的天数
        all = {}
        for info in day_range:
            if len(train_limit[info]) >= 7 and work.Train_Number not in train_limit[info]:
                continue
            if work.Train_Number in track_limit[track_type_priority][info] and day_worktime_load[info]['all'] < work_time:
                all[info] = day_worktime_load[info]['all'] + abs((info - next_mainten_date).days) * alpha

        if all != {}:
            return min(all, key=all.get)

        # 2. 维修天数内，找不到一天使用该股道，因此选择一天股道约束满足的天塞入
        all = {}
        for info in day_range:
            # 尽量不去股道切换
            if len(train_limit[info]) >= 7 and work.Train_Number not in train_limit[info]:
                continue
            if track_type_priority == 'B' and (work.Train_Number in track_limit['A'][info] or work.Train_Number in track_limit['C'][info] or work.Train_Number in track_limit['AC'][info]):
                continue
            elif (track_type_priority == 'A' or track_type_priority == 'C' or track_type_priority == 'AC') and (work.Train_Number in track_limit['B'][info]):
                continue
            elif track_type_priority == 'A' and work.Train_Number in track_limit['C'][info]:
                continue
            elif track_type_priority == 'C' and work.Train_Number in track_limit['A'][info]:
                continue
            if day_worktime_load[info]['all'] > work_time:
                continue
            # if track_limit['E'][info] == set():
            #     continue
            if (track_type_priority =='A' or track_type_priority =='C') and len(track_limit[track_type_priority][info]) < track_limit_number[track_type_priority] \
                and len(track_limit['A'][info]) + len(track_limit['C'][info]) + len(track_limit['AC'][info]) < track_limit_number['AC']:
                all[info] = day_worktime_load[info]['all'] + abs((info - next_mainten_date).days) * alpha +len(train_limit[info])*50
            if track_type_priority =='AC' and len(track_limit['A'][info]) + len(track_limit['C'][info]) + len(track_limit['AC'][info]) < track_limit_number[track_type_priority]:
                all[info] = day_worktime_load[info]['all'] + abs((info - next_mainten_date).days) * alpha +len(train_limit[info])*50

        if all != {}:
            return min(all, key=all.get)

    # 找不到满足股道约束的天，因此选择一天股道约束满足的天塞入

    all = {}
    for info in tmp_day_range:
        if len(train_limit[info]) >= 7 and work.Train_Number not in train_limit[info]:
            continue
        if day_worktime_load[info]['all'] > work_time:
            continue
        if train_lock[info][work.Train_Number] == True:
            continue
        all[info] = day_worktime_load[info]['all'] + abs((info - next_mainten_date).days) * alpha

    if all != {}:
        return min(all, key=all.get)

    all = {}
    for info in tmp_day_range:
        all[info] = day_worktime_load[info]['all'] + abs((info - next_mainten_date).days) * alpha + len(train_limit[info]) * 100
    return min(all, key=all.get)


def _select_weekend_1505(work, range_days, train_limit, turnover_limit, next_mainten_day):
    #专门用来处理1505-01工作包
    all = {}
    flag_min_day = False
    for min_day in range_days:
        # 判断周转件是否符合
        # print(,work.Work_Package_Number, min_day)
        # pdb.set_trace()
        if turnover_limit[work.Work_Package_Number][min_day] == False or work.Train_Number in train_limit[min_day]\
            or work.Train_Number in train_limit[min_day + relativedelta(days= 1)]:
            all[min_day] = 10000
            continue
        all[min_day] = abs((next_mainten_day - min_day).days)
    result = min(all, key=all.get)
    if all[result] == 10000:
        print("wrong")
        exit(-1)
    return result


def _day_turnover_package(workpackage, days_index):
    turnover_limit = {}
    for work in workpackage:
        if work.Cooling_Time == 0:
            continue
        if work.Shared_Cooling_Work_Package_Number == 'None':
            turnover_constrain = {index: True for index in days_index}
            turnover_limit[work.Work_Package_Number] = turnover_constrain
        else:
            if work.Work_Package_Number not in turnover_limit and work.Shared_Cooling_Work_Package_Number not in turnover_limit:
                turnover_constrain = {index: True for index in days_index}
                turnover_limit[work.Work_Package_Number] = turnover_constrain
                turnover_limit[work.Shared_Cooling_Work_Package_Number] = turnover_constrain
    return turnover_limit


# 给定月份生成所有的天数
def _generate_month_days(month):
    start_date = datetime.strptime(month, '%Y-%m')
    end_date = start_date + relativedelta(months=1)
    current_date = start_date
    date_list = []
    while current_date < end_date:
        date_list.append(current_date)
        current_date += relativedelta(days=1)
    return date_list


def _generate_weekend_days(lower_bound, upper_bound):
    # start_date = datetime.strptime(lower_bound, '%Y-%m')
    # end_date = start_date + relativedelta(months = 1)
    # #start_date = start_date - relativedelta(months = 1)
    # if start_date > convert_str_to_date("2024-05-01"):
    #     current_date = start_date - relativedelta(months = 2)
    # else:
    #     current_date = start_date
    date_list = []
    while lower_bound <= upper_bound:
        if lower_bound.weekday() == 5:
            date_list.append(lower_bound)
            lower_bound += relativedelta(days=7)
            continue
        lower_bound += relativedelta(days=1)
    return date_list


def _select_turnover_package(wholelife_workpackage):
    """
    从整个工作包中选择需要翻车的工作包和不需要翻车的工作包。
    
    Args:
    wholelife_workpackage: list of objects
        整个全寿命工作包，包含所有需要进行维护的工作包信息。
    
    Returns:
    turnover_package: list of objects
        需要周转件的工作包列表。
    not_turnover_package: list of objects
        不需要周转件的工作包列表。
    """
    special_list = ["1505-01", "1505-02"]
    turnover_package = [info for info in wholelife_workpackage if info.Cooling_Time != 0 and info.Work_Package_Number not in special_list]
    not_turnover_package = [info for info in wholelife_workpackage if info.Cooling_Time == 0 and info.Work_Package_Number not in special_list]
    special_package = [info for info in wholelife_workpackage if info.Work_Package_Number in special_list]
    return turnover_package, not_turnover_package, special_package
