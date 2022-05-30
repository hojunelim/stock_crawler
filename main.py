import requests

from parsel import Selector
from urllib.parse import quote, unquote

formdata = {
    'method': 'searchCorpList',
    'pageIndex': '1',
    'currentPageSize': '15',
    'location': 'all',
    'orderMode': '3',
    'orderStat': 'D',
}
r = requests.post('https://kind.krx.co.kr/corpgeneral/corpList.do', data=formdata)
selector = Selector(text=r.text)
for tr in selector.xpath('//table/tbody/tr'):
    name = tr.xpath('td/a/text()').get(default='')
    r2 = requests.post('https://kind.krx.co.kr/common/searchcorpname.do', data={
        'method': 'searchCorpNameJson',
        'searchCorpName': name.strip(),
    })
    data = r2.json()

    formdata = {
        'searchCorpName': name.strip(),
        'method': 'searchTotalInfo',
        'kisComCd': data[0]['kiscomcd'],
        'isurCd': data[0]['isurcd'],
        'repIsuCd': data[0]['repisucd'],
    }
    rr = requests.post('https://kind.krx.co.kr/corpdetail/totalinfo.do', data=formdata)
    selector = Selector(text=rr.text)
    price = float(selector.xpath('//table[2]/tbody/tr/td/strong/text()').get(default='').replace(',', ''))

    formdata = {
        'searchCorpName': name.strip(),
        'companyNM': name.strip(),
        'searchCodeType': '',
        'method':'searchStockStatus',
        'isurCd': data[0]['isurcd'],
        'repIsuCd': data[0]['repisucd'],
        'tabMenu': '1',
        'mode': '',
    }
    r = requests.post('https://kind.krx.co.kr/corpdetail/stockstatus.do', data=formdata)
    selector = Selector(text=r.text)
    total_count = float(selector.xpath('//table[1]/tbody/tr[2]/td[2]/text()').get(default='').replace(',', ''))
    print(f'{name}: 주식가격: {price}, 주식발행수: {total_count}, 시총: {price * total_count}')