# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 10:53:57 2021

@author: JZ2018
"""

#import time
import requests
import pandas as pd
#import datetime
#from re import findall
#from copy import copy
#from random import randint
from io import StringIO

def weather_dl(year, city, station_ID):
    #default month to 1, downloads entire year
    month = '1'
    #generate csv url from gov of canada website
    csv_url = f'https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_ID}&Year={year}&Month={month}&Day=1&time=&timeframe=2&submit=Download+Data'
    csv_dl = requests.get(csv_url).content
    #download and read as pandas dataframe
    df = pd.read_csv(StringIO(csv_dl.decode("utf8")))
    return df

# parms for data export
city = 'yyc'
station_ID = '50430'
year = "2020"

#get raw data into pd dataframe
df_raw  = weather_dl(year, city, station_ID)
