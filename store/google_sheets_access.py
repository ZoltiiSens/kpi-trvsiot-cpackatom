import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'credentials-excel.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())
spreadsheetId = '1tKOgG4xD3KjLUboVh9VgXogui8jVAu0FFZxtqYpmMog'

driveService = build('drive', 'v3', http=httpAuth)
access = driveService.permissions().create(
    fileId=spreadsheetId,
    body={'type': 'user', 'role': 'writer', 'emailAddress': 'example_email@gmail.com'},
    fields='id'
).execute()
