# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 21:14:55 2021

@author: JZ2018
"""

import streamlit as st
import pandas as pd
import altair as alt
import datetime
import urllib
import plotly.express as px
from gsheet_fun import *
from electricity_scrape import *
#@st.cache

#d2 = pd.read_csv('aeso_hpp.csv')
#d2 = d2.drop(d2.columns[0], axis = 1)
#Gsheet_Append(d2, aeso_hpp_id, sheet_range)
#aeso_hpp = Gsheet_Download(aeso_hpp_id, sheet_range)
#aeso_hpp['Date (HE)'] = aeso_hpp['Date (HE)'].apply(pd.to_datetime)
#dftest = aeso_hpp[0:2]
#Gsheet_Append(dftest, aeso_hpp_id, sheet_range)

def get_data():
    #df = pd.read_csv('aeso_hpp.csv')
    # here enter the id of your google sheet
    aeso_hpp_id = '1sRkTyY8jlv-NGizn-0ulBSIgIjQmVvpBVnofy49-NPM'
    #weather_daily_id = '1niPYt8HCYKWLFqnJbSv-7p-kuk9qheIx-igeL5hIy0s'
    #weather_hourly_id = '1k_41_j8CpYeGDNdRWRlIyx_2cx58ROp-6bQ3RcFZidg'
    sheet_range = 'A1:AA1000000'
    df = Gsheet_Download(aeso_hpp_id, sheet_range)
    df['Date (HE)'] = df['Date (HE)'].apply(pd.to_datetime)
    num_cols = ['Price ($)', '30Ravg ($)', 'AIL Demand (MW)']
    df[num_cols] = df[num_cols].apply(pd.to_numeric)
    # if df.columns.values[0] == 'Unnamed: 0':
    #     df.columns.values[0] = 'RowID'
    # else:
    #     df['RowID'] = df.index+1
    return df

def check_newdata(data):
    maxdate = max(data['Date (HE)'])
    currdate = datetime.datetime.now()
    dateformat = '%Y-%m-%d'
    if maxdate < currdate:
        append_data = aeso_download_range('HistoricalPoolPrice', 'html',  maxdate.strftime(dateformat),  currdate.strftime(dateformat), dateformat)
        append_data['Date (HE)'] = append_data['Date (HE)'].apply(pd.to_datetime)
        num_cols = ['Price ($)', '30Ravg ($)', 'AIL Demand (MW)']
        append_data[num_cols] = append_data[num_cols].apply(pd.to_numeric)
        data2 = data.append(append_data).reset_index(drop=True).drop_duplicates().sort_values('Date (HE)')
    else:
        data2 = data.copy()
    return data2

try:
    data_gsheet = get_data()
    data = check_newdata(data_gsheet)
    
    data['Electricity Price $/kwh'] = data['Price ($)'] / 1000
    data = data.rename(columns={'Date (HE)':'Date'})
    #data['Date'] = data['Date'].apply(pd.to_datetime)
    
    st.write('current datetime '+str(datetime.datetime.now()))    
    mindate = st.date_input(
       'Plot Start Date', datetime.date(2020,1,1)
    )
    
    st.write('Click below to update plot time range')
    dateupdate = st.button('Update Plot Time Range')
    
    st.write('Enter your quoted electricity price below in $/kwh')
    user_priceinput = st.number_input('Price')
    st.write(f'Your price is {user_priceinput} $/kwh')
    
    st.write('Enter your electricity price lock-in time')
    user_locktime = st.number_input('Years', format = '%i')
    user_locktime_int = int(user_locktime)
    st.write(f'Your quoted price is locked in for {user_locktime_int} years')
    
    mindate = datetime.datetime.strptime(str(mindate), '%Y-%m-%d')
    
    if not mindate:
        st.error("Please select start date for plot range")
    else:
        if dateupdate:
            df = data.loc[data['Date']>=mindate]
        else:
            df = data.loc[data['Date']>=datetime.datetime.strptime('2020-01-01', '%Y-%m-%d')]
        
        st.write("AESO Historical Data", df)

        chart1 = (
            alt.Chart(df)
            .mark_line(opacity=0.5)
            .encode(
                x="Date:T",
                y=alt.Y("Electricity Price $/kwh:Q", stack=None)
            )
        )
        
        # chart2 = (
        #     alt.Chart(df)
        #     .mark_line(opacity=0.5)
        #     .encode(
        #         x="Date:T",
        #         y=alt.Y("AIL Demand (MW):Q", stack=None)
        #     )
        # )
        chart2 = px.scatter(df, x='Date', y='AIL Demand (MW)')
        
        st.write('Alberta Electricity Price History')
        st.altair_chart(chart1, use_container_width=True)
        st.write('Alberta Electricity Demand Hsitory')
        st.plotly_chart(chart2, use_container_width=True)
        
except urllib.error.URLError as e:
    st.error(
        """
        **error**

        Connection error: %s
    """
        % e.reason
        )