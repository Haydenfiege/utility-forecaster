'''
    File name: historic_weather_scrape.py
    Author: Hayden Fiege
    Date created: 03/01/2021
    Date last modified: 03/06/2021
    Python Version: 3.8.8
'''

import requests 

# dictionary for weather stations IDs
weather_stations = {
  "calgary": "50430",
  "edmonton": "27214",
  "fort_mac": "49490"
}

# parms for data export
city = 'calgary'
year_start = '2020'
month_start = "1"
year_end = '2020'
month_end = '3'

month = month_start
year = year_start

# loop through the selected data range and download the historic hourly weather data for the selected city
while year in range(year_start,year_end + 1):
    month = 1
    while month in range(1, 13):
        
        # generate the url for the requested csv
        csv_url = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={}&Year={}&Month={}&Day=1&time=LST&timeframe=1&submit=Download+Data".format(weather_stations[city],year,month)
        
        # read in url contents with requests
        req = requests.get(csv_url)
        url_content = req.content

        # open a csv with progamatic name
        file_name = 'gc_{}_hourly_weather_{}_{}.csv'.format(city, year, month)
        file_path = 'data_collection/data/{}'.format(file_name)
        csv_file = open(file_path, 'wb')

        # write to csv and close csv
        weather_data = csv_file.write(url_content)
        csv_file.close()
        if year == year_end and month == month_end:
            break
        else:
            month += 1
    year += 1


