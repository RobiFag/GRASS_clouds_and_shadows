#!/usr/bin/env python 
# coding=utf-8

import grass.script as gscript
import xml.etree.ElementTree as et
#import time
from datetime import datetime
#from osgeo import gdal
import os
from pyproj import Proj, transform

def main ():

    bands = {}
    dem = 'dem_sicily'
    
    
    ### start compiling the txt control file for i.atcorr

    tree = et.parse('/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/sentinel2/py_script/MTD_MSIL1C.xml')
    root = tree.getroot()

    tree_tl = et.parse('/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/sentinel2/MTD_TL.xml')
    root_tl = tree_tl.getroot()

    for elem in root[0].findall('Product_Info'):

        datatake = elem.find('Datatake')

        sensor = datatake.find('SPACECRAFT_NAME')

        time_str = elem.find('PRODUCT_START_TIME')

        time_py = datetime.strptime(time_str.text,'%Y-%m-%dT%H:%M:%S.%fZ')

        dec_hour = float(time_py.hour) + float(time_py.minute)/60 + float(time_py.second)/3600

        product = elem.find('Product_Organisation')
        g_list = product.find('Granule_List')
        granule = g_list.find('Granule')
        for img in root.iter('IMAGE_FILE'):
            #print img.text
            a = img.text.split('/')
            #print a[3]
            b = a[3].split('_')
            #print b[2]
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
            elif b[2] == 'B8a':
                bands['nir8a'] = a[3]
            elif b[2] == 'B09':
                bands['vapour'] = a[3]
            elif b[2] == 'B10':
                bands['cirrus'] = a[3]
            elif b[2] == 'B11':
                bands['swir11'] = a[3]
            elif b[2] == 'B12':
                bands['swir12'] = a[3]

            #print bands['costal']
            
        #image = granule.find('IMAGE_FILE')
        #for img in image:
            #print img.text
            #a = image.text.split('/')
            #b = a[3].split('_')

    #print bands

    for elem_tl in root_tl[1].findall('Tile_Geocoding'):
        epsg = elem_tl.find('HORIZONTAL_CS_CODE')
        print epsg.text.lower()
        position = elem_tl.find('Geoposition')
        print position.tag
        east_mtd = position.find('ULX')
        print east_mtd.text
        north_mtd = position.find('ULY')
        print north_mtd.text
        in_proj = Proj(init=epsg.text.lower())
        out_proj = Proj(init='epsg:4326')
        east,north = float(east_mtd.text),float(north_mtd.text)
        lon,lat = transform(in_proj,out_proj,east,north)
        print lon,lat



    for key, bb in bands.items():
        text = open("input_f.txt", "w+r")
        if sensor.text == 'Sentinel-2A':
            text.write(str(25) + "\n")
        elif sensor.text == 'Sentinel-2B':
            text.write(str(26) + "\n")
        else: 
            print 'error'
        text.write('{} {} {} {} {}'.format(time_py.month, time_py.day, dec_hour, lon, lat) + "\n")
        text.write('2' + "\n") #atmo model?
        text.write('1' + "\n") #aerosol model?
        text.write('0' + "\n") #visibility
        text.write('0.2' + "\n") #AOT add script for reading aot from aeronet data
        text.write('-0.600' + "\n") #mean elevation 
        text.write('-1000' + "\n") #sensor height
        b = bb.split('_')
        if b[2] == 'B01' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('166') #band
        elif b[2] == 'B02' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('167') #band
        elif b[2] == 'B03' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('168') #band
        elif b[2] == 'B04' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('169') #band
        elif b[2] == 'B05' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('170') #band
        elif b[2] == 'B06' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('171') #band
        elif b[2] == 'B07' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('172') #band
        elif b[2] == 'B08' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('173') #band
        elif b[2] == 'B8a' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('174') #band
        elif b[2] == 'B09' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('175') #band
        elif b[2] == 'B10' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('176') #band
        elif b[2] == 'B11' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('177') #band
        elif b[2] == 'B12' and sensor.text == 'Sentinel-2A':
            print b[2]
            text.write('178') #band
        else:
            gscript.message("some errors")
        
        gscript.run_command('i.atcorr',
        input=bb,
        parameters='input_f.txt',
        output='{}_{}'.format(bb, 'cor'),
        range='0,10000',
        elevation=dem,
        rescale='0,1',
        flags='r',
        overwrite=True)


if __name__ == "__main__":
    #options, flags = gscript.parser()
    #atexit.register(cleanup)
    main()



