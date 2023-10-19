import openpyxl
import os
import multiprocessing as mp
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils.utils_time import convert_day_to_quarter, convert_day_to_month, quarter_difference, month_difference
        
def output_wholeLife_plan(workpackage):
    mainten_quarter = []
    for i in range(len(workpackage)):
        work = workpackage[i]
        for j in range(len(work.mainten_quarter)):
            date = work.mainten_quarter[j]
            if j == 0:
                last_mainten = convert_day_to_quarter(work.last_mainten_time)
            else:
                last_mainten = work.mainten_quarter[j-1]
            mainten_quarter.append((work.Train_Number,work.Work_Package_Number, work.Work_Package_Person_Day, int(work.Work_Package_Interval_Conversion_Value), work.Cooling_Time,date,last_mainten, quarter_difference(date,last_mainten), int(work.Work_Package_Interval_Conversion_Value/90)-quarter_difference(date,last_mainten)))
    
    wb = openpyxl.Workbook()
    ws = wb.create_sheet(title='全寿命计划')
    ws.append(['列车编号','工作包编号','维修时间','工作包间隔转换值','冷却时间','维修时间','上次维修时间', '间隔季度差值', '过修季度'])
    mainten_quarter.sort(key=lambda x: (x[5], x[3], x[0], x[1],x[6],x[4]), reverse=False)
    for data in mainten_quarter:
        ws.append(list(data))
    wb.remove(wb['Sheet'])
    folder_path = './results'
    # 判断文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    wb.save(os.path.join(folder_path, '全寿命计划.xlsx'))
    
def output_year_plan(workpackage):
    mainten_month = []
    for i in range(len(workpackage)):
        work = workpackage[i]
        for j in range(len(work.mainten_month)):
            date = work.mainten_month[j]
            if j == 0:
                last_mainten = convert_day_to_month(work.last_mainten_time)
            else:
                last_mainten = work.mainten_month[j-1]
            tmp = int(work.Work_Package_Interval_Conversion_Value/30)-month_difference(date,last_mainten)- int(int(work.Work_Package_Interval_Conversion_Value)/2190)
            mainten_month.append((work.Train_Number,work.Work_Package_Number, work.Work_Package_Person_Day, int(work.Work_Package_Interval_Conversion_Value), work.Cooling_Time,date,last_mainten, month_difference(date,last_mainten), tmp))
    
    wb = openpyxl.Workbook()
    ws = wb.create_sheet(title='年计划')
    ws.append(['列车编号','工作包编号','维修时间','工作包间隔转换值','冷却时间','维修时间','上次维修时间', '间隔月份差值', '过修月份'])
    mainten_month.sort(key=lambda x: (x[5], x[3], x[0], x[1],x[6],x[4]), reverse=False)
    for data in mainten_month:
        ws.append(list(data))
    wb.remove(wb['Sheet'])
    folder_path = './results'
    # 判断文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    wb.save(os.path.join(folder_path, '年计划.xlsx'))