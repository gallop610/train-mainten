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

def convert_day_to_month(day):
    """
    将日期转换为月份，返回月份字符串，格式为YYYY-MM。
    
    Args:
        day: datetime.date类型，需要转换的日期。
    
    Returns:
        返回月份字符串，格式为YYYY-MM。
    """
    month = day.month
    year = day.year
    return f"{year}-{month:02d}"

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

def gen_month_360(str_month):
    """
    生成一个包含360个月份的列表，从给定的月份开始，每次加1个月，直到360个月。
    
    参数：
        str_month：str类型，表示开始的月份，格式为"YYYY-MM"，其中YYYY表示年份，MM表示月份，如"2022-03"表示2022年3月。
    
    返回：
        months：list类型，包含360个月份的列表，每个月份的格式为"YYYY-MM"，如["2022-03", "2022-04", "2022-05", ...]
    """
    months = []
    current_month = str_month
    cnt = 0
    while cnt < 360:
        months.append(current_month)
        year, month = current_month.split('-')
        month = int(month)
        if month == 12:
            year = str(int(year) + 1)
            month = 1
        else:
            month += 1
        current_month = f"{year}-{month:02d}"
        cnt += 1
    return months

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

def add_months(str_month, cnt):
    """
    将给定的月份字符串加上指定的月份数，返回新的月份字符串。
    
    Args:
    - str_month (str): 给定的月份字符串，格式为 "YYYY-MM"，其中 YYYY 表示年份，MM 表示月份。
    - cnt (int): 指定的月份数，可以为正数、负数或零。
    
    Returns:
    - str: 新的月份字符串，格式同输入的月份字符串。
    """
    
    year, month = str_month.split('-')
    month = int(month)
    dt = datetime(int(year), month, 1)
    dt += relativedelta(months=cnt) 
    year = dt.year
    month = dt.month
    return f"{year}-{month:02d}"

def add_days(str_day, cnt):
    """
    将给定的日期字符串加上指定的天数，返回新的日期字符串。
    
    Args:
    - str_day (str): 给定的日期字符串，格式为 "YYYY-MM-DD"，其中 YYYY 表示年份，MM 表示月份，DD 表示日期。
    - cnt (int): 指定的天数，可以为正数、负数或零。
    
    Returns:
    - str: 新的日期字符串，格式同输入的日期字符串。
    """
    
    dt = datetime.strptime(str_day, '%Y-%m-%d')
    dt += relativedelta(days=cnt) 
    return dt.strftime('%Y-%m-%d')

def compare_quarters(a, b):
    """
    Compares two quarters and returns True if a < b, False otherwise.
    
    Args:
        a (str): A string representing a quarter in the format "YYYYQX".
        b (str): A string representing a quarter in the format "YYYYQX".
    
    Returns:
        int: 1 if a < b, 0 if a==b, -1 if a > b.
    """
    year_a, quarter_a = map(int, a.split('Q'))
    year_b, quarter_b = map(int, b.split('Q'))
    if year_a < year_b:
        return 1
    elif year_a == year_b and quarter_a < quarter_b:
        return 1
    elif year_a == year_b and quarter_a == quarter_b:
        return 0
    else:
        return -1

def compare_months(a, b):
    """
    Compares two months and returns True if a < b, False otherwise.
    
    Args:
        a (str): A string representing a month in the format "YYYY-MM".
        b (str): A string representing a month in the format "YYYY-MM".
    
    Returns:
        int: 1 if a < b, 0 if a==b, -1 if a > b.
    """
    year_a, month_a = a.split('-')
    year_b, month_b = b.split('-')
    if year_a < year_b:
        return 1
    elif year_a == year_b and month_a < month_b:
        return 1
    elif year_a == year_b and month_a == month_b:
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

# 两个月份之间的所有月份
def gen_all_months(start_month, end_month):
    months = []
    current_month = start_month
    while current_month != end_month:
        months.append(current_month)
        year, month = current_month.split('-')
        month = int(month)
        if month == 12:
            year = str(int(year) + 1)
            month = 1
        else:
            month += 1
        current_month = f"{year}-{month:02d}"
    months.append(end_month)
    return months

# 两个季度之间相差多少个季度
def quarter_difference(start_quarter, end_quarter):
    # print(start_quarter, end_quarter)
    if compare_quarters(start_quarter, end_quarter) == -1:
        start_quarter, end_quarter = end_quarter, start_quarter
    start_year, start_q = map(int, start_quarter.split('Q'))
    end_year, end_q = map(int, end_quarter.split('Q'))
    difference = (end_year - start_year) * 4 + (end_q - start_q)
    return difference

def gen_all_months_on_quarter(str_quarter):
    """
    生成一个包含3个月份的列表，从给定的季度开始，每次加1个月，直到3个月。
    
    参数：
        str_quarter：str类型，表示开始的季度，格式为"YYYYQX"，其中YYYY表示年份，QX表示季度数，如"2022Q3"表示2022年第3季度。
    
    返回：
        months：list类型，包含3个月份的列表，每个月份的格式为"YYYY-MM"，如["2022-07", "2022-08", "2022-09"]
    """
    year, quarter = str_quarter.split('Q')
    if quarter == '1':
        months= [f'{year}-01', f'{year}-02', f'{year}-03']
    elif quarter == '2':
        months= [f'{year}-04', f'{year}-05', f'{year}-06']
    elif quarter == '3':
        months= [f'{year}-07', f'{year}-08', f'{year}-09']
    else:
        months= [f'{year}-10', f'{year}-11', f'{year}-12']
    return months

# 两个月份之间相差多少个月份
def month_difference(start_month, end_month):
    if compare_months(start_month, end_month) == -1:
        start_month, end_month = end_month, start_month
    start_year, start_m = map(int, start_month.split('-'))
    end_year, end_m = map(int, end_month.split('-'))
    difference = (end_year - start_year) * 12 + (end_m - start_m)
    return difference

