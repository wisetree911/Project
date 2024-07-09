import logging # для логирования
import gspread
from config import SPREADSHEET_URL
logging.basicConfig(level=logging.INFO)


def get_cell_value(row: int, col: int) -> str:
    # авторизация с помощью json файла "service_account.json"
    gc = gspread.service_account("service_account.json")
    sh = gc.open_by_url(SPREADSHEET_URL)
    ws = sh.sheet1
    value = ws.cell(row, col).value
    logging.info(f" Значение из таблицы получено")
    return value


def add_to_table_A2(value):
    # авторизация с помощью json файла "service_account.json"
    gc = gspread.service_account("service_account.json")
    # открываем таблицу по ссылке
    sh = gc.open_by_url(SPREADSHEET_URL)
    # получаем первый лист таблицы
    ws = sh.sheet1
    # считаем, сколько строк в столбце В уже занято и записываем в свободной строке столбца В значение "value"
    rows_in_col = ws.col_values(2)
    ws.update_cell(row=len(rows_in_col)+1, col=2, value=value)
    logging.info(f" Значение {value} добавлено в столбец B")
