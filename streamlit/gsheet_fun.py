# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 15:37:42 2021

@author: JZ2018
"""

import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def Gsheet_main(sheet_id, sheet_range):
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'dk_id.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=sheet_id,
                                range=sheet_range).execute()
    values_input = result_input.get('values', [])

    if not values_input and not values_expansion:
        print('No data found.')


def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)
    
    cred = None

    if os.path.exists('token_write.pickle'):
        with open('token_write.pickle', 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open('token_write.pickle', 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        #return service
    except Exception as e:
        print(e)
        #return None
        
def Export_Data_To_Sheets(df, gsheetId, sheet_range):
    response_date = service.spreadsheets().values().append(
        spreadsheetId=gsheetId,
        valueInputOption='RAW',
        range=sheet_range,
        body=dict(
            majorDimension='ROWS',
            values=df.T.reset_index().T.values.tolist()[1:])
    ).execute()
    print('Sheet successfully Updated')
    
def Gsheet_Append(df, sheetid, sheet_range):
    Create_Service('dk_id.json', 'sheets', 'v4',['https://www.googleapis.com/auth/spreadsheets'])
    #dfnew = aeso_hpp[0:3]
    Export_Data_To_Sheets(df, sheetid, sheet_range)
    
def Gsheet_Download(sheet_id, sheet_range):
    Gsheet_main(sheet_id, sheet_range)
    df_output = pd.DataFrame(values_input[1:], columns=values_input[0])
    return df_output

def Gsheet_updateAll(df, sheet_id, sheet_range):
    Create_Service('dk_id.json', 'sheets', 'v4',['https://www.googleapis.com/auth/spreadsheets'])
    service.spreadsheets().values().clear(spreadsheetId=sheet_id,range=sheet_range).execute()
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        valueInputOption='RAW',
        range=sheet_range,
        body=dict(
            majorDimension='ROWS',
            values=df.T.reset_index().T.values.tolist())
    ).execute()
    print('Sheet successfully cleared and replaced')
