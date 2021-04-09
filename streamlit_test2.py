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

#@st.cache
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
    mindate = datetime.datetime.strptime(str(mindate), '%Y-%m-%d')
    if not mindate:
        st.error("Please select start date for plot range")
    else:
        data['Electricity Price $/kwh'] = data['Price ($)'] / 1000
        data.columns.values[1] = 'Date'
        data['Date'] = data['Date'].apply(pd.to_datetime)
        df = data.loc[data['Date']>=mindate]
        
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