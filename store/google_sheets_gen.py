import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'credentials-excel.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())
service = build('sheets', 'v4', http=httpAuth)

spreadsheet = service.spreadsheets().create(body={
    'properties': {'title': 'cpackatom-dashboard-excel', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Main',
                               'gridProperties': {'rowCount': 1000000, 'columnCount': 9}}}]
}).execute()
spreadsheetId = spreadsheet['spreadsheetId']
print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)
