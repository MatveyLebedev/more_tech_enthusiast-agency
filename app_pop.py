import fileinput
alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
all_words = []

for line in fileinput.input(files=('popular_words_1.txt', 'popular_words_2.txt', 'popular_words_3.txt')):
    word = ''
    for letter in line:
        if letter in alphabet:
            word += letter
    all_words.append(word)

all_words = list(dict.fromkeys(all_words))
print(len(all_words))
print(all_words)

with open("all_pop_words.txt", "w") as f:
    for item in all_words:
        f.write(item + "\n")
