from time import sleep
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from parsel import Selector


def getCookie():
    url="http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201040102"
    response = requests.Session().get(url)
    return response.cookies
    
def getStockData(standart_code, company_code,company_name,cookie):
    stock_url="http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    formdata={
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT02101',
        'locale': 'ko_KR',
        'tboxisuCd_finder_stkisu0_3': company_code+'/'+company_name,
        'isuCd': 'KR7'+company_code,
        'isuCd2': 'KR7'+company_code,
        'codeNmisuCd_finder_stkisu0_3': company_name,
        'param1isuCd_finder_stkisu0_3': 'ALL',
        'csvxls_isNo': 'false',
    }
    
    result = requests.post(stock_url, data=formdata ,cookies=cookie).json()
    return result
    

scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]
json_file_name = 'gsheet_auth.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1W999-qi_DTlMrQA1r9bBd_6-yXBSpEzq4mOIxCvIF0U/edit#gid=126783781'
# 스프레스시트 문서 가져오기 
doc = gc.open_by_url(spreadsheet_url)
# 시트 선택하기
worksheet = doc.worksheet('시트2')

standard_codes=worksheet.col_values(1)
company_codes=worksheet.col_values(2)
company_names=worksheet.col_values(3)

cookie = getCookie()

for company in standard_codes:
    cell_index=standard_codes.index(company)
    
    if(cell_index ==0) :
        continue
    
    data =getStockData(standard_codes[cell_index], company_codes[cell_index],company_names[cell_index],cookie)
    sleep(5)
    print(data)