#%%
import requests
from lxml import etree
from io import BytesIO

url = 'https://odws.hccg.gov.tw/001/Upload/25/opendataback/9059/457/fee97769-78c5-475b-bbe6-07f086f22b9e.xml'
res = requests.get(url)
file = BytesIO(res.content)
tree = etree.parse(file)
tree_xml=etree.tostring(tree, pretty_print=True,encoding='unicode')
# print(tree_xml)
datas = [i.text for i in tree.xpath('//月份 | //門票收入合計')]
month = datas[::2]
salary = datas[1::2]
income_dict = {}
for i in range(len(month)):
    if month[i] in income_dict:
        income_dict[f'{month[i]}-2'] = float(salary[i])
    else:
        income_dict[month[i]] = float(salary[i])

print(f'{max(income_dict, key=income_dict.get)}收入最高')

avg = sum(income_dict.values())/len(month)
print(f'平均營業額為: {avg:.2f}')

income_datas = [float(i.text) for i in tree.xpath('//現金門票收入 | //多卡通門票收入')]
cash_income = sum(income_datas[::2])
cartoon_income = sum(income_datas[1::2])
income_type = {
    '現金': cash_income,
    '卡通': cartoon_income
}
print(f'{max(income_type, key=income_type.get)}收入最多')

#%%
import requests
from lxml import html
years=input('輸入年分:')
url=f"https://www.truemovie.com/tairelease{years}.htm"
res=requests.get(url)
tree=html.fromstring(res.text)
month=tree.xpath('//font')
#%%
import requests
from bs4 import BeautifulSoup
years=input('輸入年分:')
url=f"https://www.truemovie.com/tairelease{years}.htm"
# url=f"https://www.truemovie.com/tairelease.htm"
res=requests.get(url)
res.encoding='big5'
bts=BeautifulSoup(res.text,'html.parser')
table=bts.select('div[align="left"] p')
month=bts.select('font b')
for i in range(len(table)):
    name=bts.select('td a')
    print(f'{i+1}月')
    for n in name:
        print(n.get_text().strip())
    print('='*25)
#%%
from selenium import webdriver
import time
from bs4 import BeautifulSoup
driver=webdriver.Chrome()
driver.get('https://www.imdb.com/title/tt1877830/?ref_=nv_sr_srsg_0')
content=driver.page_source
bts=BeautifulSoup(content,'lxml')
casts=bts.select('a[data-testid="title-cast-item__actor"]')
# print(casts)
casts_list=[i.get_text() for i in casts]
time.sleep(3)
print(driver.title)
driver.quit()