import timeit
from collections import defaultdict

import pandas as pd
import json
import numpy as np
import datetime as dt
from pathlib import Path
import holidays
import re

ROOT = Path(__file__).parent
TODAY = dt.datetime.today()
NOW = dt.datetime.now()
output_filename = f"clean_{TODAY.year}{TODAY.month:02d}{TODAY.day:02d}_{NOW.hour:02d}"
outfile = (ROOT / 'data' / output_filename).with_suffix('.csv')

df = pd.read_csv(ROOT / 'data' / 'clean_20190211_15.csv')

def closest_holiday(df, threshold=5):
    """
    Determine if this was a holiday weekend, if so, then a
    :param df:
    :param threshold:
    :return:
    """

    us_holidays = holidays.US()
    df['is_holiday'] = df.release_dt.apply(lambda x: x in us_holidays)
    US_HOLIDAY_DATES = list(us_holidays.keys())
    US_HOLIDAY_NAMES = list(us_holidays.values())
    holiday_df = pd.concat([pd.Series(US_HOLIDAY_DATES), pd.Series(US_HOLIDAY_NAMES)], axis=1)
    holiday_df.rename(columns={0:'holiday_dt',1:'holiday_name'},inplace=True)
    holiday_df.holiday_dt = pd.to_datetime(holiday_df.holiday_dt,infer_datetime_format=True)
    holiday_df.set_index('holiday_dt',inplace=True)
    holiday_df.sort_index(inplace=True)

    def nearest_holiday(rel_date):
        check_date = pd.to_datetime(rel_date, infer_datetime_format=True)
        index = holiday_df.index.get_loc(check_date, "nearest")
        date_val = holiday_df.iloc[index].name
        ret_val = f'{check_date- date_val},{holiday_df.iloc[index]["holiday_name"]}'
        return ret_val

    df['holiday_info'] = df.release_dt.apply(lambda x: nearest_holiday(x))
    df = pd.concat([df, df.holiday_info.str.split(',', expand=True, n=1)],axis=1)
    df.rename(columns={0:'days_from_holiday',1:'holiday_name'}, inplace=True)
    df.drop(columns=['holiday_info'],inplace=True)
    exp = re.compile(r'(-?\d+)\s+days')

    def parse_date(x):
        return int(exp.findall(x)[0])

    df.days_from_holiday = df.days_from_holiday.apply(lambda x:parse_date(x))
    return df

def filter_holidays(df, threshold =7):
    mask = abs(df.days_from_holiday) > threshold
    df.days_from_holiday[mask] = df.holiday_name[mask] = None
    return df

df = closest_holiday(df)
#df = filter_holidays(df, 7)

df.to_csv(outfile,index_label='id')
