from algorithms import *
from SchedulingEntities import *
from utils import *
import os
import numpy as np
import copy
from datetime import datetime
import time
import random
import pdb
import pandas as pd
from tqdm import tqdm

def Wholelife_Plan(config):
    # 读取不同类型的工作包、列车、约束等数据
    # 列车数据
    TrainData_list = read_TrainData(os.path.join(config['file_path'], config['TrainDataFilename']))
    Train_Data = [TrainData(train) for train in TrainData_list]
    # 工作包数据
    work_package_list = read_WorkPackage(os.path.join(config['file_path'], config['WorkPackageFilename']))
    work_package = [WorkPackage(work) for work in work_package_list]
    # 特殊工作包
    SpecialWorkPackage = config['SpecialWorkPackage'].split()
    # 历史维修时间
    last_maintenance_time = read_Last_Mainten_Time(os.path.join(config['file_path'], config['LastMaintenTimeFilename']))
    # 列车检修记录
    Train_Mainten_Range = read_Train_Mainten_Range(os.path.join(config['file_path'], config['TrainMaintenRangeFilename']))
    
    # 根据列车和工作包数据，初始化每一列车的工作包
    ALL_workpackage = []
    for train in Train_Data:
        ID = train.Train_Number
        for info in work_package:
            if set([train.Train_Number,info.Work_Package_Number]) in Train_Mainten_Range:
                continue
            workpackage = copy.deepcopy(info)
            workpackage.Train_Number = ID
            key = tuple([workpackage.Train_Number,workpackage.Work_Package_Number])
            if key in last_maintenance_time:
                workpackage.last_mainten_time = datetime.strptime(list(last_maintenance_time[key])[2],"%Y-%m-%d")
                workpackage.last_mainten_mterial = list(last_maintenance_time[key])[1]
            else:
                workpackage.last_mainten_time = train.Online_Date
                workpackage.last_mainten_mterial = 0
            workpackage.Online_Date = train.Online_Date
            ALL_workpackage.append(workpackage)
    
    work_package = [work for work in ALL_workpackage if work.Work_Package_Number not in SpecialWorkPackage and work.Work_Package_Contract != '委外']

    # 挑选维修间隔大于90天的工作包
    WorkPackage_WholeLife = []
    for work in work_package:
        if work.Work_Package_Interval_Conversion_Value > 90:
            WorkPackage_WholeLife.append(work)
    result = wholelife_plan(WorkPackage_WholeLife, config)
    output_wholeLife_plan(result)
    
    
def _read_exist_plan(file_path):
    """
    Given an excel file path, reads the contents of the file and returns a 2D list without the header row.
    """
    df = pd.read_excel(file_path)
    data = df.values.tolist()
    exist_plan = {}
    for info in data:
        key = tuple([info[0],info[1],info[2]])
        if key not in exist_plan:
            exist_plan[key] = []
        exist_plan[key].append(info[20])
    return exist_plan
    
    
    
def Year_Plan(config):
    # 读取不同类型的工作包、列车、约束等数据
    # 列车数据
    TrainData_list = read_TrainData(os.path.join(config['file_path'], config['TrainDataFilename']))
    Train_Data = [TrainData(train) for train in TrainData_list]
    # 工作包数据
    work_package_list = read_WorkPackage(os.path.join(config['file_path'], config['WorkPackageFilename']))
    work_package = [WorkPackage(work) for work in work_package_list]
    # 特殊工作包
    SpecialWorkPackage = config['SpecialWorkPackage'].split()
    # 历史维修时间
    last_maintenance_time = read_Last_Mainten_Time(os.path.join(config['file_path'], config['LastMaintenTimeFilename']))
    # 根据列车和工作包数据，初始化每一列车的工作包
    Train_Mainten_Range = read_Train_Mainten_Range(os.path.join(config['file_path'], config['TrainMaintenRangeFilename']))
    
    ALL_workpackage = []
    for train in Train_Data:
        ID = train.Train_Number
        for info in work_package:
            if set([train.Train_Number,info.Work_Package_Number]) in Train_Mainten_Range:
                continue
            workpackage = copy.deepcopy(info)
            workpackage.Train_Number = ID
            key = tuple([workpackage.Train_Number,workpackage.Work_Package_Number])
            if key in last_maintenance_time:
                workpackage.last_mainten_time = datetime.strptime(list(last_maintenance_time[key])[2],"%Y-%m-%d")
                workpackage.last_mainten_mterial = list(last_maintenance_time[key])[1]
            else:
                workpackage.last_mainten_time = train.Online_Date
                workpackage.last_mainten_mterial = 0
            workpackage.Online_Date = train.Online_Date
            ALL_workpackage.append(workpackage)
    work_package = [work for work in ALL_workpackage if work.Work_Package_Number not in SpecialWorkPackage and work.Work_Package_Contract != '委外']

    # 读取全寿命计划表
    wholelife_plan = _read_exist_plan('./results/全寿命计划.xlsx')
    wholelife = []
    year = []
    for info in work_package:
        key = tuple([info.Train_Type,info.Train_Number,info.Work_Package_Number])
        if key in wholelife_plan:
            info.mainten_quarter = wholelife_plan[key]
            wholelife.append(info)
        if 30<info.Work_Package_Interval_Conversion_Value <= 90:
            year.append(info)
    result = year_plan(year, wholelife, config)
    output_year_plan(result)
    
def Month_Plan(config):
    # 读取不同类型的工作包、列车、约束等数据
    # 列车数据
    TrainData_list = read_TrainData(os.path.join(config['file_path'], config['TrainDataFilename']))
    Train_Data = [TrainData(train) for train in TrainData_list]
    # 工作包数据
    work_package_list = read_WorkPackage(os.path.join(config['file_path'], config['WorkPackageFilename']))
    work_package = [WorkPackage(work) for work in work_package_list]
    # 特殊工作包
    SpecialWorkPackage = config['SpecialWorkPackage'].split()
    # 历史维修时间
    last_maintenance_time = read_Last_Mainten_Time(os.path.join(config['file_path'], config['LastMaintenTimeFilename']))
    # 根据列车和工作包数据，初始化每一列车的工作包
    Train_Mainten_Range = read_Train_Mainten_Range(os.path.join(config['file_path'], config['TrainMaintenRangeFilename']))
    
    ALL_workpackage = []
    for train in Train_Data:
        ID = train.Train_Number
        for info in work_package:         
            if set([train.Train_Number,info.Work_Package_Number]) in Train_Mainten_Range:
                continue
            workpackage = copy.deepcopy(info)
            workpackage.Train_Number = ID
            key = tuple([workpackage.Train_Number,workpackage.Work_Package_Number])
            if key in last_maintenance_time:
                workpackage.last_mainten_time = datetime.strptime(list(last_maintenance_time[key])[2],"%Y-%m-%d")
                workpackage.last_mainten_mterial = list(last_maintenance_time[key])[1]
            else:
                workpackage.last_mainten_time = train.Online_Date
                workpackage.last_mainten_mterial = 0
            workpackage.Online_Date = train.Online_Date
            ALL_workpackage.append(workpackage)
            
    work_package = [work for work in ALL_workpackage if work.Work_Package_Number not in SpecialWorkPackage and work.Work_Package_Contract != '委外']
    
    # 读取年计划表
    year_plan = _read_exist_plan('./results/年计划.xlsx')
    year = []
    month = []
    print('正在将现有的年计划分配至工作包...')
    for info in tqdm(work_package):
        key = tuple([info.Train_Type,info.Train_Number,info.Work_Package_Number])
        if key in year_plan:
            info.mainten_month = year_plan[key]
            year.append(info)
        if info.Work_Package_Interval_Conversion_Value in [8, 16, 30]:
            month.append(info)
    result = month_plan(month, year, config)
    result = adjust(result, config)
    
    output_month_plan(result)

if __name__ == '__main__':
    start_time = time.time()
    # 下面是config.yaml配置文件
    # file_path: ./datasets
    config_name = './datasets/config.yaml'
    config = read_file_config(config_name)
    
    # 设置必要的参数
    np.random.seed(int(config['seed']))
    random.seed(int(config['seed']))
    
    # Wholelife_Plan(config)
    # Year_Plan(config)
    Month_Plan(config)
    
    end_time = time.time()
    elapsed_time_in_seconds = end_time - start_time
    hours, remainder = divmod(elapsed_time_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 打印结果
    print(f"程序运行时间：{int(hours)}时{int(minutes)}分{int(seconds)}秒")
    exit(0)