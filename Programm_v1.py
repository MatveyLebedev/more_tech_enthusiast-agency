import pymorphy2
import pandas as pd
import string

import ssl
import requests
import pickle
from bs4 import BeautifulSoup
import time
import math
from csv import writer
from random import randint
from time import sleep
import re



from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_

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



morph = pymorphy2.MorphAnalyzer()

# Выгружаем словарь №1
data_dict_1 = pd.read_csv('trend_sum.csv', delimiter = ',')


link = 'https://www.klerk.ru/news/'
html_text_ads = session.request('GET', link).text
html_text_ads_xml = BeautifulSoup(html_text_ads, 'lxml')

header_all_ads_on_page = html_text_ads_xml.find_all('article', class_ = 'feed-item feed-item--normal')
data = []

for i in range(len( header_all_ads_on_page) ):
    # for i in range(1):
    link_poln = str( header_all_ads_on_page[i].find('a', class_ = 'feed-item__link feed-item-link__check-article') )
    # print('link_poln = ', link_poln)
    # print('')
    symbol_start = link_poln.find('href=')
    # print('symbol_start = ', symbol_start)
    symbol_end = link_poln.find('/">')
    # print('symbol_end = ', symbol_end)
    link = 'https://www.klerk.ru' + link_poln[symbol_start+6 : symbol_end ] + '/'
    number_news =  link_poln[symbol_start+16 : symbol_end ]
    header_news = str( header_all_ads_on_page[i].find('a', class_ = 'feed-item__link feed-item-link__check-article').text )
    header_news_clear = re.sub("[📒|⚡|🎤|🔥|❗|✋|;|👚|🍝|😁|📤|🍯|☎️|🙉|🐌|💸|✨|🚗|🐮|🍅|📄|✅|🔎|📜|🏦|👪|📞|👎|💥|✍️|👷|🎰|🙆|💣|📌|🚗|🚿|😱|💰|🚩|💻|❎|📈|👆|👯|📜]","",header_news)

    time = str( header_all_ads_on_page[i].find('span', class_ = 'stats-block') )
    symbol_start2 = time.find('date=')
    # print('symbol_start = ', symbol_start)
    symbol_end2 = time.find('></core')
    # print('symbol_end = ', symbol_end)
    time_clear =  time[symbol_start2+6 : symbol_end2 -1 ]


    short_description = str( header_all_ads_on_page[i].find('div', class_ = 'feed-item__content').text ).strip()

    rrr = header_all_ads_on_page[i].find('a', class_ = 'feed-item__rubric')
    if rrr != None :
        rubrication = str( rrr.text )
    else:
        rubrication = 'нет'

    data.append([number_news, link, time_clear, rubrication, header_news_clear, short_description])


data_for_analysis = data_dict_1.copy()


# Заполняем таблицу нолями. Колонки означают статьи для анализа
for new in range(len(data)):
    name = 'News'+str(new)
    data_for_analysis.loc[:, name] = 0

# print(data_for_analysis)

# Для форматирования
tab = str.maketrans(string.punctuation, ' ' * len(string.punctuation))


# Заполянем таблицу количеством вхождений
for i in range(len(data)):
# for i in range(0,1):
    name = 'News'+str(i)
    text_header = data[i][4]
    # print('text_header = ', text_header)
    text_description = data[i][5]
    # print('text_description = ', text_description)
    text = text_header + ' ' +text_description
    res = text.translate(tab).split()
    res_normal_form = []
    for ii in range(len(res)):
        res_normal_form.append(morph.parse(res[ii])[0].normal_form)

    for iii in range(len(res_normal_form)):
        now_word = res_normal_form[iii]
        data_for_analysis.loc[data_for_analysis['word'] == now_word, name] = data_for_analysis.loc[data_for_analysis['word'] == now_word][name] + 1



# Создаем новую таблицу, куда будут записываться формулы

weight = 'num'

data_dict = {}
df_marks = pd.DataFrame(data_dict)

for i in range(len(data)):
# for i in range(0,3):
    name = 'News'+str(i)
    stroki = data_for_analysis.loc[data_for_analysis[name] > 0]
    sum_rating = 0.0

    for ii, rr in stroki.iterrows():
        # print(ii)
        # print(rr[weight])
        sum_rating = sum_rating + ( rr[weight] * rr[name] )

    # print('News = ', name, ' sum_rating = ', sum_rating)
    new_row = {'Name' : name, 'Rating' : sum_rating}
    df_marks = df_marks.append(new_row, ignore_index=True)



sorted_df = df_marks.sort_values(by='Rating', ascending=False)
print(sorted_df)
top_news = sorted_df[:6]



# print(top_news.index)

text_header_top1 = data[top_news.index[0]][4]
text_header_top2 = data[top_news.index[1]][4]
text_header_top3 = data[top_news.index[2]][4]

link_top1 = data[top_news.index[0]][1]
link_top2 = data[top_news.index[1]][1]
link_top3 = data[top_news.index[2]][1]

print('Новости для бухгалтера:')

print('Новость 1 : ', text_header_top1)
print('Ссылка : ', link_top1)
print('')


print('Новость 2 : ', text_header_top2)
print('Ссылка : ', link_top2)
print('')

print('Новость 3 : ', text_header_top3)
print('Ссылка : ', link_top3)
print('')


dir_header_top1 = data[top_news.index[3]][4]
dir_header_top2 = data[top_news.index[4]][4]
dir_header_top3 = data[top_news.index[5]][4]

dir_link_top1 = data[top_news.index[3]][1]
dir_link_top2 = data[top_news.index[4]][1]
dir_link_top3 = data[top_news.index[5]][1]

print('')
print('')
print('')

print('Новости для директора:')

print('Новость 1 : ', dir_header_top1)
print('Ссылка : ', dir_link_top1)
print('')


print('Новость 2 : ', dir_header_top2)
print('Ссылка : ', dir_link_top2)
print('')

print('Новость 3 : ', dir_header_top3)
print('Ссылка : ', dir_link_top3)
print('')






# print(res_normal_form)

# print(data_for_analysis['News0'])






# df.loc[df['column_name'] == some_value]






'''
for r in range(len(data)):
    print(data[r])
    print()
    print()








p = morph.parse('яблони')[0]


p = p.normal_form
print(p)



tab = str.maketrans(string.punctuation, ' ' * len(string.punctuation))

text = 'Министерство цифрового развития, связи и массовых коммуникаций предлагает создание реестра согласий на обработку персональных данных с возможность их отзыва через интернет-портал Госуслуги, сообщает ведомство в своем Telegram-канале...'

res = text.translate(tab).split()
res_normal_form = []

for i in range(len(res)):
    res_normal_form.append(morph.parse(res[i])[0].normal_form)




print(res)
print()
print(res_normal_form)

'''
