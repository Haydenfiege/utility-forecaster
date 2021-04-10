# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 13:26:03 2021

@author: JZ2018
"""

import lxml
import time
import requests
import pandas as pd
import datetime
from re import findall
from copy import copy
from random import randint
from numpy import where

#import functions from source file
#execfile('D:/JZP/dl_funs.py')

#function to create url for downloading aeso electricity data
def aeso_url_gen(tablename, contenttype, startdate, enddate, dateformat = None):
    #convert start and end dates to url format
    startdate = dateconv(startdate, dateformat)
    enddate = dateconv(enddate, dateformat)
    url = f'http://ets.aeso.ca/ets_web/ip/Market/Reports/{tablename}ReportServlet?beginDate={startdate}&endDate={enddate}&contentType={contenttype}'
    #time.sleep(3)
    print('download url generated: ' + url)
    return url

#function to convert y-m-d date string to mdy in url generation
def dateconv(mydate, dateformat = None):
    #check if mydate is already in datetime format, convert if not
    if not isinstance(mydate, datetime.datetime) and dateformat is not None:     
        mydate = datetime.datetime.strptime(mydate, dateformat)

    #create string formatted for url date input
    yr = str(mydate.year)
    mo = '0' + str(mydate.month) if mydate.month < 10 else str(mydate.month)
    d = '0' + str(mydate.day) if mydate.day < 10 else str(mydate.day)
    output = mo + d + yr
    print('converted date string from ' + str(mydate) + ' to datetime value ' + output)
    return output

#function to download and pre process dataframe from aeso
def aeso_download_one(url):
    #get data into pandas df from processed url
    download_raw = pd.read_html(url)
    df = range_dl_combine(download_raw)
    #flatten multi index column names into single column names
    if len(df.columns.names)>1:
        cols = ''
        for l in range(0, len(df.columns.names)):
            if l == 0:
                cols = df.columns.get_level_values(l)
            else:
                cols = cols +'_'+df.columns.get_level_values(l)
        df.columns = cols
    else:
        cols = df.columns
    #convert date columns to datetime format
    datecols = [n for n in cols if len(findall('(?i)date', n))>0]
    for dc in datecols:
        #convert hour 24 to hour 00 for pandas to_datetime conversion
        df[dc] = df[dc].str[:-2]+where(df[dc].str[-2:]=='24', '00', df[dc].str[-2:])
        #convert column to date time
        df[dc] = df[dc].str.replace('*', '')
        df[dc] = df[dc].apply(pd.to_datetime)
    return df

#function to download data for timerange
def aeso_download_range(tablename, contenttype, startdate, enddate, dateformat):
    #convert start/end to date time format
    startdate = datetime.datetime.strptime(startdate, dateformat)
    enddate = datetime.datetime.strptime(enddate, dateformat)
    
    #trim end date if it's greater than current datetime
    if enddate > datetime.datetime.now():
        enddate = copy(datetime.datetime.now())
    
    #calculate number of days from start to end
    dayrange = (enddate - startdate).days
    #remove combine_df object if exists
    if 'combine_df' in locals() or 'combine_df' in globals():
        del combine_df
    
    #pull directly if range less than 30 days
    if dayrange <=30:
        print('date range <= 30 days, downloading')
        url = aeso_url_gen(tablename, contenttype, startdate, enddate, dateformat)    
        combine_df = aeso_download_one(url)
    else:
        #create list of start/end dates in 30 day intervals
        dl_ranges = dayrange_parse(startdate, enddate)

        #loop through list of start/end dates and pull each one, append together into combine_df
        for r in range(0,len(dl_ranges)):
            range_start = dl_ranges[r][0]
            range_end = dl_ranges[r][1]
            url = aeso_url_gen(tablename, contenttype, range_start, range_end, dateformat)    
            df = aeso_download_one(url)
            if 'combine_df' in locals() or 'combine_df' in globals():
                combine_df = combine_df.append(df, ignore_index = True)
            else:
                combine_df = copy(df)
            print(str(range_start) + 'downloaded')
            sleeptime = randint(3,9)
            print('sleep for ' + str(sleeptime) + ' seconds')
            #time.sleep(sleeptime)
        
    return combine_df

#parse start/end range into list of start/end dates in 30 day intervals
def dayrange_parse(startdate, enddate):
    r_start = copy(startdate)
    out_list = []
    while r_start < enddate:
        if r_start + datetime.timedelta(days=30) > enddate:
            r_end = copy(enddate)
        else:
            r_end = r_start + datetime.timedelta(days=30)
        out_list.append([r_start, r_end])
        r_start = copy(r_end) + datetime.timedelta(days=1)
        if r_start >= enddate:
            break    
    print('date range > 30 days, parse into ' + str(len(out_list)) + ' number of downloads')
    return out_list


def range_dl_combine(download_raw):
    for d in range(0, len(download_raw)):
        df_rows = download_raw[d].shape[0]
        if df_rows > 3:
            tempdf = download_raw[d]
            if 'combine_df' in locals() or 'combine_df' in globals():
                combine_df = combine_df.append(tempdf, ignore_index = True)
            else:
                combine_df = tempdf
        else:
            next
            
    output = combine_df.copy()    
    if 'combine_df' in locals() or 'combine_df' in globals():
        del combine_df
        
    return output


# =============================================================================
# #input parameters
# tablename = 'DailyAveragePoolPrice'
# startdate = '2015-01-01'
# enddate = '2021-03-31'
# dateformat = '%Y-%m-%d'
# contenttype = 'html'
# #url = aeso_url_gen(tablename, contenttype, startdate, enddate, dateformat)    
# #df = aeso_download_one(url)
# #pd.options.display.max_columns = df.shape[1]
# #df.describe(include='all')
# #dr = aeso_download_range(startdate, enddate, dateformat)
# 
# #get table of downloaded data, sort by date
# final_df = aeso_download_range(tablename, contenttype, startdate, enddate, dateformat)
# final_df = final_df.sort_values(by='$/MWh_Date').reset_index()
# final_df.to_csv('D:/JZP/test.csv')
# =============================================================================


