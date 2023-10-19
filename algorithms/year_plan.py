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

def year_plan(year_workpackage, wholelife_workpackage, config):
    # 初始化参数
    today = convert_str_to_date(config['today'])
    current_month = convert_day_to_month(today)
    year_overtake_percentage = float(config['year_overtake_percentage'])
    alpha = float(config['month_alpha'])
    
    # 初始化月负载工时
    sum_interval = 0
    month_list = gen_month_360(current_month)
    month_worktime_load = {}
    for month in month_list:
        month_worktime_load[month] = 0
        
    # 初始化季度的周转件约束
    # turnover_package, not_turnover_package = _select_turnover_package(wholelife_workpackage)   
    month_turnover_constraint = _month_turnover_constraint(wholelife_workpackage, month_list)

        
    # 首先排产全寿命计划工作包
    for work in wholelife_workpackage:
        # print('1',work.Work_Package_Number)
        if not np.isnan(work.Cooling_Time):
            flag_tunover = True
        else:
            flag_tunover = False
        
        work.mainten_month = []
        # 上次维修的月份
        last_mainten_month = convert_day_to_month(work.last_mainten_time)
        # 维修间隔的月份表示
        interval_month = int(work.Work_Package_Interval_Conversion_Value/30)
        
        # 根据历史维修信息，计算下一次维修的月份
        next_mainten_month = add_months(last_mainten_month, interval_month)
        if compare_months(next_mainten_month, current_month) == 1:
            next_mainten_month = current_month
        
        for quarter in work.mainten_quarter:
            # 在该维修季度中选择一个工时最低，间隔最小的月份
            float_range_ub = interval_month*0.05
            upper_bound = add_months(next_mainten_month, int(float_range_ub))
            if random.random()/3 < float_range_ub - int(float_range_ub)-1e-9:
                upper_bound = add_months(next_mainten_month, int(float_range_ub)+1)
            
            float_range_lb = interval_month*year_overtake_percentage
            # 以一定的概率将下一次维修月份向前推迟一个季度，具体取决于维修间隔的月份
            lower_bound = add_months(next_mainten_month, -int(float_range_lb))
            if random.random()/3 < float_range_lb - int(float_range_lb)-1e-9:
                lower_bound = add_months(lower_bound, -1)
            if compare_months(lower_bound, current_month) != -1:
                lower_bound = current_month
        
            range_months = gen_all_months_on_quarter(quarter)
            range_months = [month for month in range_months if compare_months(month, upper_bound)!=-1 and compare_months(month, lower_bound)!=1]
            if range_months == []:
                range_months = gen_all_months_on_quarter(quarter)[:1]
            if flag_tunover:
                # 如果需要周转件，那么需要考虑周转件的约束
                cnt = -1
                flag_cnt = -1
                while True:
                    if range_months == []:
                        if compare_quarters(add_quarters(quarter, cnt), convert_day_to_quarter(today))==1:
                            flag_cnt = 1
                            cnt = 1    
                        range_months = gen_all_months_on_quarter(add_quarters(quarter, cnt))
                        range_months = [month for month in range_months if compare_months(month, current_month)!=1]
                        cnt += flag_cnt
                    else:
                        min_month = _select_less_month_worktime_load(month_worktime_load, sum_interval, range_months, work.Work_Package_Person_Day, next_mainten_month, alpha)
                        if month_turnover_constraint[work.Work_Package_Number][min_month] > 0:
                            sum_interval += month_difference(min_month, next_mainten_month)
                            next_mainten_month = min_month
                            break
                        else:
                            range_months.remove(min_month)
                month_turnover_constraint[work.Work_Package_Number][next_mainten_month] -= 1
                work.mainten_month.append(next_mainten_month)
                month_worktime_load[next_mainten_month] += work.Work_Package_Person_Day
                next_mainten_month = add_months(next_mainten_month, interval_month)
            else:
                # 选择最佳的月份
                # pdb.set_trace()
                # if work.Train_Number == 1 and work.Work_Package_Number =='0204-01':
                #     print(work.mainten_quarter)
                #     exit(0)
                #     print(quarter, range_months)
                if interval_month in range(1, 60):
                    min_month = _select_less_month_worktime_load(month_worktime_load, sum_interval, range_months, work.Work_Package_Person_Day, next_mainten_month, 400)
                else:  
                    min_month = _select_less_month_worktime_load(month_worktime_load, sum_interval, range_months, work.Work_Package_Person_Day, next_mainten_month, alpha)
                sum_interval += month_difference(min_month, next_mainten_month)
                next_mainten_month = min_month
                work.mainten_month.append(next_mainten_month)
                month_worktime_load[next_mainten_month] += work.Work_Package_Person_Day
                next_mainten_month = add_months(next_mainten_month, interval_month)
        
    for work in year_workpackage:
        # print('2',work.Work_Package_Number)
        work.mainten_month = []
        # 初始化基本信息
        start_mainten_month = convert_day_to_month(work.Online_Date)
        end_mainten_month = add_months(start_mainten_month, 360)
        # 上次维修的月份
        last_mainten_month = convert_day_to_month(work.last_mainten_time)
        # 维修间隔的月份表示
        interval_month = int(work.Work_Package_Interval_Conversion_Value/30)
        # 根据历史维修信息，计算下一次维修的月份
        next_mainten_month = add_months(last_mainten_month, interval_month)
        
        # 如果下一次标准维修的月份小于当前月份，则将下一次维修月份设置为当前月份
        if compare_months(next_mainten_month, current_month) == 1:
            next_mainten_month = current_month
        
        while compare_months(next_mainten_month, end_mainten_month) == 1:
            # print(next_mainten_month,end_mainten_month, interval_month)
            float_range_ub = interval_month*0.05
            # 以一定的概率将下一次维修月份向后推迟一个季度，具体取决于维修间隔的月份
            upper_bound = add_months(next_mainten_month, int(float_range_ub))
            if random.random()/3 < float_range_ub - int(float_range_ub)-1e-9:
                upper_bound = add_months(upper_bound, 1)
            if compare_months(upper_bound, end_mainten_month) != 1:
                upper_bound = add_months(end_mainten_month, -1)
            
            float_range_lb = interval_month*year_overtake_percentage
            # 以一定的概率将下一次维修月份向前推迟一个季度，具体取决于维修间隔的月份
            lower_bound = add_months(next_mainten_month, -int(float_range_lb))
            if random.random()/3 < float_range_lb - int(float_range_lb)-1e-9:
                lower_bound = add_months(lower_bound, -1)
            if compare_months(lower_bound, current_month) != -1:
                lower_bound = current_month
            
            # print('upper_bound',upper_bound, 'lower_bound',lower_bound)
            
            range_months = gen_all_months(lower_bound, upper_bound)
            # print('range',range)
            # 选择最佳的月份
            min_month = _select_less_month_worktime_load(month_worktime_load, sum_interval, range_months, work.Work_Package_Person_Day, next_mainten_month, alpha)
            # print('min_month',min_month)
            sum_interval += month_difference(min_month, next_mainten_month)
            next_mainten_month = min_month
            work.mainten_month.append(next_mainten_month)
            month_worktime_load[next_mainten_month] += work.Work_Package_Person_Day
            # print('*', next_mainten_month)
            next_mainten_month = add_months(next_mainten_month, interval_month)
            # print('*', next_mainten_month)

    return wholelife_workpackage + year_workpackage


def _month_turnover_constraint(turnover_package, month_list):
    """
    根据给定的周转包和季度列表，计算每个工作包在每个季度内的周转次数限制。
    
    Args:
        turnover_package: 周转包，包含多个工作包。
        quarter_list: 季度列表，包含多个季度。
    
    Returns:
        turnover_cd: 字典类型，包含每个工作包在每个季度内的周转次数限制。
    """
    turnover_cd = {}
    for work in turnover_package:
        if np.isnan(work.Cooling_Time):
            continue
        if not isinstance(work.Shared_Cooling_Work_Package_Number,str) and np.isnan(work.Shared_Cooling_Work_Package_Number):
            turnover_month_constrain = {}
            for month in month_list:
                turnover_month_constrain[month] = int(30/work.Cooling_Time)
            turnover_cd[work.Work_Package_Number] = turnover_month_constrain
        else:
            if work.Work_Package_Number not in turnover_cd and work.Shared_Cooling_Work_Package_Number not in turnover_cd:
                turnover_month_constrain = {}
                for month in month_list:
                    turnover_month_constrain[month] = int(30/work.Cooling_Time)
                turnover_cd[work.Work_Package_Number] = turnover_month_constrain
                turnover_cd[work.Shared_Cooling_Work_Package_Number] = turnover_month_constrain
    return turnover_cd

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
    
    turnover_package = [info for info in wholelife_workpackage if not np.isnan(info.Cooling_Time)]
    not_turnover_package = [info for info in wholelife_workpackage if np.isnan(info.Cooling_Time)]
    return turnover_package, not_turnover_package

def _select_less_month_worktime_load(month_worktime_load,sum_interval, month_range,worktime, next_mainten_month,alpha):
    """
    从月负载工时中选择最小的月份。
    
    Args:
        month_worktime_load: 字典类型，包含每个月份的工时负载。
        month_range: list of str
            月份列表，包含所有的月份。
        next_mainten_quarter: str
            下次维修的季度。
    
    Returns:
        min_month: str
            工时负载最小的月份。
    """
    all = {}
    for i in month_range:
        all[i] = (month_worktime_load[i]+worktime)+(sum_interval+month_difference(i, next_mainten_month))*alpha
    min_key = min(all, key=all.get)
    return min_key