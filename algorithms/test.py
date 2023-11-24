    print('处理45日包')
    for work in tqdm(year_plan_workpackage):
        # 寻找维修间隔为45的工作包，开始直接排列
        if work.Work_Package_Interval_Conversion_Value == 45:
            work.mainten_day = []
            start_mainten_date = work.Online_Date
            end_mainten_date = start_mainten_date + relativedelta(days=366 * 30)
            interval_days = 45
            # 将股道优先级按字典存储并根据优先级排序
            # track_type_priority = {track[0]: track[1] for track in work.Track_Type_Priority}
            next_mainten_date = work.last_mainten_time + relativedelta(days=45)
            while next_mainten_date <= end_mainten_date:
                float_range_ub = interval_days * 0.05
                upper_bound = next_mainten_date + relativedelta(days=int(float_range_ub))
                float_range_lb = interval_days * 0.05
                lower_bound = next_mainten_date - relativedelta(days=int(float_range_lb))

                # 判断上界和下界的日期会不会超出边界，满足调节则置为边界值
                if upper_bound >= end_mainten_date:
                    upper_bound = end_mainten_date - relativedelta(days=1)

                if lower_bound < current_day:
                    lower_bound = current_day
                date_difference = (upper_bound - lower_bound).days
                date_range = [lower_bound + relativedelta(days=i) for i in range(date_difference + 1)]
                for date_info in date_range:
                    if work.Train_Number in train_limit[date_info]:
                        next_mainten_date = date_info
                        break
                    work.mainten_day.append(next_mainten_date)
                    day_worktime_load[next_mainten_date]['all'] += work.Work_Package_Person_Day
                    # 统计列车维修工时负载
                    if work.Train_Number not in day_worktime_load[next_mainten_date]:
                    day_worktime_load[next_mainten_date][work.Train_Number] = 0.0
                    day_worktime_load[next_mainten_date][work.Train_Number] += work.Work_Package_Person_Day
                    train_limit[next_mainten_date].add(work.Train_Number)  # 维修的列车数量

                    next_mainten_date = next_mainten_date + relativedelta(days=45)