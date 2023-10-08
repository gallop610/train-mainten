import openpyxl
import os
import multiprocessing as mp
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils.utils_time import convert_day_to_quarter
        
def output_wholeLife_plan(workpackage):
    mainten_quarter = {}
    for i in range(len(workpackage)):
        work = workpackage[i]
        for j in range(len(work.mainten_quarter)):
            date = work.mainten_quarter[j]
            year = date.split('Q')[0]
            if year not in mainten_quarter:
                mainten_quarter[year] = []
            if j == 0:
                last_mainten = convert_day_to_quarter(work.last_mainten_time)
            else:
                last_mainten = work.mainten_quarter[j-1]
            mainten_quarter[year].append((work.Train_Number,work.Work_Package_Number, work.Work_Package_Person_Day, int(work.Work_Package_Interval_Conversion_Value), work.Cooling_Time,date,last_mainten))
    
    wb = openpyxl.Workbook()
    key = list(mainten_quarter.keys())
    key.sort()
    for year in key:
        ws = wb.create_sheet(title=year)
        print(year)
        ws.append(['列车编号','工作包编号','维修时间','工作包间隔转换值','冷却时间','维修时间','上次维修时间'])
        mainten_data = mainten_quarter[year]
        mainten_data.sort(key=lambda x: (x[5], x[3], x[0], x[1],x[6],x[4]), reverse=False)
        
        for data in mainten_data:
            ws.append(list(data))
    wb.remove(wb['Sheet'])
    folder_path = './results'
    # 判断文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    wb.save(os.path.join(folder_path, '全寿命计划.xlsx'))