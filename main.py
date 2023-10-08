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


def Wholelife_Plan(config):
    # 读取不同类型的工作包、列车、约束等数据
    # 列车数据
    today = convert_str_to_date(config['today'])
    TrainData_list = read_TrainData(os.path.join(config['file_path'], config['TrainDataFilename']))
    Train_Data = [TrainData(train, today) for train in TrainData_list]
    
    # 工作包数据
    work_package_list = read_WorkPackage(os.path.join(config['file_path'], config['WorkPackageFilename']))
    work_package = [WorkPackage(work) for work in work_package_list]
    
    # 特殊工作包
    SpecialWorkPackage = config['SpecialWorkPackage'].split()
    
    # 历史维修时间
    last_maintenance_time = read_Last_Mainten_Time(os.path.join(config['file_path'], config['LastMaintenTimeFilename']))
    
    # 根据列车和工作包数据，初始化每一列车的工作包
    ALL_workpackage = []
    for train in Train_Data:
        ID = train.Train_Number
        for info in work_package:
            workpackage = copy.deepcopy(info)
            workpackage.Train_Number = ID
            key = tuple([workpackage.Train_Number,workpackage.Work_Package_Number])
            if key in last_maintenance_time:
                workpackage.last_mainten_time = datetime.strptime(list(last_maintenance_time[key])[0][2],"%Y-%m-%d")
                workpackage.last_mainten_mterial = list(last_maintenance_time[key])[0][1]
            else:
                workpackage.last_mainten_time = train.Online_Date
                workpackage.last_mainten_mterial = 0
            workpackage.Online_Date = train.Online_Date
            # workpackage.sum_mainten_days = Compute_Days_Train_Remaining_Life(workpackage.Online_Date, today)
            ALL_workpackage.append(workpackage)
    
    work_package = [work for work in ALL_workpackage if work.Work_Package_Number not in SpecialWorkPackage and work.Work_Package_Contract != '委外']


    # 全生命，年计划，月计划，周计划分开输出
    t = wholelife_plan(work_package, config)
    output_wholeLife_plan(t)


if __name__ == '__main__':
    start_time = time.time()
    # 下面是config.yaml配置文件
    # file_path: ./datasets
    config_name = './datasets/config.yaml'
    config = read_file_config(config_name)
    
    # 设置必要的参数
    np.random.seed(int(config['seed']))
    random.seed(int(config['seed']))
    
    Wholelife_Plan(config)
    
    end_time = time.time()
    elapsed_time_in_seconds = end_time - start_time
    hours, remainder = divmod(elapsed_time_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 打印结果
    print(f"程序运行时间：{int(hours)}时{int(minutes)}分{int(seconds)}秒")
    exit(0)