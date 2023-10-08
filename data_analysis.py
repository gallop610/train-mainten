import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def read_excel_file(file_path):
    """
    Given an excel file path, reads the contents of the file and returns a 2D list without the header row.
    """
    df = pd.read_excel(file_path)
    return df.values.tolist()[1:]

def draw_worktime_load(data, model):
    if model == 'wholelife':
        s1 = 'Quarters'
        s2 = 'Quarterly Worktime Load'
        s3 = 'Quarterly Worktime Load Analysis'
        s4 = './results/wholelife_worktime_load.png'
    elif model == 'year':
        s1 = 'Months'
        s2 = 'Monthly Worktime Load'
        s3 = 'Monthly Worktime Load Analysis'
        s4 = './results/year_worktime_load.png'
    
    # 筛选出周转件约束负载和非周转件约束负载
    turnover = [info for info in data if not np.isnan(info[4])]
    not_turnover = [info for info in data if np.isnan(info[4]) ]
    
    turnover_worktime_load = {}
    for info in turnover:
        if info[5] not in turnover_worktime_load:
            turnover_worktime_load[info[5]] = 0
        turnover_worktime_load[info[5]] += info[2]
    not_turnover_worktime_load = {}
    for info in not_turnover:
        if info[5] not in not_turnover_worktime_load:
            not_turnover_worktime_load[info[5]] = 0
        not_turnover_worktime_load[info[5]] += info[2]
    
    # 将字典，按照key排序，并将对应的value放入列表中
    turnover_worktime_load = sorted(turnover_worktime_load.items(),key = lambda x:x[0], reverse=False)
    not_turnover_worktime_load = sorted(not_turnover_worktime_load.items(),key = lambda x:x[0], reverse=False)
    
    turnover_worktime_load = [info[1] for info in turnover_worktime_load]
    not_turnover_worktime_load = [info[1] for info in not_turnover_worktime_load]
    all = [turnover_worktime_load[i] + not_turnover_worktime_load[i] for i in range(len(turnover_worktime_load))]
    
    # 绘制周转件约束负载和非周转件约束负载
    plt.plot(turnover_worktime_load, label='turnover')
    plt.plot(not_turnover_worktime_load, label='not turnover')
    plt.plot(all, label='all', color='r')

    # 添加标题和标签
    plt.legend()
    plt.xlabel(s1)
    plt.ylabel(s2)
    plt.title(s3)

    # 保存图为PNG文件
    plt.savefig(s4)
    

if __name__ == '__main__':
    file_path = './results/年计划.xlsx'
    r = read_excel_file(file_path)
    draw_worktime_load(r,'year')