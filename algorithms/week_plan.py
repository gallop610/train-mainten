import pandas as pd
import numpy as np
from collections import Counter

def determine_track(filename, config):
    data = pd.read_excel(filename)
    bianhao = data['列车编号'].unique()
    baojiange = data['工作包间隔转换值'].unique()
    shijian = data['本次维修时间'].unique()
    data['股道'] = 0
    real_res = pd.DataFrame()
    
    for i in bianhao:
        for j in baojiange:
            for k in shijian:
                t = data[(data['列车编号'] == i) & (data['工作包间隔转换值'] == j) & (data['本次维修时间'] == k)]
                if not t.empty:
                    res = func(i, j, k, list(t['股道类型']))
                    t.loc[:, '股道'] = res
                    real_res = pd.concat([real_res, t])
                    
    real_res.to_excel('./results/月计划-股道.xlsx', sheet_name='Sheet1')
    
def func(i, j, k, l):
    res = []
    t = [s.split(",") for s in l]
    c = [letter for sublist in t for letter in sublist]
    counter = Counter(c)
    most_common_elements = {element for element, count in counter.items() if count == counter.most_common(1)[0][1]}
    for g in l:
        g = g.split(",")
        intersection = most_common_elements.intersection(set(g))
        for element in g:
            if element in intersection:
                most_common_element = element
                break
    for g in l:
        g = g.split(",")
        if j in (8, 16, 30, 45) and 'B' in g:
            res.append('B')
            continue
        elif most_common_element in g:
            res.append(most_common_element)
        else:
            res.append(g[0])
    return res