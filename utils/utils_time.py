from datetime import datetime
from dateutil.relativedelta import relativedelta

def convert_str_to_date(str_time):
    """
    将字符串时间转换为日期格式。
    
    Args:
        str_time (str): 字符串时间，格式为 "%Y-%m-%d"。
    
    Returns:
        datetime.date: 转换后的日期格式。
    """
    return datetime.strptime(str_time, "%Y-%m-%d")

def convert_day_to_quarter(day):
    """
    将日期转换为季度，返回季度字符串，格式为YYYYQ1/Q2/Q3/Q4。
    
    Args:
        day: datetime.date类型，需要转换的日期。
    
    Returns:
        返回季度字符串，格式为YYYYQ1/Q2/Q3/Q4。
    """
    month = day.month
    year = day.year
    if 1 <= month <= 3:
        quarter = f"{year}Q1"
    elif 4 <= month <= 6:
        quarter = f"{year}Q2"
    elif 7 <= month <= 9:
        quarter = f"{year}Q3"
    else:
        quarter = f"{year}Q4"
    return quarter

def gen_quarter_120(str_quarter):
    """
    生成一个包含120个季度的列表，从给定的季度开始，每次加1个季度，直到120个季度。
    
    参数：
        str_quarter：str类型，表示开始的季度，格式为"YYYYQX"，其中YYYY表示年份，QX表示季度数，如"2022Q3"表示2022年第3季度。
    
    返回：
        quarters：list类型，包含120个季度的列表，每个季度的格式为"YYYYQX"，如["2022Q3", "2022Q4", "2023Q1", ...]
    """
    quarters = []
    current_quarter = str_quarter
    cnt = 0
    while cnt < 120:
        quarters.append(current_quarter)
        year, quarter = current_quarter.split('Q')
        quarter = int(quarter)
        if quarter == 4:
            year = str(int(year) + 1)
            quarter = 1
        else:
            quarter += 1
        current_quarter = f"{year}Q{quarter}"
        cnt += 1
    return quarters

def add_quarters(str_quarter, cnt):
    """
    将给定的季度字符串加上指定的季度数，返回新的季度字符串。
    
    Args:
    - str_quarter (str): 给定的季度字符串，格式为 "YYYYQX"，其中 YYYY 表示年份，QX 表示季度数，X 为 1、2、3、4 中的一个数字。
    - cnt (int): 指定的季度数，可以为正数、负数或零。
    
    Returns:
    - str: 新的季度字符串，格式同输入的季度字符串。
    """
    
    year, quarter = str_quarter.split('Q')
    quarter = int(quarter)
    dt = datetime(int(year), (quarter-1)*3+1, 1)
    dt += relativedelta(months=3*cnt) 
    year = dt.year
    quarter = (dt.month-1)//3 + 1
    return f"{year}Q{quarter}"

def compare_quarters(a, b):
    """
    Compares two quarters and returns True if a < b, False otherwise.
    
    Args:
        a (str): A string representing a quarter in the format "YYYYQX".
        b (str): A string representing a quarter in the format "YYYYQX".
    
    Returns:
        int: 1 if a < b, 0 if a==b, -1 if a > b.
    """
    year_a, quarter_a = a.split('Q')
    year_b, quarter_b = b.split('Q')
    if year_a < year_b:
        return 1
    elif year_a == year_b and quarter_a < quarter_b:
        return 1
    elif year_a == year_b and quarter_a == quarter_b:
        return 0
    else:
        return -1

# 两个季度之间的所有季度
def gen_all_quarters(start_quarter, end_quarter):
    quarters = []
    current_quarter = start_quarter
    while current_quarter != end_quarter:
        quarters.append(current_quarter)
        year, quarter = current_quarter.split('Q')
        quarter = int(quarter)
        if quarter == 4:
            year = str(int(year) + 1)
            quarter = 1
        else:
            quarter += 1
        current_quarter = f"{year}Q{quarter}"
    quarters.append(end_quarter)
    return quarters

# 两个季度之间相差多少个季度
def quarter_difference(start_quarter, end_quarter):
    # print(start_quarter, end_quarter)
    start_date = datetime.strptime(start_quarter, '%YQ%m')
    end_date = datetime.strptime(end_quarter, '%YQ%m')
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    difference = (end_date.year - start_date.year) * 4 + (end_date.month - start_date.month) // 3
    return difference