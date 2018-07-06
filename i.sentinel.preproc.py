#!/usr/bin/env python 
# coding=utf-8
#
############################################################################
#
# MODULE:	i.sentinel.preproc
# AUTHOR(S):	Roberta Fagandini, Moritz Lennert, Roberto Marzocchi
# PURPOSE:	Dowload, import and apply atmospheric correction to Sentinel-2 images
#
# COPYRIGHT:	(C) 2018 by the GRASS Development Team
#
#		This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%Module
#% description: Creates clouds and shadows masks for Sentinel-2 images
#% keywords: imagery
#% keywords: sentinel 
#% keywords: download
#% keywords: import
#% keywords: atmospheric correction
#%End
#%option
#% key: mtd_file
#% type: string
#% gisprompt: old,file,file
#% description: Name of the image metadata file (MTD_MSIL1C.xml)
#% required : yes
#% multiple: no
#% guisection: Required
#%end
#%option
#% key: elevation
#% type: string
#% gisprompt: old,cell,raster
#% description: Name of input elevation raster map (in m)
#% required : yes
#% multiple: no
#% guisection: Required
#%end
#%option
#% key: visibility
#% type: string
#% gisprompt: old,cell,raster
#% description: Name of input visibility raster map (in Km)
#% required : no
#% multiple: no
#% guisection: Required
#%end
#%option
#% key: aerosol_model
#% type: string
#% description: Select the proper Aerosol model
#% options: No aerosols,Continental model,Maritime model,Urban model,Shettle model for background desert aerosol,Biomass burning,Stratospheric model
#% answer: Continental model
#% required : yes
#% multiple: no
#% guisection: 6S Parameters
#%end
#%option
#% key: aeronet_file
#% type: string
#% gisprompt: old,file,file
#% description: Name of the AERONET file for computing AOT at 550nm
#% required : no
#% multiple: no
#% guisection: 6S Parameters
#%end

import grass.script as gscript
import xml.etree.ElementTree as et
from datetime import datetime
import os
import math
import sys
import shutil
import re
import glob
import atexit

def main ():


    bands = {}
    cor_bands = {}
    dem = options['elevation']	
    vis = options['visibility']
    mtd_file = options['mtd_file']
    
    ### create xml "tree" for reading parameters from metadata ###
    tree = et.parse(mtd_file)
    root = tree.getroot()

    ### start reading the xml file ###
    for elem in root[0].findall('Product_Info'):
        datatake = elem.find('Datatake')
        sensor = datatake.find('SPACECRAFT_NAME') #geometrical conditions = sensor 
        time_str = elem.find('GENERATION_TIME') #acquisition date and time 
        time_py = datetime.strptime(time_str.text,'%Y-%m-%dT%H:%M:%S.%fZ') #date and time conversion 
        gscript.message(_(time_py))
        dec_hour = float(time_py.hour) + float(time_py.minute)/60 + float(time_py.second)/3600 #compute decimal hour
        ### read input bands from metadata ###
        product = elem.find('Product_Organisation')
        g_list = product.find('Granule_List')
        granule = g_list.find('Granule')
        for img in root.iter('IMAGE_FILE'):
            a = img.text.split('/')
            b = a[3].split('_')
            gscript.message(_(a[3]))
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

    ### Aerosols model ###
    aerosol_mod = options['aerosol_model']

    ### read and compute AOT from AERONET file ###
    aot_value = options['aot_value']
    aeronet_file = options['aeronet_file']
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

    for row in file(aeronet_file):
        count+=1
        if count==4:
            columns = row.split(',')

    count=0
    for row in file(aeronet_file):
        count+=1
        if count>=5:
            columns = row.split(',')
            m_time.append(columns[0] + ' ' + columns[1])

    dates = [datetime.strptime(row, '%d:%m:%Y %H:%M:%S') for row in m_time]
    dates_list.append(dates)
    format_bd = time_py.strftime('%d/%m/%Y %H:%M:%S')
    gscript.message(_(format_bd))
    base_date = str(format_bd) #'13/08/2017 06:00:00'
    b_d = datetime.strptime(base_date,'%d/%m/%Y %H:%M:%S')

    for line in dates_list:
        closest = min(line, key=lambda x: abs(x - b_d))
        timedelta = abs(closest - b_d)

    count=0
    for row in file(aeronet_file): # reading file from line 4 
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
    upper = min([ i for i in wl if i >= aot_req], key=lambda x:abs(x-aot_req))
    lower = min([ i for i in wl if i < aot_req], key=lambda x:abs(x-aot_req))

    count=0
    for row in file(aeronet_file): 
        count+=1
        if count==dates.index(closest)+5:
            t_columns = row.split(',')
            count2=0
            check_up=0
            check_lo=0
            while count2<len(i_col) and check_up<1:
                if t_columns[wl.index(upper)+i_col[0]]=="N/A": #search for the not null value for the upper wavelenght
                    aot_req_tmp = upper
                    upper = min([ i for i in wl if i > aot_req_tmp], key=lambda x:abs(x-aot_req_tmp))
                else:
                    wl_upper = float(upper)
                    aot_upper = float(t_columns[wl.index(upper)+i_col[0]])
                    check_up=1
                count2+=1
            count2=0
            while count2<len(i_col) and check_lo<1:
                if t_columns[wl.index(lower)+i_col[0]]=="N/A": #search for the not null value for the lower wavelenght
                    aot_req_tmp = lower
                    lower = min([ i for i in wl if i < aot_req_tmp], key=lambda x:abs(x-aot_req_tmp))
                else:
                    wl_lower = float(lower)
                    aot_lower = float(t_columns[wl.index(lower)+i_col[0]])
                    check_lo=1
                count2+=1

    alpha = math.log(aot_lower/aot_upper)/math.log(wl_upper/wl_lower)
    aot550 = math.exp(math.log(aot_lower) - math.log(550.0/wl_lower)*alpha)
    gscript.message(_('--- Computed AOT at 550 nm: {} ---'.format(aot550)))

    ### compute mean target elevation in km ###
    stats_d = gscript.parse_command('r.univar', flags='g', map=dem)
    mean = (float(stats_d['mean']))
    conv_fac = -0.001
    dem_mean = mean * conv_fac
    gscript.message(_('--- Computed mean target elevation above sea level: {:.3f} m ---'.format(mean)))
    
    if vis != '':
        stats_v = gscript.parse_command('r.univar', flags='g', map=vis)
        vis_mean = int(float(stats_v['mean']))
        gscript.message(_('--- Computed visibility mean value: {} Km ---'.format(vis_mean)))
    else:
        gscript.message(_('--- No visibility map has been provided ---'))

    for key, bb in bands.items():
        gscript.message(_('--- Compiling the control file.. ---'))
        text = open("control_file.txt", "w")
        if sensor.text == 'Sentinel-2A':
            text.write(str(25) + "\n")
        elif sensor.text == 'Sentinel-2B':
            text.write(str(26) + "\n")
        else: 
            gscript.fatal('The input image does not seem to be a Sentinel image')
        text.write('{} {} {} {} {}'.format(time_py.month, time_py.day, dec_hour, lon, lat) + "\n")
        winter = [1, 2, 3, 4, 10, 11, 12]
        summer = [5, 6, 7, 8, 9]
        if lat > -15.00 and lat <= 15.00: #tropical
            text.write('1' + "\n")
        elif lat > 15.00 and lat <= 45.00:
            if b_d.month in winter: #midlatitude winter
                text.write('3' + "\n")
            else: #midlatitude summer
                text.write('2' + "\n")
        elif lat > -15.00 and lat <= -45.00: 
            if b_d.month in winter: #midlatitude summer
                text.write('2' + "\n")
            else: #midlatitude winter
                text.write('3' + "\n")
        elif lat > 45.00 and lat <= 60.00:
            if b_d.month in winter: #subartic winter
                text.write('5' + "\n")
            else: #subartic summer
                text.write('4' + "\n")
        elif lat > -45.00 and lat <= -60.00:
            if b_d.month in winter: #subartic summer
                text.write('4' + "\n")
            else: #subartic winter
                text.write('5' + "\n")
        else:
            gscript.fatal('Latitude {} is out of range'.format(lat))
        if aerosol_mod == 'No aerosols':
            text.write('0' + "\n") #aerosol model
        elif aerosol_mod == 'Continental model':
            text.write('1' + "\n") #aerosol model
        elif aerosol_mod == 'Maritime model':
            text.write('2' + "\n") #aerosol model
        elif aerosol_mod == 'Urban model':
            text.write('3' + "\n") #aerosol model
        elif aerosol_mod == 'Shettle model for background desert aerosol':
            text.write('4' + "\n") #aerosol model
        elif aerosol_mod == 'Biomass burning':
            text.write('5' + "\n") #aerosol model
        elif aerosol_mod == 'Stratospheric model':
            text.write('6' + "\n") #aerosol model
        if vis != '':
            text.write('{}'.format(vis_mean) + "\n")
            if aot550 != '' and aot_value != '':
                gscript.warning(_("AOT input will be ignored"))
        elif vis == '' and aot550 != 0:
            text.write('0' + "\n") #visibility
            text.write('{}'.format(aot550) + "\n") #AOT add script for reading aot from aeronet data
        elif vis == '' and aot550 == 0:
            text.write('-1' + "\n") #visibility
            text.write('{}'.format(aot550) + "\n") #AOT add script for reading aot from aeronet data
        else:
            gscript.fatal("Unable to retrieve visibility or AOT value, check the input")
        #text.write('{}'.format(aot550) + "\n") #AOT add script for reading aot from aeronet data
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
            gscript.fatal('Bands do not seem to belong to a Sentinel image')
    	text.close()
        
        gscript.run_command('i.atcorr',
            input=bb,
            parameters='control_file.txt',
            output='{}_{}'.format(bb, 'cor'),
            range='1,10000',
            elevation=dem,
            rescale='0,1',
            flags='r',
            overwrite=True)
        cor_bands[key] = "{}_{}".format(bb, 'cor')
    #gscript.message(_(cor_bands.values()))
    gscript.message(_('--- All bands have been processed ---'))

    for key, cb in cor_bands.items():
        gscript.message(_(cb))
        gscript.run_command('r.colors',
            map=cb,
            color='grey1.0')


if __name__ == "__main__":
    #options, flags = gscript.parser()
    #atexit.register(cleanup)
    main()

