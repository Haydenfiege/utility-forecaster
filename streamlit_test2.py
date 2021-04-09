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

@st.cache(show_spinner=False)
def get_data():
    df = pd.read_csv('aeso_hpp.csv')
    if df.columns.values[0] == 'Unnamed: 0':
        df.columns.values[0] = 'RowID'
    return df

try:
    data = get_data()
        
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
        data['Electricity Price $/kwh'] = data['Price ($)'] / 1000
        data.columns.values[1] = 'Date'
        data['Date'] = data['Date'].apply(pd.to_datetime)
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