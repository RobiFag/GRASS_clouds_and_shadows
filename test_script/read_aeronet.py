#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Py6S import *
s=SixS()

Aeronet.import_aeronet_data(s, "/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/home/roberta/ATM_COR/dati_AERONET/170601_170630_Sirmione_Museo_GC.dubovik", "13/06/2017 10:10")

print s.aero_profile

print s.aot550
