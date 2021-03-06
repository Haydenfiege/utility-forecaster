'''
    File name: aeso_scrape.py
    Author: Hayden Fiege
    Date created: 03/01/2021
    Date last modified: 03/01/2021
    Python Version: 3.8.8
'''

import pandas as pd
import requests 
from datetime import datetime

# parameters for URL
report_type = 'HistoricalPoolPriceReportServlet' 
start_date = '02282020' 
end_date = '02282021'
content_type = 'html'

# check if date range is acceptable
start_date_datatime = datetime.strptime(start_date, '%M%d%Y')
end_date_datatime = datetime.strptime(end_date, '%M%d%Y')
time_delta = end_date_datatime - start_date_datatime

# check if date range is acceptable as the AESO site can only generate HTML tables for date ranges <366 days
start_date_datatime = datetime.strptime(start_date, '%M%d%Y')
end_date_datatime = datetime.strptime(end_date, '%M%d%Y')
time_delta = end_date_datatime - start_date_datatime

# error check
if time_delta >= 366:
    print("There has been an error in the system.")
    import sys
    sys.exit(1)

# URL for web scrape
url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/{}?beginDate={}&endDate={}&contentType={}'.format(report_type, start_date, end_date, content_type)
print(url)

# get html into text using requests 
source = requests.get(url).text

# use pandas to read html table to df
df_list = pd.read_html(source)
print(df_list)
df = df_list[1]
print(df)

# write to csv
file_name = 'aeso_{}_{}_to_{}.csv'.format(report_type, start_date, end_date)
file_path = 'data_collection/data/{}'.format(file_name)
df.to_csv(file_path)