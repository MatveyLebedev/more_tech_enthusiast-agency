import fileinput
all_words = []

for line in fileinput.input(files=('words_bux_1.txt')):
    l = line
    l = l.split('—')
    word = l[0]
    word = word.replace('(', '')
    word = word.replace(')', '')
    if len(word) < 30:
        if word != '\n':
            word = word.lower()
            if word[-1] == ' ':
                word = word[0:-1]
            all_words.append(word)

for line in fileinput.input(files=('words_bux_2.txt')):
    l = line.replace('— ', '')
    if '(' in l:
        t1 = l.split('(')[0]
        if t1[-1] == ' ':
            t1 = t1[0:-1]
        t2 = l.split('(', 1)[1].split(')')[0]
        all_words.append(t1.lower())
        all_words.append(t2.lower())
    else:
        all_words.append(l[0])

for line in fileinput.input(files=('words_bux_3.txt')):
    if len(line) > 1:
        word = line.split('—')[0]
        if '\n' not in word:
            if '(' in word:
                t1 = word.split('(')[0]
                if t1[-1] == ' ':
                    t1 = t1[0:-1]
                t2 = word.split('(', 1)[1].split(')')[0]
                all_words.append(t1.lower())
                all_words.append(t2.lower())
            else:
                if word[-1] == ' ':
                    word = word[0:-1]
                all_words.append(word.lower())

n_all_words = []
for w in all_words:
    if len(w) > 1 and len(w) < 50:
        n_all_words.append(w)
all_words = n_all_words

all_words.extend(['Нетто', 'Котировка', 'Импорт', 'Дисконт', 'Валюта', 'Брутто'])
all_words = list(dict.fromkeys(all_words))
print(all_words)
print(len(all_words))

with open("all_bux_termins.txt", "w") as f:
    for w in all_words:
        f.write(w + "\n")
