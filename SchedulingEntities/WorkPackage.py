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
        # 是否需要试车, bool
        self.Need_Trial_Run:bool = work_package_data['Need_Trial_Run']
        # 是否在非工作日工作, bool
        self.Work_On_Non_Working_Day:bool = work_package_data['Work_On_Non_Working_Day']
        
        # 冷却时间（天）, int
        if not np.isnan(work_package_data['Cooling_Time']):
            self.Cooling_Time:int = work_package_data['Cooling_Time']
        else:
            self.Cooling_Time:int = 0
            
        # 共享冷却工作包编号, string
        if isinstance(work_package_data['Shared_Cooling_Work_Package_Number'], str):
            self.Shared_Cooling_Work_Package_Number:str = work_package_data['Shared_Cooling_Work_Package_Number']
        elif np.isnan(work_package_data['Shared_Cooling_Work_Package_Number']):
            self.Shared_Cooling_Work_Package_Number:str = 'None'
        
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
        
        # self._vaild_parameters()
    
    # 检验参数的合法性
    # def _vaild_parameters(self):
    #     if not isinstance(self.Train_Type, str):
    #         raise TypeError("Train_Type must be str.")
    #     if not isinstance(self.Work_Package_Number, str):
    #         raise TypeError("Work_Package_Number must be str.")
    #     if not isinstance(self.Electrifiable, bool):
    #         raise TypeError("Electrifiable must be bool.")
    #     if not isinstance(self.Powerless, bool):
    #         raise TypeError("Powerless must be bool.")
    #     if not isinstance(self.Work_Package_Interval_Time_Dimension, str):
    #         raise TypeError("Work_Package_Interval_Time_Dimension must be str.")
    #     if not isinstance(self.Work_Package_Interval_Value, int):
    #         raise TypeError("Work_Package_Interval_Value must be int.")
    #     if not isinstance(self.Work_Package_Interval_Conversion_Value, int):
    #         raise TypeError("Work_Package_Interval_Conversion_Value must be int.")
    #     if not isinstance(self.Work_Package_Person_Day, float):
    #         raise TypeError("Work_Package_Person_Day must be float.")
    #     if not isinstance(self.Work_Package_Person_Day_Unit_Price, float):
    #         raise TypeError("Work_Package_Person_Day_Unit_Price must be float.")
    #     if not isinstance(self.Need_Trial_Run, bool):
    #         raise TypeError("Need_Trial_Run must be bool.")
    #     if not isinstance(self.Work_On_Non_Working_Day, bool):
    #         raise TypeError("Work_On_Non_Working_Day must be bool.")
    #     if not isinstance(self.Cooling_Time, int):
    #         raise TypeError("Cooling_Time must be int.")
    #     if not isinstance(self.Shared_Cooling_Work_Package_Number, str):
    #         raise TypeError("Shared_Cooling_Work_Package_Number must be str.")
    #     if not isinstance(self.Sampling_Times, int):
    #         raise TypeError("Sampling_Times must be int.")
    #     if not isinstance(self.Combined_Work_Package_Number, str):
    #         raise TypeError("Combined_Work_Package_Number must be str.")
    #     if not isinstance(self.Need_High_Voltage_Verification, bool):
    #         raise TypeError("Need_High_Voltage_Verification must be bool.")
    #     if not isinstance(self.Work_Package_Contract, str):
    #         raise TypeError("Work_Package_Contract must be str.")
    #     if not isinstance(self.Undercarriage_Assembly, bool):
    #         raise TypeError("Undercarriage_Assembly must be bool.")
    #     if not isinstance(self.Material, set):
    #         raise TypeError("Material must be set.")
    #     if not isinstance(self.Track_Type_Priority, set):
    #         raise TypeError("Track_Type_Priority must be set.")
        
    def output(self):
        print(self.Track_Type_Priority, self.Material)
        
        