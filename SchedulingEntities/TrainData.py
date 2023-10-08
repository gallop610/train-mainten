from datetime import datetime
class TrainData(object):
    '''
    列车数据管理
    Args:
        object (_type_): _description_
    '''
    def __init__(self, train_data, today) -> None:
        '''
        这是TrainDataManagement的初始化函数，用于从train_data中读取数据并初始化TrainDataManagement类的实例。

        Args:
            train_data (dict): 一个字典格式的变量，用于初始化TrainDataManagement类的实例。
        '''
        # 车型, string
        self.Train_Type:str = train_data['Train_Type']
        
        # 列车编号, string
        self.Train_Number:str = train_data['Train_Number']
        
        # 上线日期, datetime
        self.Online_Date:datetime = datetime.strptime(train_data['Online_Date'], "%Y-%m-%d")
        
        # 列车距离生命结束剩余天数, int
        # self.Train_Remaining_Life:int = Compute_Days_Train_Remaining_Life(datetime.strptime(train_data['Online_Date'], "%Y-%m-%d"), today)

        # 里程记录日期
        self.Mileage_Record_Date:datetime = datetime.strptime(train_data['Mileage_Record_Date'], "%Y-%m-%d")
        
        # 里程数（公里）, int
        self.Mileage:int = train_data['Mileage']
        
        # 列车状态, string
        self.Train_Status:str = train_data['Train_Status']
        
        # 维修基地, string
        self.Maintenance_Base:str = train_data['Maintenance_Base']

    def output(self) -> None:
        '''
        这是TrainDataManagement的输出函数，用于输出TrainDataManagement类的实例的信息。

        Args:
            None

        Returns:
            None
        '''
        print(f"Train_Type: {self.Train_Type}, Train_Number: {self.Train_Number}, Online_Date: {self.Online_Date.strftime('%Y-%m-%d')}, Mileage_Record_Date: {self.Mileage_Record_Date.strftime('%Y-%m-%d')}, Mileage: {self.Mileage}, Train_Status: {self.Train_Status}, Maintenance_Base: {self.Maintenance_Base}")
