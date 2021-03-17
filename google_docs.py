import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from settings import CREDENTIALS_FILE, spreadsheetId
import pandas as pd
import datetime

class GoogleDoc:

    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
        self.excel_sheets = self.get_excel_lists()

    def get_excel_lists(self):
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
        sheetList = spreadsheet.get('sheets')
        return {sheet['properties']['index']: sheet['properties']['title'] for sheet in sheetList}

    def get_list_values(self, list_name):
        list_name_to_num = {
            'услуги': 0,
            'лист машин': 1,
            'ТО': 2
        }
        ranges = [self.excel_sheets[list_name_to_num[list_name]]]

        results = self.service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        res = pd.DataFrame(sheet_values[1:], columns=sheet_values[0])
        return res

    def spend_service(self, car, serv, price, walk, who_changed):
        df = self.get_list_values('ТО')
        row_num = df.shape[0] + 2  # +1 за заголовок +1 за отсчет с 0
        now = datetime.datetime.now()
        body = {
            "valueInputOption": "USER_ENTERED",
            'data': [{
                'range': f'{self.excel_sheets[2]}!{row_num}:{row_num}',
                'values': [[now.strftime("%d.%m.%Y"), car, serv, price, walk,  who_changed]]
                 }]
        }
        result = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=body
        ).execute()

        df = self.get_list_values('услуги')
        row_num = df.index[df[df.columns[0]] == serv].tolist()[0]
        serv_to_change = df.iloc[row_num]
        body = {
            "valueInputOption": "USER_ENTERED",
            'data': [{
                'range': f'{self.excel_sheets[0]}!{row_num+2}:{row_num+2}',
                'values': [[serv_to_change[0], int(serv_to_change[1]) - 1]]
            }]
        }
        result = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=body
        ).execute()
        return result

if __name__ == '__main__':
    Gd = GoogleDoc()
    l = Gd.get_excel_lists()
    row = ['123123ыв', 'лайтбокс', '100', '100', 'Иван Петрович']
    res = Gd.spend_service(*row)
    x = 1

