'''
    File name: gc_weather_scrape.py
    Author: Hayden Fiege
    Date created: 03/01/2021
    Date last modified: 03/01/2021
    Python Version: 3.8.8
'''

import requests 

# parms for data export
city = 'yyc'
frequency = 'daily'
date_range = '2020'
station_ID = '50430'
year = "2020"
month = "1"


# generate the csv_url
csv_url = 'https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={}&Year={}&Month={}&Day=1&time=&timeframe=2&submit=Download+Data'.format(station_ID, year, month)


# read in url contents with requests
req = requests.get(csv_url)
url_content = req.content

# open a csv with progamatic name
file_name = 'gc_{}_{}_weather_{}.csv'.format(city, frequency, date_range)
file_path = 'data_collection/data/{}'.format(file_name)
csv_file = open(file_path, 'wb')

# write to csv and close csv
weather_data = csv_file.write(url_content)
csv_file.close()

# use the below link to pull hourly data
#https://climate.weather.gc.ca/climate_data/hourly_data_e.html?hlyRange=1953-01-01%7C2012-07-12&dlyRange=1881-10-01%7C2012-07-11&mlyRange=1881-01-01%7C2012-07-01&StationID=2205&Prov=AB&urlExtension=_e.html&searchType=stnProv&optLimit=yearRange&StartYear=2010&EndYear=2021&selRowPerPage=100&Line=73&Month=1&Day=1&lstProvince=AB&timeframe=1&Year=2010