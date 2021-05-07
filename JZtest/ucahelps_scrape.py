# -*- coding: utf-8 -*-
"""
Created on Wed May  5 23:25:04 2021

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


def dateconv(mydate, dateformat = None):
    #check if mydate is already in datetime format, convert if not
    if not isinstance(mydate, datetime.datetime) and dateformat is not None:     
        mydate = datetime.datetime.strptime(mydate, dateformat)
    #create string formatted for url date input
    yr = str(mydate.year)
    mo = str(mydate.month) 
    d = str(mydate.day)
    output = mo + '%2F' + d + '%2F' + yr
    
    print('converted date string from ' + str(mydate) + ' to datetime value ' + output)
    return output


def raw_url_gen(start_date, end_date, dateformat):   
    start_date_str = dateconv(start_date, dateformat)
    end_date_str = dateconv(end_date, dateformat)
    raw_url = f'https://ucahelps.alberta.ca/api/api/ExportHistoricalData?energy-type=0&retailer=&rate-type=&service-area=&start-date={start_date_str}&end-date={end_date_str}'
    return raw_url
    
def uca_download(start_date, end_date, dateformat=None):
    
    startdate = datetime.datetime.strptime(start_date, dateformat)
    enddate = datetime.datetime.strptime(end_date, dateformat)
    
    if enddate > datetime.datetime.now():
        enddate = copy(datetime.datetime.now())   
        
    #calculate number of days from start to end
    dayrange = (enddate - startdate).days
    
    if 'combine_df' in locals() or 'combine_df' in globals():
        del combine_df
        
    #pull directly if range less than 30 days
    if dayrange <=181:
        print('date range <= 6 months, extending start date back to minimum of 6 months')
        startdate = startdate - datetime.timedelta(days=181-dayrange)
    elif dayrange > 181 and dayrange < 720:
        combine_df = uca_single_dl(start_date, end_date, dateformat)
    elif dayrange >= 720:
        dl_ranges = dayrange_parse(startdate, enddate)
        #loop through list of start/end dates and pull each one, append together into combine_df
        for r in range(0,len(dl_ranges)):
            range_start = dl_ranges[r][0]
            range_end = dl_ranges[r][1]
            #url = raw_url_gen(range_start, range_end, dateformat)
            df = uca_single_dl(range_start, range_end, dateformat)
            if 'combine_df' in locals() or 'combine_df' in globals():
                combine_df = combine_df.append(df, ignore_index = True)
            else:
                combine_df = copy(df)
            print(str(range_start) + 'downloaded')
            sleeptime = randint(3,9)
            print('sleep for ' + str(sleeptime) + ' seconds')
            #time.sleep(sleeptime)
    
    return combine_df

def dayrange_parse(startdate, enddate):
    r_start = copy(startdate)
    out_list = []
    while r_start < enddate:
        if r_start + datetime.timedelta(days=719) > enddate:
            r_end = copy(enddate)
        else:
            r_end = r_start + datetime.timedelta(days=719)
        out_list.append([r_start, r_end])
        r_start = copy(r_end) + datetime.timedelta(days=1)
        if r_start >= enddate:
            break    
    print('date range > 24 months, parse into ' + str(len(out_list)) + ' number of downloads')
    return out_list   

def uca_single_dl(start_date, end_date, dateformat ):
    rawl_url = raw_url_gen(start_date, end_date, dateformat)
    print(f'generated website link as {rawl_url}')
    raw_dl = requests.get(rawl_url, verify=False).content
    print(f'raw request link generated as {raw_dl}')
    raw_link = str(raw_dl).replace("b'{", '').replace('"filePath":"', '').replace('","error":false,"errorMessage":""}', '').replace("'", "")
    dl_link = 'https://ucahelps.alberta.ca'+raw_link
    print(f'downloading csv from {dl_link}')
    time.sleep(1)
    df = pd.read_csv(dl_link, error_bad_lines=False)
    print('csv downloaded')    
    return df



start_date = '2012-08-01'
end_date = '2021-05-01'
dateformat = '%Y-%m-%d'
mydf = uca_download(start_date, end_date, dateformat)
mydf.to_csv('D:/JZP/uca_hist.csv')
mydf.to_parquet('D:/JZP/uca_hist.parquet')

#raw_url = 'https://ucahelps.alberta.ca/api/api/ExportHistoricalData?energy-type=0&retailer=&rate-type=&service-area=&start-date=9%2F1%2F2020&end-date=4%2F5%2F2021'
#csv_url = 'https://ucahelps.alberta.ca/api/api/ExportHistoricalData?energy-type=0&retailer=&rate-type=&service-area=&start-date=4%2F5%2F2020&end-date=4%2F5%2F2021'
df = pd.read_csv('D:/JZP/uca_hist_processed.csv')
df.to_parquet('D:/JZP/uca_hist_processed.parquet')
#csv_dl_url = 'https://ucahelps.alberta.ca/Temp/HistoricalDataExport_20210505_110251.csv'
# raw_dl = requests.get(csv_url, verify=False).content
# #df = pd.read_csv(StringIO(csv_dl.decode("utf8")))
# raw_link = str(raw_dl).replace("b'{", '').replace('"filePath":"', '').replace('","error":false,"errorMessage":""}', '').replace("'", "")
# dl_link = 'https://ucahelps.alberta.ca'+raw_link
# df = pd.read_csv(dl_link)
