import os
import yaml
import pandas as pd
from collections import defaultdict
from datetime import datetime

def read_file_config(yaml_file_path) -> dict:
    '''
    从文件中读取配置信息，包括不同约束文件的文件路径、文件名等

    Args:
        yaml_file_path (string): yaml格式的配置文件，命名为xxx.yaml

    Returns:
        dict : 以字典的形式给出所有配置信息 
    '''
    # 读取 YAML file
    with open(yaml_file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    return yaml_data

def read_WorkPackage(filename) -> list:
    '''
    从文件中读取工作包数据信息，将每一行的信息转为对应的字典，注意每一个字典是工作包数据.xlsx中三个sheet的相同内容的集合，最后将所有字典组成的列表，并返回

    Args:
        filename (string): 工作包数据.xlsx的文件路径

    Returns:
        list: 以列表的形式给出所有工作包数据信息
    '''

    # 从Excel文件读取数据到dataframes
    df1 = pd.read_excel(filename, sheet_name='工作包数据')
    df2 = pd.read_excel(filename, sheet_name='工作包物资')
    df3 = pd.read_excel(filename, sheet_name='股道优先级')
    
    # 创建一个defaultdict来存储每个工作包的物资信息
    WorkPackageMaterials = defaultdict(set)
    for _, row in df2.iterrows():
        # 将行数据转换为元组
        data = tuple(row)  
        # 提取前两个元素作为键
        key = data[0:2]
        # 剩下的元素是物资信息     
        materials = data[2:]  
        WorkPackageMaterials[key].add(materials)

    # 创建一个defaultdict来存储每条股道的优先级信息
    TrackPriority = defaultdict(set)
    for _, row in df3.iterrows():
        # 将行数据转换为元组
        data = tuple(row)  
        # 提取股道ID作为键
        track_id = data[0]  
        # 剩下的元素是优先级数据
        priority_data = data[1:]  
        TrackPriority[track_id].add(priority_data)
    
    WorkPackage = list()
    AttributeList = ['Train_Type', 'Work_Package_Number', 'Electrifiable', 'Powerless', 'Work_Package_Interval_Time_Dimension', 'Work_Package_Interval_Value', 'Work_Package_Interval_Conversion_Value', 
                     'Work_Package_Person_Day', 'Work_Package_Person_Day_Unit_Price', 'Need_Trial_Run','Work_On_Non_Working_Day','Cooling_Time','Shared_Cooling_Work_Package_Number','Sampling_Times',
                     'Combined_Work_Package_Number','Need_High_Voltage_Verification','Work_Package_Contract','Undercarriage_Assembly','Material','Track_Type_Priority']
    # 遍历df1中的每一行数据
    for _, row in df1.iterrows():
        # 将行数据转换为列表
        data = list(row)  
        # 如果工作包的前两项数据在WorkPackageMaterials中存在
        if tuple(data[0:2]) in WorkPackageMaterials:
            data.append(list(WorkPackageMaterials[tuple(data[0:2])]))
        else:
            data.append(None)
        # 如果工作包号在TrackPriority中存在
        if data[1] in TrackPriority:
            data.append(list(TrackPriority[data[1]]))
        else:
            data.append(None)
        
        combined_dict = {}
        # 组合属性列表和数据列表为一个字典
        for i in range(min(len(AttributeList), len(data))):
            combined_dict[AttributeList[i]] = data[i]
        WorkPackage.append(combined_dict)
    # 返回包含工作包信息的列表
    return WorkPackage

def read_TrainData(filename) -> list:
    df = pd.read_excel(filename, sheet_name='列车数据管理')
    # 创建一个defaultdict来存储每个工作包的物资信息
    AttributeList = ['Train_Type', 'Train_Number', 'Online_Date', 'Mileage_Record_Date', 'Mileage', 'Train_Status', 'Maintenance_Base']
    TrainData = []
    for _, row in df.iterrows():
        # 将行数据转换为元组
        data = list(row)
        combined_dict = {}
        # 组合属性列表和数据列表为一个字典
        for i in range(min(len(AttributeList), len(data))):
            combined_dict[AttributeList[i]] = data[i]
        TrainData.append(combined_dict)
    return TrainData


def read_Last_Mainten_Time(filename) -> list:
    df = pd.read_excel(filename, sheet_name='上次维修数据管理')
    Last_Mainten_Time = defaultdict(set)
    for _, row in df.iterrows():
        # 将行数据转换为元组
        data = tuple(row)
        # 提取前两个元素作为键
        key = data[0:2]
        # 剩下的元素是物资信息     
        materials = data[2:] 
        if key in Last_Mainten_Time:
            # 比较日期，选择日期大的
            date1 = datetime.strptime(list(Last_Mainten_Time[key])[2], "%Y-%m-%d")
            date2 = datetime.strptime(materials[2], "%Y-%m-%d")
            if date2 > date1:
                Last_Mainten_Time[key] = materials
        else:
            Last_Mainten_Time[key] = materials
    return Last_Mainten_Time
    
    
        
    
# test
if __name__ == "__main__":
    config_name = 'config.yaml'
    config = read_file_config(config_name)
    read_WorkPackage(os.path.join(config['file_path'], config['WorkPackageFilename']))
    # print(config)
