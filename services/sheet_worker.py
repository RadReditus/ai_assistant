from concurrent.futures.thread import _worker
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from services.logger_func import logger


dotenv_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(dotenv_path)

def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if not value:
        raise ValueError(logger.error(f"[get_env_variable action]: ❌ Ошибка: {var_name} не задан в .env файле!"))
    return value

DEBUG = os.getenv("DEBUG", "False")
SERVICE_ACCOUNT_FILE = get_env_variable("GOOGLE_SHEET_DATAS" if DEBUG != 'True' else "TEST_GOOGLE_SHEET_DATAS")
SPREADSHEET_ID = get_env_variable("GOOGLE_SPREADSHEET_ID" if DEBUG != 'True'else "TEST_GOOGLE_SPREADSHEET_ID")
SCOPES_ENV = get_env_variable("SCOPES" if DEBUG != 'True'else "TEST_SCOPES")
SCOPES = [str(SCOPES_ENV)]
MAIN_TABLE: str = 'general_info_clients'

class SheetWorker:
    def __init__(self):
        self.creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.spreadsheet_id = SPREADSHEET_ID


    def write_info_to_sheets(self, name, phone, country):

        sheet_info = self.get_sheet_data(MAIN_TABLE, "A1:Z1000")

        if not isinstance(sheet_info, list) or not sheet_info:
            logger.warning("[write_info_to_sheets action]: ⚠️ Таблица пустая, идёт заполнение...")
            sheet_info = []

        headers = ['ФИО', 'Номер телефона', 'Страна интереса']

        first_row = sheet_info[0] if sheet_info else []
        add_headers = first_row != headers

        new_data = [[name, str(phone), country]]

        data_to_write = [headers] + new_data if add_headers else new_data

        start_row = len(sheet_info) + 1 if sheet_info else 1

        logger.info(f"Используемый range: {MAIN_TABLE}!A{start_row}")

        sheet = self.service.spreadsheets()
        request = sheet.values().append( 
            spreadsheetId=self.spreadsheet_id,
            range=f'{MAIN_TABLE}!A{start_row}',  
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS', 
            body={'values': data_to_write}
        ).execute()

        self.make_background(start_row)
        logger.info(f"[write_info_to_sheets action]: ✅ Данные успешно загружены! Обновлено {request.get('updates').get('updatedCells')} ячеек.")
        return ''

    def get_sheet_data(self, sheet_name: str, cell_range: str) -> list | str:
        sheet = self.service.spreadsheets()
        range_name = f"{sheet_name}!{cell_range}"

        try:
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            values = result.get("values", [])

            filtered_values = [
                [cell for cell in row if cell.strip() and cell != ""] 
                for row in values if any(cell.strip() for cell in row if isinstance(cell, str))
            ]

            return filtered_values if filtered_values else logger.warning("[get_sheet_data action]: Данных нет")
        except HttpError as e:
            return logger.critical(f"[get_sheet_data action]: ❌ Ошибка HTTP при получении данных: {e}")
        except Exception as e:
            return logger.critical(f"[get_sheet_data action]: ❌ Неизвестная ошибка: {e}")
        

    def make_background(self, end_bg_str: int):
        light_green = {
            "red": 144 / 255,
            "green": 238 / 255,
            "blue": 144 / 255
            }

        gray = {
            "red": 0.83,
            "green": 0.83,
            "blue": 0.83
        }

        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 3
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": light_green
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 1,
                        "endRowIndex": int(end_bg_str),
                        "startColumnIndex": 0,
                        "endColumnIndex": 3
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": gray
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            }
        ]

        body = {
            "requests": requests
        }

        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        ).execute()

        print(logger.info("[make_background action]: Первая строка окрашена в зелёный, указанные строки в серый."))
        return response
'''
if __name__ == "__main__":
    worker = SheetWorker()


    worker.write_info_to_sheets()


    data = worker.get_sheet_data("general_info_clients", "A1:Z1000")
    print(f"📄 Данные из Google Sheets: --- {len(data) - 1 }")
    for row in data:
        print(row)'
'''