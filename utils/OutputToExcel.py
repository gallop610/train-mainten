import openpyxl
import os
import multiprocessing as mp
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from utils.utils_time import convert_day_to_quarter, convert_day_to_month, quarter_difference, month_difference, add_quarters, add_months
        
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
            tmp = [work.Train_Number,work.Work_Package_Number, work.Work_Package_Person_Day, int(work.Work_Package_Interval_Conversion_Value), work.Cooling_Time,date,last_mainten, quarter_difference(date,last_mainten), int(work.Work_Package_Interval_Conversion_Value/90)-quarter_difference(date,last_mainten)]
            
            tmp.extend([tmp[8]*90/(int(tmp[3])), add_quarters(tmp[6],int(math.ceil(tmp[3]*1.05/90)))])
            mainten_quarter.append(tmp)
    
    wb = openpyxl.Workbook()
    ws = wb.create_sheet(title='全寿命计划')
    ws.append(['列车编号','工作包编号','维修时间','工作包间隔转换值','冷却时间','维修时间','上次维修时间', '间隔季度差值', '过修季度','过修百分比','红线日期'])
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
            tmp1 = [work.Train_Number,work.Work_Package_Number, work.Work_Package_Person_Day, int(work.Work_Package_Interval_Conversion_Value), work.Cooling_Time,date,last_mainten, month_difference(date,last_mainten), tmp]
            tmp1.extend([tmp1[8]*30/int(tmp1[3]), add_months(tmp1[6],int(math.ceil(tmp1[3]/30)))])
            mainten_month.append(tmp1)
    
    wb = openpyxl.Workbook()
    ws = wb.create_sheet(title='年计划')
    ws.append(['列车编号','工作包编号','维修时间','工作包间隔转换值','冷却时间','维修时间','上次维修时间', '间隔月份差值', '过修月份','过修百分比','红线日期'])
    mainten_month.sort(key=lambda x: (x[5], x[3], x[0], x[1],x[6],x[4]), reverse=False)
    for data in mainten_month:
        ws.append(list(data))
    wb.remove(wb['Sheet'])
    folder_path = './results'
    # 判断文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    wb.save(os.path.join(folder_path, '年计划.xlsx'))
    
def output_month_plan(workpackage):
    mainten_day = []
    for i in range(len(workpackage)):
        work = workpackage[i]
        for j in range(len(work.mainten_day)):
            date = work.mainten_day[j]
            if j == 0:
                last_mainten = work.last_mainten_time
            else:
                last_mainten = work.mainten_day[j-1]
                
            tmp = [work.Train_Number, work.Work_Package_Number, work.Work_Package_Person_Day, int(work.Work_Package_Interval_Conversion_Value), work.Cooling_Time,
                    date, last_mainten, (date-last_mainten).days, int(work.Work_Package_Interval_Conversion_Value)-(date-last_mainten).days,
                    (int(work.Work_Package_Interval_Conversion_Value)-(date-last_mainten).days)/int(work.Work_Package_Interval_Conversion_Value),
                    last_mainten + relativedelta(days=int(work.Work_Package_Interval_Conversion_Value*1.05))]
            tmp = [tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5].strftime("%Y-%m-%d"), tmp[6].strftime("%Y-%m-%d"), tmp[7], tmp[8], tmp[9], tmp[10].strftime("%Y-%m-%d")]
            mainten_day.append(tmp)

    wb = openpyxl.Workbook()
    ws = wb.create_sheet(title='月计划')
    ws.append(['列车编号','工作包编号','维修时间','工作包间隔转换值','冷却时间','维修时间','上次维修时间', '间隔天数差值', '过修天数','过修百分比','红线日期'])
    mainten_day.sort(key=lambda x: (x[5], x[3], x[0], x[1],x[6],x[4]), reverse=False)
    print('正在写入月计划...')
    for data in tqdm(mainten_day):
        ws.append(list(data))
    wb.remove(wb['Sheet'])
    folder_path = './results'
    # 判断文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    wb.save(os.path.join(folder_path, '月计划.xlsx'))