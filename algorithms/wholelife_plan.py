from SchedulingEntities import *
import numpy as np
import copy
from utils import *
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pdb
import math

def wholelife_plan(wholelife_workpackage, config):
    """
    Generate a whole life plan for a given set of work packages and configuration.

    Args:
        all_workpackage (list): A list of WorkPackage objects.
        config (dict): A dictionary containing configuration parameters.

    Returns:
        A list of ScheduledWorkPackage objects representing the whole life plan.
    """
    
    # 初始化参数
    today = convert_str_to_date(config['today'])
    current_quarter = convert_day_to_quarter(today)
    over_repair_restrictions_on_turnover = int(config['over_repair_restrictions_on_turnover'])
    over_repair_restrictions_on_not_turnover = float(config['over_repair_restrictions_on_not_turnover'])
    
    # 初始化季度负载工时
    quarter_list = gen_quarter_120(current_quarter)
    quarter_worktime_load = {}
    for quarter in quarter_list:
        quarter_worktime_load[quarter] = 0
    
    # # 筛选含有周转件约束的工作包和不含周转件约束的工作包
    turnover_package, not_turnover_package = _select_turnover_package(wholelife_workpackage)
    
    # 统计同一时间上线的列车数量，以时间作为key，列车数量作为value
    train_cnt = _count_num_trains_on_sametime(turnover_package)
    
    # 排序含有周转件约束的工作包
    turnover_package.sort(key=lambda x: (x.Online_Date, x.Work_Package_Interval_Conversion_Value, x.Cooling_Time, x.Train_Number, x.Work_Package_Number), reverse=False)
    
    # 生成季度周转件约束
    quarter_turnover_constraint = _quarter_turnover_constraint(turnover_package, quarter_list)
    
    # 含有周转件工作包的全寿命计划
    for work in turnover_package:
        work.mainten_quarter = []
        # 初始化基本信息
        start_mainten_quarter = convert_day_to_quarter(work.Online_Date)
        end_mainten_quarter = add_quarters(start_mainten_quarter, 120)
        
        # 上次维修的季度
        last_mainten_quarter = convert_day_to_quarter(work.last_mainten_time)
        # 维修间隔的季度表示
        interval_quarter = int(work.Work_Package_Interval_Conversion_Value/90)
        
        # 根据历史维修信息，计算下一次维修的季度
        next_mainten_quarter = add_quarters(last_mainten_quarter, interval_quarter)
        
        # 如果下一次标准维修的季度小于当前季度，则将下一次维修季度设置为当前季度
        if compare_quarters(next_mainten_quarter, current_quarter) == 1: # next_mainten_quarter < current_quarter
            next_mainten_quarter = current_quarter
        
        while compare_quarters(next_mainten_quarter, end_mainten_quarter) == 1:
            float_range_ub = interval_quarter*0.05
            # 以一定的概率将下一次维修季度向后推迟一个季度，具体取决于维修间隔的季度
            upper_bound = add_quarters(next_mainten_quarter, int(float_range_ub))
            if random.random() < float_range_ub-int(float_range_ub):
                upper_bound = add_quarters(upper_bound, 1)
            if compare_quarters(upper_bound, end_mainten_quarter) != 1:
                upper_bound = add_quarters(end_mainten_quarter, -1)
                
            if not isinstance(work.Shared_Cooling_Work_Package_Number, str) and np.isnan(work.Shared_Cooling_Work_Package_Number):
                float_range_lb = math.ceil(len(train_cnt[work.Online_Date])/int(90/work.Cooling_Time))+over_repair_restrictions_on_turnover
            else:
                float_range_lb = math.ceil(2*len(train_cnt[work.Online_Date])/int(90/work.Cooling_Time))+over_repair_restrictions_on_turnover
            
            lower_bound = add_quarters(next_mainten_quarter, -int(float_range_lb))
            if random.random() < float_range_lb-int(float_range_lb)-1e-9:
                lower_bound = add_quarters(lower_bound, -1)
                
            if compare_quarters(lower_bound, current_quarter) == 1:
                lower_bound = current_quarter
                upper_bound = add_quarters(current_quarter, int(math.ceil(float_range_lb+float_range_ub)))
            
            # 找到符合周转件要求且工时负载最小的季度
            range = gen_all_quarters(lower_bound, upper_bound)
            while True:
                if range == []:
                    if compare_quarters(lower_bound, current_quarter) == 0:
                        upper_bound = add_quarters(upper_bound,1)
                        range = gen_all_quarters(upper_bound, upper_bound)
                    else:
                        lower_bound = add_quarters(lower_bound,-1)
                        range = gen_all_quarters(lower_bound, lower_bound)
                    continue
                    
                min_worktime_load_quarter = _select_less_quarter_worktime_load(quarter_worktime_load, range, next_mainten_quarter)
                if quarter_turnover_constraint[work.Work_Package_Number][min_worktime_load_quarter] > 0:
                    next_mainten_quarter = min_worktime_load_quarter
                    break
                else:
                    range.remove(min_worktime_load_quarter)
            # 对应周转件约束数量减一，记录维修日期
            quarter_turnover_constraint[work.Work_Package_Number][next_mainten_quarter] -= 1
            work.mainten_quarter.append(next_mainten_quarter)
            # 季度维修工时负载
            quarter_worktime_load[next_mainten_quarter] += work.Work_Package_Person_Day
            # 更新下一次维修季度
            next_mainten_quarter = add_quarters(next_mainten_quarter, interval_quarter)
    
    work_load_quarter = list(quarter_worktime_load.values())



    # 添加标题和标签
    
    # 不含周转件工作包的全寿命计划
    for work in not_turnover_package:
        work.mainten_quarter = []
        # 初始化基本信息
        start_mainten_quarter = convert_day_to_quarter(work.Online_Date)
        end_mainten_quarter = add_quarters(start_mainten_quarter, 120)
        
        # 上次维修的季度
        last_mainten_quarter = convert_day_to_quarter(work.last_mainten_time)
        # 维修间隔的季度表示
        interval_quarter = int(work.Work_Package_Interval_Conversion_Value/90)
        
        # 根据历史维修信息，计算下一次维修的季度
        next_mainten_quarter = add_quarters(last_mainten_quarter, interval_quarter)
        
        # 如果下一次标准维修的季度小于当前季度，则将下一次维修季度设置为当前季度
        if compare_quarters(next_mainten_quarter, current_quarter) == 1: # next_mainten_quarter < current_quarter
            next_mainten_quarter = current_quarter
        
        while compare_quarters(next_mainten_quarter, end_mainten_quarter) == 1:
            float_range_ub = interval_quarter*0.05
            # 以一定的概率将下一次维修季度向后推迟一个季度，具体取决于维修间隔的季度
            upper_bound = add_quarters(next_mainten_quarter, int(float_range_ub))
            if random.random() < float_range_ub-int(float_range_ub):
                upper_bound = add_quarters(upper_bound, 1)
            if compare_quarters(upper_bound, end_mainten_quarter) != 1:
                upper_bound = add_quarters(end_mainten_quarter, -1)
                
            float_range_lb = interval_quarter*over_repair_restrictions_on_not_turnover
            lower_bound = add_quarters(next_mainten_quarter, -int(float_range_lb))
            if random.random() < float_range_lb-int(float_range_lb):
                lower_bound = add_quarters(lower_bound, -1)
                
            if compare_quarters(lower_bound, current_quarter) == 1:
                lower_bound = current_quarter
            
            range = gen_all_quarters(lower_bound, upper_bound)
            min_worktime_load_quarter = _select_less_quarter_worktime_load(quarter_worktime_load, range, next_mainten_quarter)
            next_mainten_quarter = min_worktime_load_quarter
            work.mainten_quarter.append(next_mainten_quarter)
            # 季度维修工时负载
            quarter_worktime_load[next_mainten_quarter] += work.Work_Package_Person_Day
            # 更新下一次维修季度
            next_mainten_quarter = add_quarters(next_mainten_quarter, interval_quarter)

    return turnover_package+not_turnover_package

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

def _count_num_trains_on_sametime(turnover_package):
    """
    统计同一时间上线的列车数量

    Args:
        turnover_package (list): A list of WorkPackage objects that require turnover parts.

    Returns:
        A dictionary where the keys are the online dates and the values are sets of train numbers that are online at the same time.
    """
    train_cnt = {}
    for work in turnover_package:
        if work.Online_Date not in train_cnt:
            train_cnt[work.Online_Date] = set()
        train_cnt[work.Online_Date].add(work.Train_Number)
    return train_cnt

def _quarter_turnover_constraint(turnover_package, quarter_list):
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
        if not isinstance(work.Shared_Cooling_Work_Package_Number,str) and np.isnan(work.Shared_Cooling_Work_Package_Number):
            turnover_quarter_constrain = {}
            for quarter in quarter_list:
                turnover_quarter_constrain[quarter] = int(30/work.Cooling_Time)*3
            turnover_cd[work.Work_Package_Number] = turnover_quarter_constrain
        else:
            if work.Work_Package_Number not in turnover_cd and work.Shared_Cooling_Work_Package_Number not in turnover_cd:
                turnover_quarter_constrain = {}
                for quarter in quarter_list:
                    turnover_quarter_constrain[quarter] = int(30/work.Cooling_Time)*3
                turnover_cd[work.Work_Package_Number] = turnover_quarter_constrain
                turnover_cd[work.Shared_Cooling_Work_Package_Number] = turnover_quarter_constrain
    return turnover_cd

def _select_less_quarter_worktime_load(quarter_worktime_load, range, next_mainten_quarter):
    # range = gen_all_quarters(lb, ub)
    index = '2000Q1'
    value = float('inf')
    for i in range:
        if value >= quarter_worktime_load[i] and quarter_difference(i, next_mainten_quarter) < quarter_difference(index, next_mainten_quarter):
            value = quarter_worktime_load[i]
            index = i
    return index