import datetime
import numpy as np
class WorkPackage(object):
    '''
    工作包类

    Args:
        object (_type_): _description_
    '''
    def __init__(self, work_package_data) -> None:
        '''
        这是WorkPackage的初始化函数，用于从work_package_data中读取数据并初始化WorkPackage类的实例。

        Args:
            work_package_data (dict): 一个字典格式的变量，用于初始化WorkPackage类的实例。
        '''
        # 列车类型, string
        self.Train_Type:str = work_package_data['Train_Type']
        
        # 列车编号, string
        self.Train_Number:int = None
        
        # 工作包编号, string
        self.Work_Package_Number:str = work_package_data['Work_Package_Number']
        
        # 是否可以通电工作, bool
        self.Electrifiable:bool = work_package_data['Electrifiable']
        
        # 是否可以断电工作, bool
        self.Powerless:bool = work_package_data['Powerless']
        
        # 工作包间隔时间维度, string
        self.Work_Package_Interval_Time_Dimension:str = work_package_data['Work_Package_Interval_Time_Dimension']
        
        # 工作包间隔值, int
        self.Work_Package_Interval_Value:int = work_package_data['Work_Package_Interval_Value']
        
        # 工作包间隔转换值, int
        self.Work_Package_Interval_Conversion_Value:int = work_package_data['Work_Package_Interval_Conversion_Value']
        
        # 工作包人天(h), float
        self.Work_Package_Person_Day:float = work_package_data['Work_Package_Person_Day']
        
        # 工作包人天单价(元/h), float
        self.Work_Package_Person_Day_Unit_Price:float = work_package_data['Work_Package_Person_Day_Unit_Price']
        
        # 工作包需要花费的时间, float
        self.Work_amount = self.Work_Package_Person_Day * self.Work_Package_Person_Day_Unit_Price
        
        # 是否需要试车, bool
        self.Need_Trial_Run:bool = work_package_data['Need_Trial_Run']
        
        # 是否在非工作日工作, bool
        self.Work_On_Non_Working_Day:bool = work_package_data['Work_On_Non_Working_Day']
        
        # 冷却时间（天）, int
        if not np.isnan(work_package_data['Cooling_Time']):
            self.Cooling_Time:int = int(work_package_data['Cooling_Time'])
        else:
            self.Cooling_Time:int = work_package_data['Cooling_Time']
            
        # 共享冷却工作包编号, string
        self.Shared_Cooling_Work_Package_Number:str = work_package_data['Shared_Cooling_Work_Package_Number']
        
        # 抽检次数, int
        self.Sampling_Times:int = work_package_data['Sampling_Times']
        
        # 组合工作包编号, string
        self.Combined_Work_Package_Number:str = work_package_data['Combined_Work_Package_Number']
        
        # 是否需要高压验证, bool
        self.Need_High_Voltage_Verification:bool = work_package_data['Need_High_Voltage_Verification']
        
        # 工作包承包, string
        self.Work_Package_Contract:str = work_package_data['Work_Package_Contract']
        
        # 是否车下拆装, bool
        self.Undercarriage_Assembly:str = work_package_data['Undercarriage_Assembly']
        
        # 物资编号,set
        self.Material:set = work_package_data['Material']
        
        # 股道类型优先级,set
        self.Track_Type_Priority:set = work_package_data['Track_Type_Priority']
        
        
    def output(self):
        print(self.Track_Type_Priority, self.Material)
        
        