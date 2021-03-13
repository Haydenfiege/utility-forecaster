# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 10:53:57 2021

@author: JZ2018
"""

import time
import requests
import pandas as pd
import datetime
from re import findall
from copy import copy
from random import randint
from io import StringIO
from itertools import groupby as it_groupby

def weather_dl_one(year, city, station_ID, timeframe):
    if timeframe == 2: 
        print(f'downloading daily data for year {year}')
        #default month to 1, downloads entire year
        month = '1'
        #generate csv url from gov of canada website
        csv_url = f'https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_ID}&Year={year}&Month={month}&Day=1&time=&timeframe={timeframe}&submit=Download+Data'
        csv_dl = requests.get(csv_url).content
        #download and read as pandas dataframe
        df = pd.read_csv(StringIO(csv_dl.decode("utf8")))
    elif timeframe == 1:
        #download by month when its hourly data
        for month in range(1, 13):
            print(f'downloading hourly data for year-month: {year}-{month}')
            #generate csv url from gov of canada website
            csv_url = f'https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_ID}&Year={year}&Month={month}&Day=1&time=&timeframe={timeframe}&submit=Download+Data'
            csv_dl = requests.get(csv_url).content
            #download and read as pandas dataframe
            temp_df = pd.read_csv(StringIO(csv_dl.decode("utf8")))
            sleeptime = randint(1,4)
            print('sleep for ' + str(sleeptime) + ' seconds')
            time.sleep(sleeptime)
            if 'df' in locals() or 'df' in globals():
                df = df.append(temp_df, ignore_index = True)
            else:
                df = temp_df
         
    return df

def weather_proc(df):
    datecols = [n for n in df.columns if len(findall('(?i)date', n))>0]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    select_coltype = ['datetime','int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    sub_df = df.select_dtypes(include = select_coltype)
    
    temperature_cols = [n for n in sub_df.columns if len(findall('(?i)temp|deg', n))>0]
    temperature_cols = [n for n in temperature_cols if len(findall('(?i)gust', n))==0]
    
    sub_df[temperature_cols] = sub_df[temperature_cols].interpolate()
    sub_df = sub_df.drop(sub_df.loc[:, sub_df.isna().all()].columns, axis = 1)
    sub_df = sub_df.drop(sub_df.columns[sub_df.apply(all_equal)], axis = 1)
    
    non_temperature_cols = [n for n in sub_df.columns if n not in temperature_cols]   
    sub_df[non_temperature_cols] = sub_df[non_temperature_cols].fillna(0)  
    

    
    return sub_df


def all_equal(iterable):
    "Returns True if all elements are equal to each other"
    g = it_groupby(iterable)
    return next(g, True) and not next(g, False)


def weather_dl_range(startdate, enddate, dateformat, city, timeframe, clean=False):
    
    startdate = datetime.datetime.strptime(startdate, dateformat)
    enddate = datetime.datetime.strptime(enddate, dateformat)
    
    startyear = startdate.year
    endyear = enddate.year
    
    weather_stations = {
      "YYC": "50430",
      "YEG": "27214",
      "YMM": "49490"
    }
    if city.upper() not in weather_stations.keys():
        print('city name not found in dictionary')
        return None
    else:
        station_ID = weather_stations[city.upper()]
        print(f'Getting data for {city.upper()}, station ID {station_ID}')
    
        for yr in range(int(startyear), int(endyear)+1):
            df = weather_dl_one(yr, city, station_ID, timeframe)
            if 'combine_df' in locals() or 'combine_df' in globals():
                combine_df = combine_df.append(df, ignore_index = True)
            else:
                combine_df = copy(df)
            print('data for year ' + str(yr) + ' downloaded')
            sleeptime = randint(3,9)
            print('sleep for ' + str(sleeptime) + ' seconds')
            time.sleep(sleeptime)
        #process data to fill na and subset to useful columns
        if clean==True:
            df_proc = weather_proc(combine_df)  
        else:
            df_proc = combine_df
        
        df_out = weather_trunc_time(df_proc, startdate, enddate)
        return df_out

def weather_trunc_time(df_proc, startdate, enddate):
    datecols = [n for n in df_proc.columns if len(findall('(?i)date', n))>0]
    use_datecol = datecols[0]
    #truncate dates past current date
    df_out = df_proc.loc[df_proc[use_datecol] <= datetime.datetime.now()]
    #truncate dates to bewteen start and end dates
    df_out = df_out.loc[df_out[use_datecol] >=  startdate]
    df_out = df_out.loc[df_out[use_datecol] <=  enddate]
    return df_out

# =============================================================================
# # parms for data export
# city = 'yyc'
# station_ID = '50430'
# startyear = "2020"
# endyear = "2021"
# #get raw data into pd dataframe
# df  = weather_dl_range(startyear, endyear, city, timeframe=1, clean=True)
# df.to_csv('D:/JZP/weather.csv') 
# =============================================================================

