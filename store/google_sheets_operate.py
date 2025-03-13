import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'credentials-excel.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())
service = build('sheets', 'v4', http=httpAuth)
spreadsheetId = '1tKOgG4xD3KjLUboVh9VgXogui8jVAu0FFZxtqYpmMog'


def google_read_values():
    ranges = ["Main!A1:A1000000"]  #
    try:
        results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        return results['valueRanges'][0]['values']
    except:
        print("Warning! Empty excel file")
        return []


def google_insert_values(data: list, start_range: int):
    if start_range >= 999900:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetId,
            body={
                "requests": [
                    {'deleteDimension':
                         {'range':
                              {'sheetId': 0,
                               "dimension": "ROWS",
                               "startIndex": 1,
                               "endIndex": 1000001
                               }
                          }
                     }
                ]
            }).execute()
        start_range = 1

    end_range = start_range + len(data)
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId,
        range=f"Main!A{start_range}:I{end_range}",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={
            "values": data

        }
    ).execute()
