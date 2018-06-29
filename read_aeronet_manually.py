#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,shutil,re,glob
from datetime import datetime, date, timedelta

file_name="/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/home/roberta/ATM_COR/dati_AERONET/170801_170831_Sirmione_Museo_GC.dubovik"

i=0
cc=0 # contatore da 1 a 3 (! alla 2 riga che potrebbe non esserci
count=0

columns = []
m_time = []
dates_list = []
columns = []
i_col = []
coll = []
wl = []
for row in file(file_name): # reading file from line 4 
    count+=1
    if count==4:
        columns = row.split(',')
#print columns

count=0
for row in file(file_name): # reading file from line 5 
    #print row
    count+=1
    if count>=5:
        columns = row.split(',')
        #print datetime.strptime((columns[0] + ' ' + columns[1]),'%d:%m:%Y %H:%M:%S')
        #m_time.append(datetime.strptime((columns[0] + ' ' + columns[1]),'%d:%m:%Y %H:%M:%S') 
        m_time.append(columns[0] + ' ' + columns[1])
#print columns

#for row in m_time:
dates = [datetime.strptime(row, '%d:%m:%Y %H:%M:%S') for row in m_time]
dates_list.append(dates)
#print dates_list

base_date = '13/08/2017 06:00:00'
b_d = datetime.strptime(base_date,'%d/%m/%Y %H:%M:%S')
print b_d

for line in dates_list:
    #print line
    closest = min(line, key=lambda x: abs(x - b_d))
    #print closest
    timedelta = abs(closest - b_d)

print closest 
print timedelta 
print dates.index(closest)

for row in file(file_name): # reading file from line 4 
    count+=1
    if count==4:
        columns = row.split(',')
        for i, col in enumerate(columns):
            if "AOT_" in col:
                i_col.append(i)
                coll.append(col)
for line in coll:
    l = line.split('_')
    wl.append(int(l[1]))
print wl
print i_col,coll

aot_req = 550
upper = min([ i for i in wl if i >= aot_req], key=lambda x:abs(x-aot_req))
lower = min([ i for i in wl if i < aot_req], key=lambda x:abs(x-aot_req))

print upper,lower

