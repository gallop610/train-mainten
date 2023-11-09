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

def month_plan(month_plan_workpackage, year_plan_workpackage, config):
    # 初始化参数
    today = convert_str_to_date(config['today'])
    current_day =today
    days_index = [today + relativedelta(days=i) for i in range(366*30)]
    month_overtake_percentage = float(config['year_overtake_percentage'])
    alpha = float(config['month_alpha'])

    sum_interval = 0
    # 初始化日期负载工时
    day_worktime_load = {index:{'all':0.0} for index in days_index}
    # 维修列车数量限制
    train_limit = {index:set() for index in days_index}
    # 检修道数量限制
    track_limit = {index:set() for index in days_index}
    # 临修道数量限制
    temp_track_limit = {index:set() for index in days_index}
    # 周转件数量限制
    turnover_limit = _day_turnover_package(year_plan_workpackage, days_index)

    # 处理8日工作包
    train_order = _get_8day_train_order(month_plan_workpackage, 8)
    cnt_index = 0

    for key in sorted(train_order.keys()):
        for train_id in train_order[key]:
            for work in month_plan_workpackage:
                # 寻找维修间隔为8的工作包，开始直接排列
                if work.Train_Number == train_id and work.Work_Package_Interval_Conversion_Value == 8:
                    work.mainten_day = []
                    start_mainten_date = work.Online_Date
                    end_mainten_date = start_mainten_date + relativedelta(days=366*30)
                    next_mainten_date = today+ relativedelta(days=cnt_index) 
                    while next_mainten_date <= end_mainten_date:
                        work.mainten_day.append(next_mainten_date)
                        # 统计天维修工时负载
                        day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
                        # 统计列车维修工时负载
                        if work.Train_Number not in day_worktime_load[next_mainten_date]:
                            day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                        day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
                        train_limit[next_mainten_date].add(work.Train_Number)# 维修的列车数量 
                        next_mainten_date = next_mainten_date + relativedelta(days=8)
                    
        cnt_index += 1

    # 处理16日工作包
    cnt_index = 8
    for key in sorted(train_order.keys()):
        for train_id in train_order[key]:
            for work in month_plan_workpackage:
                # 寻找维修间隔为16的工作包，开始直接排列
                if work.Train_Number == train_id and work.Work_Package_Interval_Conversion_Value == 16:
                    work.mainten_day = []
                    start_mainten_date = work.Online_Date
                    end_mainten_date = start_mainten_date + relativedelta(days=366*30)
                    next_mainten_date = today+ relativedelta(days=cnt_index) 
                    while next_mainten_date <= end_mainten_date:
                        work.mainten_day.append(next_mainten_date)
                        day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
                        # 统计列车维修工时负载
                        if work.Train_Number not in day_worktime_load[next_mainten_date]:
                            day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                        day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
                        train_limit[next_mainten_date].add(work.Train_Number)# 维修的列车数量
                        next_mainten_date = next_mainten_date + relativedelta(days=16)
                        
                        
        cnt_index += 1

    # 处理30日工作包
    train_order = _get_8day_train_order(month_plan_workpackage, 30)
    cnt_index = 0
    for key in sorted(train_order.keys()):
        for train_id in train_order[key]:
            for work in month_plan_workpackage:
                # 寻找维修间隔为30的工作包，开始直接排列
                if work.Train_Number == train_id and work.Work_Package_Interval_Conversion_Value == 30:
                    work.mainten_day = []
                    start_mainten_date = work.Online_Date
                    end_mainten_date = start_mainten_date + relativedelta(days=366*30)
                    next_mainten_date = today+ relativedelta(days=cnt_index) 
                    while next_mainten_date <= end_mainten_date:
                        work.mainten_day.append(next_mainten_date)
                        day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
                        # 统计列车维修工时负载
                        if work.Train_Number not in day_worktime_load[next_mainten_date]:
                            day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                        day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
                        train_limit[next_mainten_date].add(work.Train_Number)# 维修的列车数量
                        next_mainten_date = next_mainten_date + relativedelta(days=30)      
                        
        cnt_index += 1
        
    # 处理1501-01，1501-02，这两个只能周末维修，只能修一辆车，修理这辆车的这个包，其他包不维修，但可以修理其他车的其他包
    ###
     
        
    turnover_package,not_turnover_package = _select_turnover_package(year_plan_workpackage)
    for work in tqdm(turnover_package):
        work.mainten_day = []
        # 初始化基本信息
        start_mainten_date = work.Online_Date
        end_mainten_date = start_mainten_date + relativedelta(days=366*30)
        
        # 上次维修的date
        last_mainten_date = work.last_mainten_time
        # 维修间隔
        interval_days = int(work.Work_Package_Interval_Conversion_Value)
        
        # 根据历史维修信息，计算下一次维修的日期
        next_mainten_date = last_mainten_date + relativedelta(days=interval_days)
        # 如果下次维修的日期小于当前日期，说明已经欠修，需要将当前日期置为第一次维修
        if next_mainten_date < current_day:
            next_mainten_date = current_day
        for month in work.mainten_month:
            range_days = _generate_month_days(month)
            seed = work.Work_Package_Number
            random.seed(seed)

            if work.Cooling_Time == 7:
                initial_number = random.randint(1, 7)
                result = [initial_number + i * 7 for i in range(4)]
                range_days = [info for info in range_days if info.day in result]
            elif work.Cooling_Time == 14:
                initial_number = random.randint(1, 14)
                result = [initial_number + i * 14 for i in range(2)]
                range_days = [info for info in range_days if info.day in result]
            elif work.Cooling_Time == 25:
                initial_number = random.randint(1, 28)
                result = [initial_number]
                range_days = [info for info in range_days if info.day in result]

            min_day_range = _select_less_day_turnover_worktime_load(day_worktime_load, range_days, next_mainten_date, alpha)

            flag_min_day = False
            for min_day in min_day_range:
                # 判断周转件是否符合
                if turnover_limit[work.Work_Package_Number][min_day] == False:
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
            # 增加列车数量，检修道数量
            train_limit[next_mainten_date].add(work.Train_Number)
            
            work.mainten_day.append(next_mainten_date)
            day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
            # 统计列车维修工时负载
            if work.Train_Number not in day_worktime_load[next_mainten_date]:
                day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
            day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
            next_mainten_date = next_mainten_date + relativedelta(days=interval_days)
    for work in tqdm(not_turnover_package):
        work.mainten_day = []
        # 初始化基本信息
        start_mainten_date = work.Online_Date
        end_mainten_date = start_mainten_date + relativedelta(days=366*30)
        
        # 上次维修的date
        last_mainten_date = work.last_mainten_time
        # 维修间隔
        interval_days = int(work.Work_Package_Interval_Conversion_Value)
        
        # 根据历史维修信息，计算下一次维修的日期
        next_mainten_date = last_mainten_date + relativedelta(days=interval_days)
        # 如果下次维修的日期小于当前日期，说明已经欠修，需要将当前日期置为第一次维修
        if next_mainten_date < current_day:
            next_mainten_date = current_day
        
        # 由于0502-01包在年计划中会有一个月出现多次的情况，不符合实际，因此要过滤掉多余的月份
        if work.Work_Package_Number == '0502-01':
            mainten_month = []
            for month in work.mainten_month:
                if month not in mainten_month:
                    mainten_month.append(month)
            work.mainten_month = mainten_month
        for month in work.mainten_month:
            float_range_ub = interval_days*0.05
            upper_bound = next_mainten_date + relativedelta(days=int(float_range_ub))

            if work.Work_Package_Interval_Conversion_Value >90:
                float_range_lb = interval_days*0.1
            else:
                float_range_lb = interval_days*month_overtake_percentage
            lower_bound = next_mainten_date - relativedelta(days=int(float_range_lb))

            # 判断上界和下界的日期会不会超出边界，满足调节则置为边界值
            if upper_bound >= end_mainten_date:
                upper_bound = end_mainten_date - relativedelta(days=1)

            if lower_bound < current_day:
                lower_bound = current_day
            
                # 按年计划的月份生成日期范围
            range_days = _generate_month_days(month)
            range_days = [day for day in range_days if day <= upper_bound and day >= lower_bound]

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

            min_day = _select_less_day_worktime_load(work, day_worktime_load, range_days, next_mainten_date, alpha, train_limit,current_day)
            sum_interval += (min_day- next_mainten_date).days
            next_mainten_date = min_day

            # 确定当前维修日期之后，将当前维修日期添加到工作包维修日期列表，日期工时负载增加，并获取下次维修日期
            work.mainten_day.append(next_mainten_date)
            day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
            # 统计列车维修工时负载
            if work.Train_Number not in day_worktime_load[next_mainten_date]:
                day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
            day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
            train_limit[next_mainten_date].add(work.Train_Number)
                
            next_mainten_date = next_mainten_date + relativedelta(days=interval_days)

    # _draw(day_worktime_load, train_limit, days_index)
    # exit(-1)
    return turnover_package + not_turnover_package + month_plan_workpackage

def _select_less_day_turnover_worktime_load(day_worktime_load, range_days, next_mainten_date, alpha):
    all = {}
    
    for i in range_days:
        all[i] = day_worktime_load[i]['all'] + abs((i-next_mainten_date).days) * alpha
    
    return [k for k, v in sorted(all.items(), key=lambda item: item[1])]


def _select_less_day_worktime_load(work, day_worktime_load, day_range, next_mainten_date, alpha, train_limit,current_day):
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
    # 优先级更高
    
    
    all = {}
    for i in day_range:
        if day_worktime_load[i]['all'] > 200:
            continue
        if work.Train_Number in train_limit[i]:
            all[i] = 1.5*day_worktime_load[i]['all'] + abs((i-next_mainten_date).days) * alpha
    
    if all != {}:
        return min(all, key=all.get)
            
    all = {}
    for i in day_range:
        if  day_worktime_load[i]['all'] > 180:
            continue
        if work.Train_Number not in train_limit[i] and len(train_limit[i])<7:
            all[i] = 1.5*day_worktime_load[i]['all'] + abs((i-next_mainten_date).days) * alpha
    if all != {}:
        return min(all, key=all.get)
    
    all = {}
    start_day = day_range[0]
    end_day = day_range[-1]
    day_range = gen_all_days_datetime(max(start_day - relativedelta(days=3),current_day),end_day + relativedelta(days=3))
    for i in day_range:
        if work.Train_Number in train_limit[i]:
            flag_train_in_today = 1
        else:
            flag_train_in_today = -1

        if len(train_limit[i]) >= 7 and flag_train_in_today == -1:
            all[i] = day_worktime_load[i]['all'] + abs((i-next_mainten_date).days) * alpha + len(train_limit[i])*10000
        else:
            all[i] = 10*day_worktime_load[i]['all'] + abs((i-next_mainten_date).days) * alpha - flag_train_in_today * 20
    return min(all, key=all.get)
    


def choose_stocktrack(train_list):
    return None
    


def _day_turnover_package(workpackage, days_index):
    turnover_limit = {}
    for work in workpackage:
        if work.Cooling_Time == 0:
            continue
        if work.Shared_Cooling_Work_Package_Number == 'None':
            turnover_constrain = {index:True for index in days_index}
            turnover_limit[work.Work_Package_Number] = turnover_constrain
        else:
            if work.Work_Package_Number not in turnover_limit and work.Shared_Cooling_Work_Package_Number not in turnover_limit:
                turnover_constrain = {index:True for index in days_index}
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

def _draw(day_worktime_load, train_limit, index):
    t1 =[]
    t2 =[]
    for info in sorted(index)[:365]:
        t1.append(day_worktime_load[info]['all'])
        t2.append(len(train_limit[info]))
    plt.plot(t1, label='work time', color='r')
    y_ticks = [160,180,200,220,240]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.savefig('./results/month_worktime_load.png')
    
    
    plt.clf()
    plt.plot(t2, label='train number', color='b')
    y_ticks = [2,3,4,7, 14]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.savefig('./results/train_number.png')
    
# 获取8日工作包的列车顺序
def _get_8day_train_order(workpackage, days_interval):
    tmp = []
    for work in workpackage:
        if work.Work_Package_Interval_Conversion_Value == days_interval:
            tmp.append(work)
    t = []
    for work in tmp:
        if work.Work_Package_Number == tmp[0].Work_Package_Number:
            t.append(work)
    t.sort(key=lambda x: x.last_mainten_time, reverse=False)
    train_order = {}
    for info in t:
        if info.last_mainten_time not in train_order:
            train_order[info.last_mainten_time] = [info.Train_Number]
        else:
            train_order[info.last_mainten_time].append(info.Train_Number)
    return train_order

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
    turnover_package = [info for info in wholelife_workpackage if info.Cooling_Time != 0]
    not_turnover_package = [info for info in wholelife_workpackage if info.Cooling_Time == 0]
    return turnover_package, not_turnover_package