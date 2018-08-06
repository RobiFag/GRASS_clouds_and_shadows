#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,shutil,re,glob,math
from datetime import datetime, date, timedelta

file_name="/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/home/roberta/ATM_COR/dati_AERONET/170801_170831_Sirmione_Museo_GC.dubovik"

i=0
cc=0 
count=0

columns = []
m_time = []
dates_list = []
t_columns = []
i_col = []
coll = []
wl = []

for row in file(file_name): # reading file from line 4 
    count+=1
    if count==4:
        columns = row.split(',')

count=0
for row in file(file_name): # reading file from line 5 
    count+=1
    if count>=5:
        columns = row.split(',')
        m_time.append(columns[0] + ' ' + columns[1])

dates = [datetime.strptime(row, '%d:%m:%Y %H:%M:%S') for row in m_time]
dates_list.append(dates)
base_date = '13/08/2017 06:00:00'
b_d = datetime.strptime(base_date,'%d/%m/%Y %H:%M:%S')

for line in dates_list:
    closest = min(line, key=lambda x: abs(x - b_d)) #identify the closest date and time to the one given
    timedelta = abs(closest - b_d)

count=0
for row in file(file_name): 
    count+=1
    if count==4:
        t_columns = row.split(',')
        for i, col in enumerate(t_columns):
            if "AOT_" in col:
                i_col.append(i)
                coll.append(col)
for line in coll:
    l = line.split('_')
    wl.append(int(l[1]))

aot_req = 550
upper = min([ i for i in wl if i >= aot_req], key=lambda x:abs(x-aot_req)) #identify the upper closest wavelength
lower = min([ i for i in wl if i < aot_req], key=lambda x:abs(x-aot_req)) #identify the upper closest wavelength

count=0
for row in file(file_name): 
    count+=1
    if count==dates.index(closest)+5:
        t_columns = row.split(',')
        count2=0
        check_up=0
        check_lo=0
        while count2<len(i_col) and check_up<1:
            if t_columns[wl.index(upper)+i_col[0]]=="N/A": #search for the not null value for the upper wavelength
                aot_req_tmp = upper
                upper = min([ i for i in wl if i > aot_req_tmp], key=lambda x:abs(x-aot_req_tmp))
            else:
                wl_upper = float(upper)
                aot_upper = float(t_columns[wl.index(upper)+i_col[0]])
                check_up=1
            count2+=1
        count2=0
        while count2<len(i_col) and check_lo<1:
            if t_columns[wl.index(lower)+i_col[0]]=="N/A": #search for the not null value for the lower wavelength
                aot_req_tmp = lower
                lower = min([ i for i in wl if i < aot_req_tmp], key=lambda x:abs(x-aot_req_tmp))
            else:
                wl_lower = float(lower)
                aot_lower = float(t_columns[wl.index(lower)+i_col[0]])
                check_lo=1
            count2+=1

alpha = math.log(aot_lower/aot_upper)/math.log(wl_upper/wl_lower) #Angstrom coefficient
aot550 = math.exp(math.log(aot_lower) - math.log(550.0/wl_lower)*alpha) #AOT at 550nm using the Angstrom coefficient and one of the closest wavelengths
print aot550

