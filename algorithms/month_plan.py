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

def month_plan(month_plan_workpackage, year_plan_workpackage, config):
    # 初始化参数
    config['today'] = '2021-01-01'
    today = convert_str_to_date(config['today'])
    days_index = gen_day_10980(config['today'])
    
    # 工时负载
    worktime_load = {index:0.0 for index in days_index}
    # 维修列车数量限制
    train_limit = {index:set() for index in days_index}
    # 检修道数量限制
    track_limit = {index:set() for index in days_index}
    # 临修道数量限制
    temp_track_limit = {index:set() for index in days_index}
    # 周转件数量限制
    turnover_limit = _day_turnover_package(year_plan_workpackage, days_index)
    
    # 优先处理8 16日工作包
    
    
    
    
    for work in month_plan_workpackage:
        pass
        
        
    



def _day_turnover_package(workpackage, days_index):
    turnover_limit = {}
    for work in workpackage:
        if np.isnan(work.Cooling_Time):
            continue
        if not isinstance(work.Shared_Cooling_Work_Package_Number,str) and np.isnan(work.Shared_Cooling_Work_Package_Number):
            turnover_constrain = {index:True for index in days_index}
            turnover_limit[work.Work_Package_Number] = turnover_constrain
        else:
            if work.Work_Package_Number not in turnover_limit and work.Shared_Cooling_Work_Package_Number not in turnover_limit:
                turnover_constrain = {index:True for index in days_index}
                turnover_limit[work.Work_Package_Number] = turnover_constrain
                turnover_limit[work.Shared_Cooling_Work_Package_Number] = turnover_constrain