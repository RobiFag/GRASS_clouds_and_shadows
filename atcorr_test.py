#!/usr/bin/env python 
# coding=utf-8

import grass.script as gscript
import xml.etree.ElementTree as et
from datetime import datetime
import os


def main ():

    bands = {}
    cor_bands = {}
    dem = 'dem_sicily'
    
    ### create xml "tree" for reading parameters from metadata ###
    tree = et.parse('/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/sentinel2/py_script/MTD_MSIL1C.xml')
    root = tree.getroot()

    ### start reading the xml file ###
    for elem in root[0].findall('Product_Info'):
        datatake = elem.find('Datatake')
        sensor = datatake.find('SPACECRAFT_NAME') #geometrical conditions = sensor 
        time_str = elem.find('GENERATION_TIME') #acquisition date and time 
        time_py = datetime.strptime(time_str.text,'%Y-%m-%dT%H:%M:%S.%fZ') #date and time conversion 
        #gscript.message(_(time_py))
        dec_hour = float(time_py.hour) + float(time_py.minute)/60 + float(time_py.second)/3600 #compute decimal hour
        ### read input bands from metadata ###
        product = elem.find('Product_Organisation')
        g_list = product.find('Granule_List')
        granule = g_list.find('Granule')
        for img in root.iter('IMAGE_FILE'):
            #gscript.message(_(img.text))
            a = img.text.split('/')
            #gscript.message(_(a[3]))
            b = a[3].split('_')
            #gscript.message(_(a[3]))
            if b[2] == 'B01':
                bands['costal'] = a[3]
            elif b[2] == 'B02':
                bands['blue'] = a[3]
            elif b[2] == 'B03':
                bands['green'] = a[3]
            elif b[2] == 'B04':
                bands['red'] = a[3]
            elif b[2] == 'B05':
                bands['re5'] = a[3]
            elif b[2] == 'B06':
                bands['re6'] = a[3]
            elif b[2] == 'B07':
                bands['re7'] = a[3]
            elif b[2] == 'B08':
                bands['nir'] = a[3]
            elif b[2] == 'B8A':
                bands['nir8a'] = a[3]
            elif b[2] == 'B09':
                bands['vapour'] = a[3]
            elif b[2] == 'B10':
                bands['cirrus'] = a[3]
            elif b[2] == 'B11':
                bands['swir11'] = a[3]
            elif b[2] == 'B12':
                bands['swir12'] = a[3]

    ### retrieve Longitude and latitude of the centre of the computational region ###
    c_region = gscript.parse_command('g.region', flags='bg')
    lon = (float(c_region['ll_clon']))
    lat = (float(c_region['ll_clat']))
    gscript.message(_(lon))
    gscript.message(_(lat))
    
    ### compute mean target elevation in km ###
    stats = gscript.parse_command('r.univar', flags='g', map=dem)
    mean = (float(stats['mean']))
    conv_fac = -0.001
    dem_mean = mean * conv_fac
    gscript.message(_('--- Computed mean target elevation above sea level: {} ---'.format(dem_mean)))

    for key, bb in bands.items():
        text = open("bbbbbbb.txt", "w")
        if sensor.text == 'Sentinel-2A': #sensor
            text.write(str(25) + "\n")
        elif sensor.text == 'Sentinel-2B':
            text.write(str(26) + "\n")
        else: 
            gscript.message(_('error'))
        text.write('{} {} {} {} {}'.format(time_py.month, time_py.day, dec_hour, lon, lat) + "\n")
        text.write('2' + "\n") #atmo model?
        text.write('1' + "\n") #aerosol model?
        text.write('0' + "\n") #visibility
        text.write('0.2' + "\n") #AOT add script for reading aot from aeronet data
        text.write('{}'.format(dem_mean) + "\n") #mean elevation 
        text.write('-1000' + "\n") #sensor height
        b = bb.split('_')
        if b[2] == 'B01' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('166') #band
        elif b[2] == 'B02' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('167') #band
        elif b[2] == 'B03' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('168') #band
        elif b[2] == 'B04' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('169') #band
        elif b[2] == 'B05' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('170') #band
        elif b[2] == 'B06' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('171') #band
        elif b[2] == 'B07' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('172') #band
        elif b[2] == 'B08' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('173') #band
        elif b[2] == 'B8A' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('174') #band
        elif b[2] == 'B09' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('175') #band
        elif b[2] == 'B10' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('176') #band
        elif b[2] == 'B11' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('177') #band
        elif b[2] == 'B12' and sensor.text == 'Sentinel-2A':
            gscript.message(_(b[2]))
            text.write('178') #band
        elif b[2] == 'B01' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('179') #band
        elif b[2] == 'B02' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('180') #band
        elif b[2] == 'B03' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('181') #band
        elif b[2] == 'B04' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('182') #band
        elif b[2] == 'B05' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('183') #band
        elif b[2] == 'B06' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('184') #band
        elif b[2] == 'B07' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('185') #band
        elif b[2] == 'B08' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('186') #band
        elif b[2] == 'B8A' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('187') #band
        elif b[2] == 'B09' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('188') #band
        elif b[2] == 'B10' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('189') #band
        elif b[2] == 'B11' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('190') #band
        elif b[2] == 'B12' and sensor.text == 'Sentinel-2B':
            gscript.message(_(b[2]))
            text.write('191') #band
        else:
            gscript.message(_("some errors"))
    	text.close()
        
        gscript.run_command('i.atcorr',
            input=bb,
            parameters='bbbbbbb.txt',
            output='{}_{}'.format(bb, 'cor'),
            range='1,10000',
            elevation=dem,
            rescale='0,1',
            flags='r',
            overwrite=True)
        cor_bands[key] = "{}_{}".format(bb, 'cor')
    gscript.message(_(cor_bands.values()))

    for key, cb in cor_bands.items():
        gscript.message(_(cb))
        gscript.run_command('r.colors',
            map=cb,
            color='grey1.0')


if __name__ == "__main__":
    #options, flags = gscript.parser()
    #atexit.register(cleanup)
    main()

