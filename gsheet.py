from time import sleep
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from parsel import Selector
import pandas as pd
from urllib import parse


def getFnguide(code):
    get_param = {
        'pGB': 1,
        'gicode': 'A%s' % (code),
        'cID': '',
        'MenuYn': 'Y',
        'ReportGB': '',
        'NewMenuID': 101,
        'stkGb': 701,
    }
    get_param = parse.urlencode(get_param)
    url = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?%s" % (get_param)
    try:
        tables = pd.read_html(url, header=0)
        return(tables)
    except:
        print('error:'+url)
        return pd.DataFrame()


def getStockData(standart_code):
    stock_url = f"https://api.odcloud.kr/api/GetStockSecuritiesInfoService/v1/getStockPriceInfo?numOfRows=1&pageNo=1&resultType=json&isinCd={standart_code}&serviceKey=4stGtGDzcC%2BEnLJ8wrUf1LEmKI%2FnqULG07zQMb8LnAKGkMvgUEUcgzN7537sAOj9R6YiWHGrlQonCC8TpTzPfA%3D%3D"
    result = requests.get(stock_url)
    return result.json()


def writeSheet(worksheet, data, lineNumber):
    print(data)
    worksheet.update_cell(lineNumber, 4, data['clpr'])
    worksheet.update_cell(lineNumber, 5, data['rowprice'])
    worksheet.update_cell(lineNumber, 7, data['per'])
    worksheet.update_cell(lineNumber, 8, data['pbr'])
    worksheet.update_cell(lineNumber, 9, data['roe'])
    worksheet.update_cell(lineNumber, 11, data['suneeick'])
    worksheet.update_cell(lineNumber, 12, data['maechul'])
    worksheet.update_cell(lineNumber, 13, data['buchae_rto'])
    worksheet.update_cell(lineNumber, 14, data['baedang'])
    worksheet.update_cell(lineNumber, 15, data['sigatotal'])


def dictLast(data):
    if(len(data) > 0):
        return data[-1]
    else:
        return ""


scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]
json_file_name = 'gsheet_auth.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    json_file_name, scope)
gc = gspread.authorize(credentials)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1W999-qi_DTlMrQA1r9bBd_6-yXBSpEzq4mOIxCvIF0U/edit#gid=126783781'
# 스프레스시트 문서 가져오기
doc = gc.open_by_url(spreadsheet_url)
# 시트 선택하기
worksheet = doc.worksheet('시트2')

standard_codes = worksheet.col_values(1)
stock_codes = worksheet.col_values(2)

for company in stock_codes:
    cell_index = stock_codes.index(company)
    if(cell_index == 0):
        continue

    fnguide = getFnguide(company)
    data = {}

    try:
        price = fnguide[0]
        data['clpr']= price.columns.values[1].split('/')[0] if price.columns.values[1] != '' else ''
        rowprice = price.iloc[0][1:2].tolist()
        rowprice = rowprice[0].split('/')[1] if rowprice[0] != '' else ''
        data['rowprice'] = rowprice
        data['sigatotal'] = price.iloc[3][1:2].tolist()[0]
    except:
        print("error:"+company)

    try:
        table = fnguide[11].dropna(axis=1)
        data['maechul'] = dictLast(table.iloc[1][1:6].tolist())
        data['suneeick'] = dictLast(table.iloc[4][1:6].tolist())
        data['buchae_rto'] = dictLast(table.iloc[13][1:6].tolist())
        data['baedang'] = dictLast(table.iloc[25][1:6].tolist())
        data['roe'] = dictLast(table.iloc[18][1:6].tolist())
        data['per'] = dictLast(table.iloc[22][1:6].tolist())
        data['pbr'] = dictLast(table.iloc[23][1:6].tolist())
        # data =getStockData(company)
        # data = data['response']['body']['items']['item'][0]
        writeSheet(worksheet,data,cell_index+1)
    except:
        print("error:"+company)

    writeSheet(worksheet,data,cell_index+1)
    sleep(3)
