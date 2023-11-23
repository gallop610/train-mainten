import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def read_excel_file(file_path):
    """
    Given an excel file path, reads the contents of the file and returns a 2D list without the header row.
    """
    df = pd.read_excel(file_path)
    return df.values.tolist()

def draw_train_number(data):
    plt.clf()
    all = {}
    print('正在计算日列车数量...')
    for info in tqdm(data):
        if info[5] not in all:
            all[info[5]] = set()
        all[info[5]].add(info[0])
    
    all = sorted(all.items(),key = lambda x:x[0], reverse=False)
    all = [len(info[1]) for info in all][:366]
    plt.plot(all, label='all', color='r')

    # 添加标题和标签
    y_ticks = [2,3,4,7]
    plt.yticks(y_ticks)
    for y_val in y_ticks:
        plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    plt.legend()
    plt.title('Train Number Analysis')
    plt.savefig('./results/train_number.png')

def draw_worktime_load(data, model):
    plt.clf()
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
    elif model == 'Month':
        s1 = 'Days'
        s2 = 'Daily Worktime Load'
        s3 = 'Daily Worktime Load Analysis'
        s4 = './results/month_worktime_load.png'
    
    # 筛选出周转件约束负载和非周转件约束负载
    turnover = [info for info in data if not np.isnan(info[4])]
    not_turnover = [info for info in data if np.isnan(info[4]) ]
    
    all = {}
    print('正在计算日工时负载...')
    for info in tqdm(data):
        if info[5] not in all:
            all[info[5]] = 0
        all[info[5]] += info[2]
        
    all = sorted(all.items(),key = lambda x:x[0], reverse=False)
    all = [info[1] for info in all][:366]
    
    plt.plot(all, label='all', color='r')

    # 添加标题和标签
    plt.legend()
    plt.title(s3)
    # y_ticks = np.arange(0, (max(all)//10 +1)*10, 10)
    # plt.yticks(y_ticks)
    # for y_val in y_ticks:
    #     plt.axhline(y=y_val, linestyle='--', color='gray', linewidth=0.3)
    # 保存图为PNG文件
    plt.savefig(s4)
    

if __name__ == '__main__':
    # file_path = './results/全寿命计划.xlsx'
    # r = read_excel_file(file_path)   
    # draw_worktime_load(r,'wholelife')
    
    file_path = './results/年计划.xlsx'
    r = read_excel_file(file_path)
    draw_worktime_load(r,'year')
    
    # file_path = './results/月计划.xlsx'
    # r1 = read_excel_file(file_path)
    # draw_worktime_load(r1,'Month')
    # draw_train_number(r1)