#Импортируем необходимые библиотеки
import pymorphy2
import pandas as pd
import string
import ssl
import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_

# словарь
pach = 'trend_sum_dir (1).csv'

# Выполняем подключение к сайту Клерк

CIPHERS = """ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:AES256-SHA"""

class TlsAdapter(HTTPAdapter):

    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TlsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context(ciphers=CIPHERS, cert_reqs=ssl.CERT_REQUIRED, options=self.ssl_options)
        self.poolmanager = PoolManager(*pool_args, ssl_context=ctx, **pool_kwargs)

session = requests.session()
adapter = TlsAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
session.mount("https://", adapter)

# Создаем объект библиотеки pymorphy2
morph = pymorphy2.MorphAnalyzer()

# Выгружаем словарь, в котором хранятся слова и веса
data_dict_1 = pd.read_csv(pach, delimiter = ',')
# Указываем, в каком столбце находятся веса
weight = 'num'

link = 'https://www.klerk.ru/news/'
html_text_ads = session.request('GET', link).text
html_text_ads_xml = BeautifulSoup(html_text_ads, 'lxml')

header_all_ads_on_page = html_text_ads_xml.find_all('article', class_ = 'feed-item feed-item--normal')
data = []

for i in range(len( header_all_ads_on_page) ):

    link_poln = str( header_all_ads_on_page[i].find('a', class_ = 'feed-item__link feed-item-link__check-article') )
    symbol_start = link_poln.find('href=')
    symbol_end = link_poln.find('/">')
    link = 'https://www.klerk.ru' + link_poln[symbol_start+6 : symbol_end ] + '/'

    number_news =  link_poln[symbol_start+16 : symbol_end ]
    header_news = str( header_all_ads_on_page[i].find('a', class_ = 'feed-item__link feed-item-link__check-article').text )
    header_news_clear = re.sub("[📒|⚡|🎤|🔥|❗|✋|;|👚|🍝|😁|📤|🍯|☎️|🙉|🐌|💸|✨|🚗|🐮|🍅|📄|✅|🔎|📜|🏦|👪|📞|👎|💥|✍️|👷|🎰|🙆|💣|📌|🚗|🚿|😱|💰|🚩|💻|❎|📈|👆|👯|📜]","",header_news)

    time = str( header_all_ads_on_page[i].find('span', class_ = 'stats-block') )
    symbol_start2 = time.find('date=')
    symbol_end2 = time.find('></core')
    time_clear =  time[symbol_start2+6 : symbol_end2 -1 ]


    short_description = str( header_all_ads_on_page[i].find('div', class_ = 'feed-item__content').text ).strip()

    rrr = header_all_ads_on_page[i].find('a', class_ = 'feed-item__rubric')
    if rrr != None :
        rubrication = str( rrr.text )
    else:
        rubrication = 'нет'

    data.append([number_news, link, time_clear, rubrication, header_news_clear, short_description])

data_for_analysis = data_dict_1.copy()

# Заполняем таблицу нолями. Колонки означают новости для анализа
for new in range(len(data)):
    name = 'News'+str(new)
    data_for_analysis.loc[:, name] = 0

# Для форматирования
tab = str.maketrans(string.punctuation, ' ' * len(string.punctuation))

# Заполянем таблицу количеством вхождений
for i in range(len(data)):
    name = 'News'+str(i)
    text_header = data[i][4]
    text_description = data[i][5]
    text = text_header + ' ' +text_description
    res = text.translate(tab).split()
    res_normal_form = []
    for ii in range(len(res)):
        res_normal_form.append(morph.parse(res[ii])[0].normal_form)

    for iii in range(len(res_normal_form)):
        now_word = res_normal_form[iii]
        data_for_analysis.loc[data_for_analysis['word'] == now_word, name] = data_for_analysis.loc[data_for_analysis['word'] == now_word][name] + 1

# Создаём DataFrame, в котором будем хранить оценки анализируемых статей
data_dict = {}
df_marks = pd.DataFrame(data_dict)

for i in range(len(data)):
    name = 'News'+str(i)
    stroki = data_for_analysis.loc[data_for_analysis[name] > 0]
    sum_rating = 0.0

    for ii, rr in stroki.iterrows():
        sum_rating = sum_rating + ( rr[weight] * rr[name] )

    new_row = {'Name' : name, 'Rating' : sum_rating}
    df_marks = df_marks.append(new_row, ignore_index=True)

# Произведем ранжирование
sorted_df = df_marks.sort_values(by='Rating', ascending=False)
# print(sorted_df)
top_news = sorted_df[:3]

text_header_top1 = data[top_news.index[0]][4]
text_header_top2 = data[top_news.index[1]][4]
text_header_top3 = data[top_news.index[2]][4]

link_top1 = data[top_news.index[0]][1]
link_top2 = data[top_news.index[1]][1]
link_top3 = data[top_news.index[2]][1]

print('Новости для директора:')

print('Новость 1 : ', text_header_top1)
print('Ссылка : ', link_top1)
print('')

print('Новость 2 : ', text_header_top2)
print('Ссылка : ', link_top2)
print('')

print('Новость 3 : ', text_header_top3)
print('Ссылка : ', link_top3)
print('')

# выводим тренды
dict_copy = data_dict_1.copy()
sorted_dict = dict_copy.sort_values(by=weight, ascending=False)
top_trends = sorted_dict[:3].to_numpy()
print('Тренды: ')
for i in range(len(top_trends)):
    now_trend = top_trends[i][1]
    print(now_trend)
