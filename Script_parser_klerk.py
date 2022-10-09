# Скрипт для парсинга данных с сайта Klerk
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

url_scrapping = 'https://www.klerk.ru/news/sort/month_best/page/'

# максимальное количество страниц
amount_pages = 47

# Обращаемся постранично
for p in range(amount_pages):

    url_accurate = url_scrapping + str(p + 1) + '/' # Формируем точный URL

    html_text_page = session.request('GET', url_accurate).text   # Получим данные одной страницы с новостями
    html_text_page_xml = BeautifulSoup(html_text_page, 'lxml')

    if not ( 'временно ограничен' in html_text_page ) :
        print("Скрапинг страницы №: %d" % (p + 1))

        header_all_ads_on_page = html_text_page_xml.find_all('article', class_ = 'feed-item feed-item--normal')
        data = []

        for i in range(len( header_all_ads_on_page) ):
            # выделим ссылку на новость
            link_poln = str( header_all_ads_on_page[i].find('a', class_ = 'feed-item__link feed-item-link__check-article') )
            symbol_start = link_poln.find('href=')
            symbol_end = link_poln.find('/">')
            link = 'https://www.klerk.ru' + link_poln[symbol_start+6 : symbol_end ] + '/'

            # Выделим номер новости
            number_news =  link_poln[symbol_start+16 : symbol_end ]
            header_news = str( header_all_ads_on_page[i].find('a', class_ = 'feed-item__link feed-item-link__check-article').text )
            header_news_clear = re.sub("[📒|⚡|🎤|🔥|❗|✋|;|👚|🍝|😁|📤|🍯|☎️|🙉|🐌|💸|✨|🚗|🐮|🍅|📄|✅|🔎|📜|🏦|👪|📞|👎|💥|✍️|👷|🎰|🙆|💣|📌|🚗|🚿|😱|💰|🚩|💻|❎|📈|👆|👯|📜]","",header_news)

            # Выделим время публикации
            time = str( header_all_ads_on_page[i].find('span', class_ = 'stats-block') )
            symbol_start2 = time.find('date=')
            symbol_end2 = time.find('></core')
            time_clear =  time[symbol_start2+6 : symbol_end2 -1 ]

            # Выделим краткое описание
            short_description = str( header_all_ads_on_page[i].find('div', class_ = 'feed-item__content').text ).strip()

            # Выделим рубрику
            rrr = header_all_ads_on_page[i].find('a', class_ = 'feed-item__rubric')
            if rrr != None :
                rubrication = str( rrr.text )
            else:
                rubrication = 'нет'

            # Выделим количество комментариев
            for_comments = str( header_all_ads_on_page[i].find('div', class_ = 'feed-item__footer-stat') )
            symbol_start3 = for_comments.find('comments-button')
            symbol_end3 = for_comments.find('#comments">')
            comments = for_comments[symbol_start3 +24 : symbol_end3 -25 ]

            # Выделим количество просмотров
            symbol_start4 = for_comments.find('core-count-format')
            symbol_end4 = for_comments.find('></core-count-format>')
            view = for_comments[symbol_start4 +25 : symbol_end4 -1 ]

            # Поместим данные в массив
            data.append([number_news, link, time_clear, rubrication, comments, view, header_news_clear, short_description])

        # Поместим данные в файл
        with open('links_with_short_descriptions.csv', 'a', encoding='utf-8', newline='') as f_object:
            writer_object = writer(f_object, delimiter=';')
            for r in range(len(header_all_ads_on_page)):
                writer_object.writerow(data[r])

            f_object.close()

    else:
        print('IP временно ограничен')

    sleep(randint(7,12))

print('Все страницы успешно обработаны')
