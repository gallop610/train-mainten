from SchedulingEntities import *
import numpy as np
import copy
from utils import *
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pdb
import matplotlib.pyplot as plt
import math
import pandas as pd
from tqdm import tqdm
import os

def analyze_track(ALL_workpackage, config):
    # 绘图
    # A股道
    track_limit = {}
    # C股道
    temp_track_limit = {}
    for work in ALL_workpackage:
        track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}
        if len(track_type_priority) == 1:
            if 'A' in track_type_priority:
                track = ('A', work.Train_Number)
            elif 'C' in track_type_priority:
                track = ('C', work.Train_Number)
        elif 'A' in track_type_priority and 'C' in track_type_priority:
            track = ('AC', work.Train_Number)
        else:
            continue
        print(track)
        
        for day_info in work.mainten_day:
            if track[0] == 'A':
                if day_info not in track_limit:
                    track_limit[day_info] = set()
                track_limit[day_info].add(track[1])
            elif track[0] == 'C':
                if day_info not in temp_track_limit:
                    temp_track_limit[day_info] = set()
                temp_track_limit[day_info].add(track[1])
                
    track_limit = dict(sorted(track_limit.items(), key=lambda x: x[0]))
    with open('track_limit.txt', 'w') as f:
        for key, value in track_limit.items():
            if len(value) > 3:
                f.write('{},{}\n'.format(key, ','.join([str(v) for v in value])))
    
    temp_track_limit = dict(sorted(temp_track_limit.items(), key=lambda x: x[0]))
    with open('temp_track_limit.txt', 'w') as f:
        for key, value in temp_track_limit.items():
            if len(value) > 1:
                f.write('{},{}\n'.format(key, ','.join([str(v) for v in value])))


    