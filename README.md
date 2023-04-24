Инструкция по запуску:
Скопировать репозиторий и запустить 'Programm_accountant.py' и 'Programm_director.py'
или
Открыть: https://colab.research.google.com/drive/1TNdZuMJjBHotCADEDz4GCMAg0E4TFbfd#scrollTo=x5V1DSqMEAlG

<img width="847" alt="image" src="https://user-images.githubusercontent.com/70165837/205015420-971da481-3ae7-4d3a-a718-6b267c7a5955.png">

В этом проэкте реализован алгоритм формирования профилтной ленты новостей для бухгалтеров и директоров и выявления трендов на основе словарей профессиональных терминов.
1. Парсинг источников данных с сайтов аудит it и клерк. (Script_parser_audit-it.py и 'Script_parser_klerk.py')
2. Парсинг словарей профессиональных терминов. ('bux_termin.py' и 'app_pop.py')
3. Выявление тренлов петем построения облоков слов. ('EDA+Выявление трендов.ipynb')
4. Формирование профильных лент новостей на основе облоков слов сформированных для трендов и содержании слов из словарей профессиональных терминов. ('Programm_accountant.py' и 'Programm_director.py')