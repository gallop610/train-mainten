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
    # 使用pandas创建以天为单位的索引
    # 工时负载
    worktime_load = pd.Series(0.0,index=pd.date_range(start=config['today'], end=add_days(config['today'],10980), freq='D'))
    # 维修列车数量限制
    train_limit = pd.Series(7,index=pd.date_range(start=config['today'], end=add_days(config['today'],10980), freq='D'))
    # 检修道数量限制
    track_limit = pd.Series(2,index=pd.date_range(start=config['today'], end=add_days(config['today'],10980), freq='D'))
    # 临修道数量限制
    temp_track_limit = pd.Series(2,index=pd.date_range(start=config['today'], end=add_days(config['today'],10980), freq='D'))
    # 周转件数量限制
    