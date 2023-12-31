from SchedulingEntities import *
import numpy as np
import copy
from utils import *
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pdb
import math
from tqdm import tqdm


def wholelife_plan(wholelife_workpackage, config):
    '''
    全寿命计划算法

    Args:
        wholelife_workpackage: 全寿命计划包含所有工作包的列表
        config: 算法的配置信息

    Returns:
        排班后的全寿命算法
    '''

    # 初始化参数
    today = convert_str_to_date(config['today'])
    alpha = float(config['whole_alpha'])
    current_quarter = convert_day_to_quarter(today)
    turnover_overtake_quarter = int(config['turnover_overtake_quarter'])
    wholelife_overtake_percentage = float(config['wholelife_overtake_percentage'])

    # 初始化季度负载工时,维修间隔
    sum_interval = 0
    quarter_list = gen_quarter_120(current_quarter)
    quarter_worktime_load = {index: 0 for index in quarter_list}

    # # 筛选含有周转件约束的工作包和不含周转件约束的工作包
    turnover_package, not_turnover_package = _select_turnover_package(wholelife_workpackage)

    # 统计同一时间上线的列车数量，以时间作为key，列车数量作为value
    train_cnt = _count_num_trains_on_sametime(turnover_package)

    # 排序含有周转件约束的工作包
    turnover_package.sort(key=lambda x: (x.Online_Date, x.Work_Package_Interval_Conversion_Value, x.Cooling_Time, x.Train_Number, x.Work_Package_Number), reverse=False)

    # 生成季度周转件约束
    quarter_turnover_constraint = _quarter_turnover_constraint(turnover_package, quarter_list)

    # 含有周转件工作包的全寿命计划
    print('正在处理全寿命计划的周转件工作包...')
    for work in tqdm(turnover_package):
        work.mainten_quarter = []
        # 初始化基本信息
        start_mainten_quarter = convert_day_to_quarter(work.Online_Date)
        end_mainten_quarter = add_quarters(start_mainten_quarter, 120)

        # 上次维修的季度
        last_mainten_quarter = convert_day_to_quarter(work.last_mainten_time)
        # 维修间隔的季度表示
        interval_quarter = int(work.Work_Package_Interval_Conversion_Value / 90)

        # 根据历史维修信息，计算下一次维修的季度
        next_mainten_quarter = add_quarters(last_mainten_quarter, interval_quarter)

        # 如果下一次标准维修的季度小于当前季度，则将下一次维修季度设置为当前季度
        if compare_quarters(next_mainten_quarter, current_quarter) == 1:  # next_mainten_quarter < current_quarter
            next_mainten_quarter = current_quarter

        while compare_quarters(next_mainten_quarter, end_mainten_quarter) == 1:
            float_range_ub = interval_quarter * 0.05

            upper_bound = add_quarters(next_mainten_quarter, int(float_range_ub))

            if compare_quarters(upper_bound, end_mainten_quarter) != 1:
                upper_bound = add_quarters(end_mainten_quarter, -1)

            if work.Shared_Cooling_Work_Package_Number == 'None':
                float_range_lb = math.ceil(len(train_cnt[work.Online_Date]) / int(90 / work.Cooling_Time)) + turnover_overtake_quarter
            else:
                float_range_lb = math.ceil(2 * len(train_cnt[work.Online_Date]) / int(90 / work.Cooling_Time)) + turnover_overtake_quarter

            lower_bound = add_quarters(upper_bound, -int(float_range_lb))

            if compare_quarters(lower_bound, current_quarter) == 1:
                lower_bound = current_quarter
                upper_bound = add_quarters(current_quarter, int(math.ceil(float_range_lb + float_range_ub)))

            # 找到符合周转件要求且工时负载最小的季度
            range = gen_all_quarters(lower_bound, upper_bound)
            while True:
                if range == []:
                    if compare_quarters(lower_bound, current_quarter) == 0:
                        upper_bound = add_quarters(upper_bound, 1)
                        range = gen_all_quarters(upper_bound, upper_bound)
                    else:
                        lower_bound = add_quarters(lower_bound, -1)
                        range = gen_all_quarters(lower_bound, lower_bound)
                    continue

                min_worktime_load_quarter = _select_less_quarter_worktime_load(quarter_worktime_load, sum_interval, range, work.Work_Package_Person_Day, next_mainten_quarter, 4.5 * alpha)
                if quarter_turnover_constraint[work.Work_Package_Number][min_worktime_load_quarter] > 0:
                    sum_interval += quarter_difference(next_mainten_quarter, min_worktime_load_quarter)
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

    # 排序
    not_turnover_package.sort(key=lambda x: (x.Work_Package_Interval_Conversion_Value, x.Online_Date, x.Cooling_Time, x.Train_Number, x.Work_Package_Number), reverse=False)
    # 不含周转件工作包的全寿命计划
    print('正在处理全寿命计划的非周转件工作包...')
    for work in tqdm(not_turnover_package):
        work.mainten_quarter = []
        # 初始化基本信息
        start_mainten_quarter = convert_day_to_quarter(work.Online_Date)
        end_mainten_quarter = add_quarters(start_mainten_quarter, 120)

        # 上次维修的季度
        last_mainten_quarter = convert_day_to_quarter(work.last_mainten_time)
        # 维修间隔的季度表示
        interval_quarter = int(work.Work_Package_Interval_Conversion_Value / 90)

        # 根据历史维修信息，计算下一次维修的季度
        next_mainten_quarter = add_quarters(last_mainten_quarter, int(work.Work_Package_Interval_Conversion_Value * 1.05 / 90))

        # 如果下一次标准维修的季度小于当前季度，则将下一次维修季度设置为当前季度
        if compare_quarters(next_mainten_quarter, current_quarter) == 1:  # next_mainten_quarter < current_quarter
            # sum_interval += quarter_difference(next_mainten_quarter, current_quarter)
            next_mainten_quarter = current_quarter
            work.mainten_quarter.append(next_mainten_quarter)
            # 季度维修工时负载
            quarter_worktime_load[next_mainten_quarter] += work.Work_Package_Person_Day
            # 更新下一次维修季度
            next_mainten_quarter = add_quarters(next_mainten_quarter, interval_quarter)
        else:
            next_mainten_quarter = add_quarters(last_mainten_quarter, int(work.Work_Package_Interval_Conversion_Value / 90))

        while compare_quarters(next_mainten_quarter, end_mainten_quarter) == 1:
            float_range_ub = interval_quarter * 0.05
            # 以一定的概率将下一次维修季度向后推迟一个季度，具体取决于维修间隔的季度
            upper_bound = add_quarters(next_mainten_quarter, int(float_range_ub))

            if compare_quarters(upper_bound, end_mainten_quarter) != 1:
                upper_bound = add_quarters(end_mainten_quarter, -1)

            float_range_lb = interval_quarter * wholelife_overtake_percentage
            lower_bound = add_quarters(next_mainten_quarter, -int(float_range_lb))

            if compare_quarters(lower_bound, current_quarter) == 1:
                lower_bound = current_quarter

            range = gen_all_quarters(lower_bound, upper_bound)
            if interval_quarter in [2, 4]:
                min_worktime_load_quarter = _select_less_quarter_worktime_load(quarter_worktime_load, sum_interval, range, work.Work_Package_Person_Day, next_mainten_quarter, 800)
            else:
                min_worktime_load_quarter = _select_less_quarter_worktime_load(quarter_worktime_load, sum_interval, range, work.Work_Package_Person_Day, next_mainten_quarter, alpha)
            sum_interval += quarter_difference(next_mainten_quarter, min_worktime_load_quarter)
            next_mainten_quarter = min_worktime_load_quarter
            work.mainten_quarter.append(next_mainten_quarter)
            # 季度维修工时负载
            quarter_worktime_load[next_mainten_quarter] += work.Work_Package_Person_Day
            # 更新下一次维修季度
            next_mainten_quarter = add_quarters(next_mainten_quarter, interval_quarter)

    return turnover_package + not_turnover_package


def wholelife_plan_contract(wholelife_workpackage_contract, config):
    '''
    全寿命计划算法(委外工作包)

    Args:
        wholelife_workpackage_contract: 全寿命计划包含所有委外工作包的列表
        config: 算法的配置信息

    Returns:
        排班后的全寿命委外工作包
    '''

    # 初始化参数
    today = convert_str_to_date(config['today'])
    current_quarter = convert_day_to_quarter(today)
    turnover_overtake_quarter = int(config['turnover_overtake_quarter'])
    wholelife_overtake_percentage = float(config['wholelife_overtake_percentage'])

    # 初始化维修季度、维修间隔
    sum_interval = 0
    quarter_list = gen_quarter_120(current_quarter)

    # 全寿命计划的周转件委外工作包
    print('正在处理全寿命计划的周转件委外工作包...')

    contract_package = wholelife_workpackage_contract
    
    # 筛选含有周转件约束的工作包和不含周转件约束的工作包
    turnover_package, not_turnover_package = _select_turnover_package(contract_package)

    # 排序含有周转件约束的工作包
    turnover_package.sort(key=lambda x: (x.Online_Date, x.Work_Package_Interval_Conversion_Value, x.Cooling_Time, x.Train_Number, x.Work_Package_Number), reverse=False)
    
    # 统计同一时间上线的列车数量，以时间作为key，列车数量作为value
    train_cnt = _count_num_trains_on_sametime(turnover_package)
    
    # 生成季度周转件约束
    quarter_turnover_constraint = _quarter_turnover_constraint(turnover_package, quarter_list)
    
    for work in tqdm(turnover_package):
        work.mainten_quarter = []
        # 初始化基本信息
        start_mainten_quarter = convert_day_to_quarter(work.Online_Date)
        end_mainten_quarter = add_quarters(start_mainten_quarter, 120)

        # 上次维修的季度
        last_mainten_quarter = convert_day_to_quarter(work.last_mainten_time)
        # 维修间隔的季度表示
        interval_quarter = int(work.Work_Package_Interval_Conversion_Value / 90)

        # 根据历史维修信息，计算下一次维修的季度
        next_mainten_quarter = add_quarters(last_mainten_quarter, interval_quarter)
        
        # 如果下一次标准维修的季度小于当前季度，则将下一次维修季度设置为当前季度
        if compare_quarters(next_mainten_quarter, current_quarter) == 1:  # next_mainten_quarter < current_quarter
            next_mainten_quarter = current_quarter
    
        while compare_quarters(next_mainten_quarter, end_mainten_quarter) == 1:
            float_range_ub = interval_quarter * 0.05

            upper_bound = add_quarters(next_mainten_quarter, int(float_range_ub))

            if compare_quarters(upper_bound, end_mainten_quarter) != 1:
                upper_bound = add_quarters(end_mainten_quarter, -1)

            if work.Shared_Cooling_Work_Package_Number == 'None':
                float_range_lb = math.ceil(len(train_cnt[work.Online_Date]) / int(90 / work.Cooling_Time)) + turnover_overtake_quarter
            else:
                float_range_lb = math.ceil(2 * len(train_cnt[work.Online_Date]) / int(90 / work.Cooling_Time)) + turnover_overtake_quarter

            lower_bound = add_quarters(upper_bound, -int(float_range_lb))

            if compare_quarters(lower_bound, current_quarter) == 1:
                lower_bound = current_quarter
                upper_bound = add_quarters(current_quarter, int(math.ceil(float_range_lb + float_range_ub)))

            # 找到符合周转件要求且工时负载最小的季度
            range = gen_all_quarters(lower_bound, upper_bound)
            while True:
                if range == []:
                    if compare_quarters(lower_bound, current_quarter) == 0:
                        upper_bound = add_quarters(upper_bound, 1)
                        range = gen_all_quarters(upper_bound, upper_bound)
                    else:
                        lower_bound = add_quarters(lower_bound, -1)
                        range = gen_all_quarters(lower_bound, lower_bound)
                    continue

                selected_quarter = _select_less_quarter_interval(range, next_mainten_quarter)
                if quarter_turnover_constraint[work.Work_Package_Number][selected_quarter] > 0:
                    sum_interval += quarter_difference(next_mainten_quarter, selected_quarter)
                    next_mainten_quarter = selected_quarter
                    break
                else:
                    range.remove(selected_quarter)

            # 对应周转件约束数量减一，记录维修日期
            quarter_turnover_constraint[work.Work_Package_Number][next_mainten_quarter] -= 1
            work.mainten_quarter.append(next_mainten_quarter)
            # 更新下一次维修季度
            next_mainten_quarter = add_quarters(next_mainten_quarter, interval_quarter)

    print('正在处理全寿命计划的非周转件委外工作包...')

    # 排序含有非周转件约束的工作包
    not_turnover_package.sort(key=lambda x: (x.Work_Package_Interval_Conversion_Value, x.Online_Date, x.Cooling_Time, x.Train_Number, x.Work_Package_Number), reverse=False)

    for work in tqdm(not_turnover_package):
        work.mainten_quarter = []
        # 初始化基本信息
        start_mainten_quarter = convert_day_to_quarter(work.Online_Date)
        end_mainten_quarter = add_quarters(start_mainten_quarter, 120)

        # 上次维修的季度
        last_mainten_quarter = convert_day_to_quarter(work.last_mainten_time)
        # 维修间隔的季度表示
        interval_quarter = int(work.Work_Package_Interval_Conversion_Value / 90)

        # 根据历史维修信息，计算下一次维修的季度
        next_mainten_quarter = add_quarters(last_mainten_quarter, int(work.Work_Package_Interval_Conversion_Value / 90))
        
        # 如果下一次标准维修的季度小于当前季度，则将下一次维修季度设置为当前季度
        if compare_quarters(next_mainten_quarter, current_quarter) == 1:  # next_mainten_quarter < current_quarter
            next_mainten_quarter = current_quarter
            work.mainten_quarter.append(next_mainten_quarter)
            # 更新下一次维修季度
            next_mainten_quarter = add_quarters(next_mainten_quarter, interval_quarter)
        else:
            next_mainten_quarter = add_quarters(last_mainten_quarter, interval_quarter)
        
        while compare_quarters(next_mainten_quarter, end_mainten_quarter) == 1:
            # 增加维修季度
            work.mainten_quarter.append(next_mainten_quarter)

            # 更新下一次维修季度
            next_mainten_quarter = add_quarters(next_mainten_quarter, interval_quarter)

    return turnover_package + not_turnover_package

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
        if work.Shared_Cooling_Work_Package_Number == 'None':
            turnover_quarter_constrain = {}
            for quarter in quarter_list:
                turnover_quarter_constrain[quarter] = int(30 / work.Cooling_Time) * 3
            turnover_cd[work.Work_Package_Number] = turnover_quarter_constrain
        else:
            if work.Shared_Cooling_Work_Package_Number not in turnover_cd:
                turnover_quarter_constrain = {}
                for quarter in quarter_list:
                    turnover_quarter_constrain[quarter] = int(30 / work.Cooling_Time) * 3
                turnover_cd[work.Shared_Cooling_Work_Package_Number] = turnover_quarter_constrain
            turnover_cd[work.Work_Package_Number] = turnover_cd[work.Shared_Cooling_Work_Package_Number]
    return turnover_cd


def _select_less_quarter_worktime_load(quarter_worktime_load, sum_interval, range, worktime, next_mainten_quarter, alpha):
    min_value = float('inf')
    all = {}
    for i in range:
        all[i] = (quarter_worktime_load[i] + worktime) + (sum_interval + quarter_difference(i, next_mainten_quarter)) * alpha
    min_key = min(all, key=all.get)
    return min_key

def _select_less_quarter_interval(range, next_mainten_quarter):
    all = {}
    for i in range:
        all[i] = quarter_difference(i, next_mainten_quarter)
    
    min_key = min(all, key=all.get)
    return min_key