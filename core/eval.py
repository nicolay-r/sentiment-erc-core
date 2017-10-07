#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import os
import re
from tqdm import tqdm
from pymystem3 import Mystem

m = Mystem()
# цвет участника
color = 'black'

syn_dict = [
    ['сша', 'соединенные штаты', 'америка', 'соединенные штаты америки',\
     'соединенный штат америка', 'штат'],\
    ['вашингтон', 'белый дом'],\
    ['обама', 'барак обама'],\
    ['ес', 'евросоюз', 'европейский союз', 'европа', 'брюссель'],\
    ['росcия', 'рф', 'российская федерация', 'российский федерация'],\
    ['путин', 'владимир путин', 'владимир владимирович путин'],\
    ['лёвен', 'лёвено'],\
    ['асеан', 'асеана'],\
    ['лиухто', 'лиухтый', 'кари лиухто'],\
    ['ИГ', 'ИГО', 'исламский государство'],\
    ['Башар Асад', 'Асад'],\
    ]

""" Округление до 4 знаков после запятой.
"""
def round4(numb):
    return int(numb * 10000) / 10000

""" Проверка имен на заменяемость. Имена могут быть:
- подстрокой другого: Путин vs Владимир Путин, Валентин vs Валентино
- формой слова: соединенные vs соединенный vs соединить.
"Словарь синонимов" хранится в переменной syn_dict.
"""
def checkWords(word1, word2):
    if word1 == word2:
        return True

    res2=re.split(" ", word2)
    for r in res2:
        if word1 in r:
            return True
        for s in syn_dict:
            if word1 in s and r in s:
                return True
        l = m.lemmatize(r)
        if word1 in l:
            return True
        for s in syn_dict:
            if word1 in s and l in s:
                return True

    res2 = re.split(" ", word1)
    for r in res2:
        if word2 in r:
            return True
        for s in syn_dict:
            if word2 in s and r in s:
                return True
        l = m.lemmatize(r)
        if word2 in l:
            return True
        for s in syn_dict:
            if word2 in s and l in s:
                return True

    return False

""" Расчет полноты и точности.
"""
def calcPrecisionAndRecall(results):
    # Берем все позитивные и негативные ответы команд
    pos_answers=results[(results['how_results']=='pos')]
    neg_answers=results[(results['how_results']=='neg')]

    # Расчет точности.
    if len(pos_answers)!=0:
        pos_prec=len(pos_answers[(pos_answers['comparison']==True)])/ len(pos_answers)
    else:
        pos_prec=0
    if len(neg_answers)!=0:
        neg_prec=len(neg_answers[(neg_answers['comparison']==True)])/ len(neg_answers)
    else:
        neg_prec=0

    # Расчет полноты.
    if len(results[results['how_orig']=='pos'])!=0:
        pos_recall=len(pos_answers[(pos_answers['comparison']==True)])/ len(results[results['how_orig']=='pos'])
    else:
        pos_recall=0
    if len(results[results['how_orig']=='neg'])!=0:
        neg_recall=len(neg_answers[(neg_answers['comparison']==True)])/ len(results[results['how_orig']=='neg'])
    else:
        neg_recall=0
    return pos_prec, neg_prec, pos_recall, neg_recall

""" Расчет данных для файла.
"""
def calc_a_file(num):
    # Если файл существует.
    filename = "test_{}/art{}.opin.txt".format(color, str(num))
    if not os.path.exists(filename):
        print filename
        print "-  art" + str(num) + ".opin.txt" # , end=" ")
        return

    # Считываем файл ответов команды и отбрасываем лишнюю информацию.
    # print("test_"+color+"/art"+str(num)+".opin.txt", end=" ")

    file = pd.read_csv(filename, sep=',', header=None)
    # print(" read")
    orig_file = file[[0,1,2]].copy()
    orig_file.columns=['who', 'to', 'how_orig']
    orig_file['who']=orig_file['who'].str.strip()
    orig_file['who']=orig_file['who'].str.lower()
    orig_file['to']=orig_file['to'].str.strip()
    orig_file['to']=orig_file['to'].str.lower()
    orig_file['how_orig']=orig_file['how_orig'].str.strip()

    # Считываем файл ответов экспертов.
    file_experts = "test_orig/artest_orig/art{}.opin.txt".format(str(num))
    print(file_experts)
    file2 = pd.read_csv(file_experts, sep=',', header=None)
    test_file = file2[[0,1,2]].copy()
    test_file.columns=['who', 'to', 'how_results']
    test_file['who'] = test_file['who'].str.strip()
    test_file['who'] = test_file['who'].str.lower()
    test_file['to'] = test_file['to'].str.strip()
    test_file['to'] = test_file['to'].str.lower()
    test_file['how_results'] = test_file['how_results'].str.strip()

    orig_file=orig_file.sort_values(['who', 'to'])
    test_file=test_file.sort_values(['who', 'to'])

    # Сливаем ответы там, где имена собвпадают.
    results= test_file.merge(orig_file, 'outer', on=['who','to'], copy=False)
    results.insert(len(results.columns), 'comparison', '')
    # Сравниваем для них ответы
    results['comparison'] = results['how_results'] == results['how_orig']
    results=results.sort_values(['comparison', 'how_orig', 'how_results'])
    # Берем те части ответов, в которых имена не совпадают.
    faulty=results[results.comparison==False]
    count_res=len(faulty)-len(faulty[faulty.how_orig.isnull()])

    # Идем по всем ответам, сравниваем всех со всеми, может быть имя было выделено командой не так, или эксперт написал синоним.
    for i in range(count_res, len(faulty)):
        for j in range(count_res):
            if(checkWords(results['who'][results.index[i]], results['who'][results.index[j]]) and \
                checkWords(results['to'][results.index[i]], results['to'][results.index[j]])):
    # Если надо длеать замену, дописываем ответ в одну строчку и помечаем на удаление другую.
    #            print('<', results['who'][results.index[i]], '>,<', results['who'][results.index[j]], '>')
    #            print('<', results['to'][results.index[i]], '>,<', results['to'][results.index[j]], '>')
                results.loc[results.index[i], ('how_orig')] = results.loc[results.index[j], ('how_orig')]
                results.loc[results.index[i], ('comparison')] = (results.loc[results.index[i], ('how_orig')] == results.loc[results.index[i], ('how_results')])
                results.loc[results.index[j], ('comparison')] = '---'

    # Выкидываем все строки, которые были слиты вместе с другими.
    results=results[results['comparison'] != '---']
    # print(">test_"+color+"/art"+str(num)+".comp.txt")
    # Сохраняем файл со сравнениями.
    comarison_file = "test_{}/art{}.comp.txt".format(color, str(num))
    results.to_csv(comparison_file)

    return calcPrecisionAndRecall(results)

if __name__ == "__main__":

    """ Основная подпрограмма.
    """
    pos_prec, neg_prec, pos_recall, neg_recall=(0,0,0,0)

    for n in range(46, 76):
        try:
            [pos_prec1, neg_prec1, pos_recall1, neg_recall1] = calc_a_file(n)
            pos_prec += pos_prec1
            neg_prec += neg_prec1
            pos_recall += pos_recall1
            neg_recall += neg_recall1
        except BaseException:
            pass

    pos_prec /= 30
    neg_prec /= 30
    pos_recall /= 30
    neg_recall /= 30
    if pos_prec * pos_recall != 0:
        f1_pos = 2 * pos_prec*pos_recall / (pos_prec+pos_recall)
    else:
        f1_pos = 0
    if neg_prec * neg_recall != 0:
        f1_neg = 2 * neg_prec * neg_recall / (neg_prec+neg_recall)
    else:
        f1_neg = 0

    print round4(pos_prec), ';', round4(neg_prec), ';', \
        round4(pos_recall), ';', round4(neg_recall), ';', \
        round4(f1_pos), ';', round4(f1_neg), ';', \
        round4((f1_pos + f1_neg) / 2)
