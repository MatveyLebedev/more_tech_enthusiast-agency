# Скрипт для парсинга данных с сайта audit-it
import pandas as pd
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


data_links = pd.read_csv('links_audit_it.csv', delimiter = ';')

for i in range(len(data_links)):
    # выделим ссылку на новость
    link = data_links.iloc[i]['link']

    html_text_ads = session.request('GET', link).text
    html_text_ads_xml = BeautifulSoup(html_text_ads, 'lxml')
    info_object_poln =  html_text_ads_xml.find('div', class_ = 'news-list')

    # Определяем время публикации
    symbol_start2 = str(html_text_ads_xml).find('<title>')
    symbol_end2 = str(html_text_ads_xml).find('</title>')
    time = str(html_text_ads_xml)[symbol_start2 +18 : symbol_end2 ]

    if not ( 'временно ограничен' in info_object_poln ) :
        print("Скрапинг страницы №: %d" % (i + 1))

        # Определяем заголовок новости
        header_news = info_object_poln.find_all('div', class_ = 'news-title-box')

        # Определяем краткое описание
        short_description = info_object_poln.find_all('span', class_ = 'text')

        for ii in range(len(short_description)):
            rrrr = str( short_description[ii] )
            symbol_start = rrrr.find('</span>')
            symbol_end = rrrr.find('<span class="wrap-options')

            short_description[ii] = rrrr[symbol_start +7 : symbol_end ]

        # Определяем количество просмотров
        view = info_object_poln.find_all('span', class_ = 'views')

    # Записываем данные в файл
    for t in range(len(short_description)):
        data = []
        data.append([time, int(view[t].text.replace('\xa0', '')), str(header_news[t].text).replace('t', '').replace('\n', ''), short_description[t].replace('\t', '').replace('\n', '') ] )
        with open('data_with_audit_it2.csv', 'a', encoding='utf-8', newline='') as f_object:
            writer_object = writer(f_object, delimiter=';')
            writer_object.writerow(data[0])
            f_object.close()

    sleep(randint(5,7))

print('Все страницы успешно обработаны')
