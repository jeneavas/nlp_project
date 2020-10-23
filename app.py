from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import pandas as pd
import numpy as np
import re
import pymorphy2
from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()


app = Flask(__name__)


import pandas as pd
import numpy as np
import re
import time
import pymorphy2
from pymorphy2 import MorphAnalyzer
import sqlite3

# !wget http://download.cdn.yandex.net/mystem/mystem-3.0-linux3.1-64bit.tar.gz
# !tar -xvf mystem-3.0-linux3.1-64bit.tar.gz
# !cp mystem /root/.local/bin/mystem
# import pymystem3

####Код Алены
with open('corpus.txt', encoding='utf-8') as f:
    line = f.read()
flag = 0
import re

line = re.sub(' \n', '\n', line)

corp = []
sents = line.split('\n\n')
for sent in sents:
    chunks = sent.split('\n')
    if len(chunks) == 5:
        l = []
        l.append(chunks[0])
        lexemes = chunks[1].split(' ')
        l.append(lexemes)
        poses = chunks[2].split(' ')
        l.append(poses)
        forms = chunks[3].split(' ')
        l.append(forms)
        l.append(chunks[4])
        corp.append(l)


def unify(tag):
    unifier = {
        'ADJF': 'A',
        'ADJS': 'A',
        'NOUN': 'S',
        'COMP': 'ADV',
        'VERB': 'V',
        'INFN': 'V',
        'PRTF': 'V',
        'PRTS': 'V',
        'GRND': 'V',
        'NUMR': 'NUM',
        'ADVB': 'ADV',
        'NPRO': 'SPRO',
        'PRED': 'ADV',
        'PREP': 'PR',
        'CONJ': 'CONJ',
        'PRCL': 'PART',
        'INTJ': 'INTJ'
    }
    return (unifier[tag])


morph = MorphAnalyzer()
poses = ['A', 'ADV', 'ADVPRO', 'ANUM', 'APRO', 'COM', 'CONJ', 'INTJ', 'NUM', 'PART', 'PR', 'S', 'SPRO', 'V']
# lists = [['Мама мыла раму моющим средством.', ['мама', 'мыть', 'рама', 'моющий', 'средство'], ['NOUN', 'VERB', 'NOUN', 'ADJ', 'NOUN'], 'Василий Ключевский - История Государства Российского. 1889'],
# ['Падая с дерева, кошка совершила сальто.', ['падать', 'с', 'дерево', 'кошка', 'совершить', 'сальто'], ['VERB', 'PREP', 'NOUN', 'NOUN', 'VERB', 'NOUN'], 'Елизавета Клыкова - Фанфик про порочную связь кота Гермионы и совы Букли. 2014'],
# ['Я прыгнул с зеленым парашютом, а очнулся с переломом.', ['я', 'прыгать', 'с', 'зеленый', 'парашют', 'а', 'очнуться', 'c', 'перелом'], ['PRON', 'VERB', 'PREP', 'ADJ', 'NOUN', 'PREP', 'VERB', 'PREP', 'NOUN'], 'Иван Петров - Основы экстрима. 2003']]
df = pd.DataFrame(corp)
#print(df)
sent = df[0].tolist()
lemm = df[1].tolist()
poss = df[2].tolist()
slova = df[3].tolist()
avtors = df[4].tolist()


#Код Семена
def split_entities (string, flag):
    if string == '':  # самоеновое
        flag += 1  # самоеновое
        output = 0
    else:
        if '+' in string:
            w, pos = re.split('\+', string)
            if w[0] == '\"' and w[-1] == '\"':
                word = 'NaN'
                slov_form = w[1:-1]
                if slov_form.isalpha()  == False: #новое
                    flag += 1 #новое
                if pos not in poses: #новое
                    flag += 1 #новое
            else:
                slov_form = 'NaN'
                if pos not in poses: #новое
                    flag += 1 #новое
                if w.isalpha()  == False: #новое
                    flag += 1 #новое
                for a in morph.parse(w.lower()):
                    if unify(str(a.tag)[0:4]) == pos:
                        word = a.normal_form
        elif string not in poses:
            if string[0] == '\"' and string[-1] == '\"':
                word = 'NaN'
                slov_form = string[1:-1]
                if slov_form.isalpha()  == False: #новое
                    flag += 1 #новое
            else:
                slov_form = 'NaN'
                if string.isalpha()  == False: #новое
                    flag += 1 #новое
                word = morph.parse(string.lower())[0].normal_form # проверка на пос
            pos = 'NaN'
        else:
            word = 'NaN'
            slov_form = 'NaN'
            pos = string
            if pos not in poses: #новое
                flag += 1 #новое
        output = (word, pos, slov_form)
    return(output, flag) #новое


def create_tuple(index, row):
    c = [(lemm[row][index], poss[row][index], slova[row][index])]
    try:
        c.append((lemm[row][index + 1], poss[row][index + 1], slova[row][index + 1]))
    except:
        q = 'ok'
    try:
        c.append((lemm[row][index + 2], poss[row][index + 2], slova[row][index + 2]))
    except:
        q = 'ok'
    if len(c) < 3:
        c.append(('NaN', 'NaN', 'NaN'))
        if len(c) < 3:
            c.append(('NaN', 'NaN', 'NaN'))
    return ([tuple(c[0:3]), row])


def count_entities(string):
  result = re.findall(' ', string)
  a = len(result) + 1
  entities = re.split(' ', string)
  return(a, entities)


def compare(a, b):
  if ((a[0][0] == b[0][0] or a[0][0] == 'NaN') and ((a[0][1] == b[0][1] or a[0][1] == 'NaN')) and
      (a[1][0] == b[1][0] or a[1][0] == 'NaN') and ((a[1][1] == b[1][1] or a[1][1] == 'NaN')) and
      (a[2][0] == b[2][0] or a[2][0] == 'NaN') and ((a[2][1] == b[2][1] or a[2][1] == 'NaN')) and
      (a[0][2] == b[0][2] or a[0][2] == 'NaN') and ((a[1][2] == b[1][2] or a[1][2] == 'NaN')) and
      (a[2][2] == b[2][2] or a[2][2]== 'NaN')):
    return('TRUE')
  else:
    return("FALSE")


def search_function(string):
    flag = 0
    #часть с бд
  #import sqlite3
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS results(id integer primary key,sentence text, author text)")
    #time.sleep(2)
    # c.execute("INSERT INTO results(sentence, author) VALUES ('привет', 'пока')")
    c.execute("DELETE FROM results")

    #print('hello')
    number, entities = count_entities(string)
    input = []
    if number > 3:  # самоеновое
        flag += 1  # самоеновое
    for enty in entities:
      d, flag = split_entities(enty, flag)
      input.append(d)
    if len(input) < 3:
      input.append(('NaN', 'NaN', 'NaN'))
    if len(input) < 3:
      input.append(('NaN', 'NaN', 'NaN'))
    input = tuple(input)
    #print(input)
    possible_results = []
    if input[0][0] is not 'NaN':
      for a in range(0, len(lemm), 1):
        if input[0][0] in lemm[a]:
          indexes = [i for i, e in enumerate(lemm[a]) if e == input[0][0]]
          for ind in indexes:
            possible_results.append(create_tuple(ind, a))
    elif input[0][1] is not 'NaN':
      for a in range(0, len(lemm), 1):
        if input[0][1] in poss[a]:
          indexes = [i for i, e in enumerate(poss[a]) if e == input[0][1]]
          for ind in indexes:
            possible_results.append(create_tuple(ind, a))
    elif input[0][2] is not 'NaN':
      for a in range(0, len(lemm), 1):
        if input[0][2] in slova[a]:
          indexes = [i for i, e in enumerate(slova[a]) if e == input[0][2]]
          for ind in indexes:
            possible_results.append(create_tuple(ind, a))
    if flag == 0:
      for result in possible_results:
        #print(input, result)
        if (compare(input, result[0]) == 'TRUE'):
          #print('Вот вам предложение:', sent[result[1]], ' - ', avtors[result[1]])
          c.execute("INSERT INTO results(sentence, author) VALUES (?, ?)", (sent[result[1]], avtors[result[1]]))

    else:
      return("Упс, ошибка. Проверьте, правильно ли вы составили запрос")
    conn.commit()
    conn.close()


# Код Юли
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'
db = SQLAlchemy(app)


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Sentence = db.Column(db.Text, nullable=False)
    Author = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Results %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        to_search = request.form['to search']
        # проверяем to search
        try:
            #search_function(to_search)
            if type(search_function(to_search)) == str:
                return (search_function(to_search))
            else:
                return redirect('/results')
        except:
            return ('К сожалению, запрос', to_search, 'невозможен. Попробуйте ввести что-то другое.')
    else:
        return render_template('web form.html')


@app.route('/results')
def result():
    results = Results.query.all()
    count = Results.query.count()
    if count > 0:
        return render_template('results.html', results=results, count=count)
    else:
        return ('Результатов нет, попробуйте поискать что-то другое.')


if __name__ == '__main__':
    app.run(debug=True)
