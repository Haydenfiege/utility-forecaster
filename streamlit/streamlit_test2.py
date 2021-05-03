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
#from pycaret.regression import *

import plotly.graph_objects as go
from plotly.offline import plot
from plotly.subplots import make_subplots

#@st.cache
#d2 = pd.read_csv('aeso_hpp.csv')
#d2 = d2.drop(d2.columns[0], axis = 1)
#Gsheet_Append(d2, aeso_hpp_id, sheet_range)
#aeso_hpp = Gsheet_Download(aeso_hpp_id, sheet_range)
#aeso_hpp['Date (HE)'] = aeso_hpp['Date (HE)'].apply(pd.to_datetime)
#dftest = aeso_hpp[0:2]
#Gsheet_Append(dftest, aeso_hpp_id, sheet_range)
#test_model = load_model('final_model1')

#function to retrieve data from google sheet
def get_data(sheet_id, sheet_range):
    #df = pd.read_csv('aeso_hpp.csv')
    # here enter the id of your google sheet
    #aeso_hpp_id = '1sRkTyY8jlv-NGizn-0ulBSIgIjQmVvpBVnofy49-NPM'
    #weather_daily_id = '1niPYt8HCYKWLFqnJbSv-7p-kuk9qheIx-igeL5hIy0s'
    #weather_hourly_id = '1k_41_j8CpYeGDNdRWRlIyx_2cx58ROp-6bQ3RcFZidg'
    #sheet_range = 'A1:AA1000000'
    
    #download google sheet with sheet id and excel style range (everything in string format)
    df = Gsheet_Download(aeso_hpp_id, sheet_range)
    #convert datetime column to appropriate format
    df['Date (HE)'] = df['Date (HE)'].apply(pd.to_datetime)
    #convert numerical columns to appropriate format
    num_cols = ['Price ($)', '30Ravg ($)', 'AIL Demand (MW)']
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors = 'coerce')
    # if df.columns.values[0] == 'Unnamed: 0':
    #     df.columns.values[0] = 'RowID'
    # else:
    #     df['RowID'] = df.index+1
    return df

#function to append new data to google sheet
def append_newdata(data, sheetid, sheet_range):
    #get max date available in downloaded google sheet data
    maxdate = max(data['Date (HE)'])
    #get current date time
    currdate = datetime.datetime.now()
    dateformat = '%Y-%m-%d'
    
    #use existing scrape functions to get new data if current date < maxdate in google sheet
    if maxdate < currdate:
        #call scrape function from electricity_scrape
        append_data = aeso_download_range('HistoricalPoolPrice', 'html',  maxdate.strftime(dateformat),  currdate.strftime(dateformat), dateformat)
        #convert column types
        append_data['Date (HE)'] = append_data['Date (HE)'].apply(pd.to_datetime)
        num_cols = ['Price ($)', '30Ravg ($)', 'AIL Demand (MW)']
        append_data[num_cols] = append_data[num_cols].apply(pd.to_numeric, errors='coerce')
        #append together new scraped data with historical data from google sheet
        data2 = data.append(append_data).reset_index(drop=True).drop_duplicates().sort_values('Date (HE)')
        #convert everything to string to prepare for google sheet upload
        upload_data = append_data.applymap(str)
        #Gsheet_Append(upload_data, sheetid, sheet_range)
        #upload new data to replace all data in google sheet
        Gsheet_updateAll(data2.applymap(str), sheetid, sheet_range)
        print(str(upload_data.shape[0]) + ' rows added to google sheet data')
        
    else:
        data2 = data.copy()
    return data2

# def Gen_Pred_df(model, data):
#     currdate = datetime.datetime.now()
#     maxdate = max(data['Date (HE)'])
df_preds = pd.read_parquet('combine_preds2.parquet')    

try:
    #google sheet id for electricity prices and demand (from Historical Pool Price)
    #aeso_hpp_id = '1sRkTyY8jlv-NGizn-0ulBSIgIjQmVvpBVnofy49-NPM'
    #define max sheet ranges to look for data in google sheet
    #sheet_range = 'A1:AA1000000'
    #get data from google sheet
    #data_gsheet = get_data(aeso_hpp_id, sheet_range)
    #check if new data needs to be appended to google sheet
    #data_new = append_newdata(data_gsheet, aeso_hpp_id, sheet_range)
    #clean and sort data
    #data = data_new.reset_index(drop=True).drop_duplicates().sort_values('Date (HE)')
    data = df_preds.copy()
    data_models = data['Data Source'].unique().tolist()
    data_models.remove('AESO_HPP_Historical')
    data['Date'] = data['Date'].apply(pd.to_datetime)
    data['Electricity Price $/kwh'] = data['Predicted Price $'] / 1000
    #data = data.rename(columns={'Date (HE)':'Date'})
    #data['Date'] = data['Date'].apply(pd.to_datetime)
    
    #print out current datetime in streamlit
    st.write('Current Date '+str(datetime.datetime.now().strftime('%Y-%m-%d')))    
    #streamlit input to filter plot range by minimum date
    mindate = st.date_input(
       'Plot Start Date', datetime.date(2020,1,1)
    )
    #streamlit input to update plot with defined range
    # st.write('Click below to update plot time range')
    # dateupdate = st.button('Update Plot Time Range')
    # #streamlit input for user's input electricity price quote
    st.sidebar.write('Enter your quoted electricity price below in $/kwh')
    user_priceinput = st.sidebar.number_input('Price')
    st.sidebar.write(f'Your price is {user_priceinput} $/kwh')
    #streamlit input for user's input electricity price quote period
    st.sidebar.write('Enter your electricity price lock-in time')
    #user_locktime = st.number_input('Years', format = '%i')
    user_locktime = st.sidebar.slider('Years', 0, 5, 1)
    user_locktime_int = int(user_locktime)
    st.sidebar.write(f'Your quoted price is locked in for {user_locktime_int} years')
    
    user_select_mod = st.sidebar.selectbox(label = 'Select Model', options=data_models)
    
    #convert minimum plot range date to appropriate format
    mindate = datetime.datetime.strptime(str(mindate), '%Y-%m-%d')
    maxdate = datetime.datetime.now() + datetime.timedelta(days=user_locktime_int*365)
    maxdate = maxdate.strftime('%Y-%m-%d')
    maxdate = datetime.datetime.strptime(str(maxdate), '%Y-%m-%d')
    #execute only if "mindate" exists
    if not mindate:
        st.error("Please select start date for plot range")
    else:
        # #update plot ranges via filtering the table to dates newer than mindate only
        # if dateupdate:
        #     df = data.loc[data['Date']>=mindate]
        # else:
        #     df = data.loc[data['Date']>=datetime.datetime.strptime('2020-01-01', '%Y-%m-%d')]
        df = data.loc[data['Date']>=mindate]
        df = df.loc[df['Date']<=maxdate]
        df['DailyCost'] = df['Electricity Price $/kwh'] * 20
        df_calcs = df[df['Data Source'] == user_select_mod]
        df_calcs = df_calcs.loc[df_calcs['Date']>=datetime.datetime.now().strftime('%Y-%m-%d')]
        df_calcs['CumCost'] = df_calcs['DailyCost'].cumsum()
        user_cost = 7300*user_priceinput*user_locktime_int
        cost_diff = round(df_calcs['CumCost'].max() - user_cost, 2)
        if cost_diff > 0:
            st.write(f'Your Quote is predicted to save ${abs(cost_diff)} dollars compared to variable price over {user_locktime_int} years')
        else:
            st.write(f'Your Quote is predicted to cost ${abs(cost_diff)} more dollars compared to variable price over {user_locktime_int} years')
        
        #write a header line and dataframe for visualization
        # st.write("AESO Historical Data", df)

        # #test Altair charting with electricity price over time
        # chart1 = (
        #     alt.Chart(df)
        #     .mark_line(opacity=0.5)
        #     .encode(
        #         x="Date:T",
        #         y=alt.Y("Electricity Price $/kwh:Q", stack=None)
        #     )
        # )
        
        # chart2 = (
        #     alt.Chart(df)
        #     .mark_line(opacity=0.5)
        #     .encode(
        #         x="Date:T",
        #         y=alt.Y("AIL Demand (MW):Q", stack=None)
        #     )
        # )
        
        #test plotly charting with AIL Demand over time
        # chart2 = px.scatter(df, x='Date', y='AIL Demand (MW)')
        
        # st.write('Alberta Electricity Price History')
        # st.altair_chart(chart1, use_container_width=True)
        # st.write('Alberta Electricity Demand Hsitory')
        # st.plotly_chart(chart2, use_container_width=True)
        
        fig=go.Figure()
        plt_types = df['Data Source'].unique().tolist()
        for p in plt_types:
            subdf = df.loc[df['Data Source']==p]
            if p == 'AESO_HPP_Historical':
                plt_mod = 'markers'
            else:
                plt_mod = 'lines'
            fig.add_trace(go.Scatter(x=subdf['Date'], y=subdf['Electricity Price $/kwh'], mode = plt_mod, name = p))
            fig.update_yaxes(type='log')
            fig.update_layout(width = 900)
        st.write('Alberta Electricity Demand History')
        st.plotly_chart(fig, use_container_width=False)
       
#error handling function        
except urllib.error.URLError as e:
    st.error(
        """
        **error**

        Connection error: %s
    """
        % e.reason
        )