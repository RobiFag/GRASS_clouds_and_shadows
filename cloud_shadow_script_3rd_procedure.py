#!/usr/bin/env python 
# coding=utf-8

import grass.script as gscript
import math,os,sys,shutil,re,glob,numpy
import xml.etree.ElementTree as et

def main ():

	#import bands atmospherically corrected using arcsi (scale factor 1000 instead of 10000)

	#############################################
	# INPUT
	#############################################

	#bands 
	b1 = 'blu'
	b2 = 'green'
	b3 = 'red'
	b4 = 'nir'
	b5 = 'nir8a'
	b7 = 'swir11'
	b8 = 'swir12'
	f = 'float'
	bands = [b1, b2, b3, b4, b5, b7, b8]
	f_bands = []
	m = 'max'
	stats = []

	gscript.run_command('g.region', rast=b1, flags='pa')

	for b in bands:
		gscript.mapcalc('{r} = 1.0 * ({a})/1000'.format(r="%s_%s" % (b, f), a=b), overwrite=True)
		f_bands.append ("%s_%s" % (b, f))

	gscript.message('--- All bands are converted to float and the quantification value has been applied ---')
	#print f_bands

	gscript.mapcalc('{r} = 1'.format(r='base_M'), overwrite=True)
	
	for fb in f_bands:
		gscript.run_command('r.stats.zonal', base='base_M', cover=fb, method='max', output="%s_%s" % (fb, m), overwrite=True)
		stats.append ("%s_%s" % (fb, m))

	gscript.message('--- Statistics have been computed! ---')
	#print stats


	#### start of Clouds detection  (some rules from litterature)###

	first_rule = '((%s > (0.08*%s)) && (%s > (0.08*%s)) && (%s > (0.08*%s)))' % (f_bands[0], stats[0], f_bands[1], stats[1], f_bands[2], stats[2])
	second_rule = '((%s < ((0.08*%s)*1.5)) && (%s > %s*1.3))' % (f_bands[2], stats[2], f_bands[2], f_bands[6])
	third_rule = '((%s < (0.1*%s)) && (%s < (0.1*%s)))' % (f_bands[5], stats[5], f_bands[6], stats[6])
	fourth_rule = '(if(%s == max(%s, 2 * %s,  2 * %s,  2 * %s)))' % (f_bands[4], f_bands[4], f_bands[0], f_bands[1], f_bands[2])
	fifth_rule = '(%s > 0.2)' % (f_bands[0])
	cloud_rules = '(%s == 1) && (%s == 0) && (%s == 0) && (%s == 0) && (%s == 1)' % (first_rule, second_rule, third_rule, fourth_rule, fifth_rule)

	expr_c = 'cloud_def = if( %s, 0, null( ) )' % (cloud_rules)
	
	gscript.mapcalc( expr_c,  overwrite=True)
	#print expr

	gscript.run_command('r.to.vect', input='cloud_def', output='cloud_def_v', type='area', flags='s', overwrite=True)

	gscript.run_command('v.clean', input='cloud_def_v', output='cloud_mask', tool='rmarea', threshold=50000, overwrite=True)

	### end of Clouds detection ####


	### start of shadows detection ###

	sixth_rule = '(((%s > %s) && (%s < %s) && (%s < 0.1) && (%s < 0.1)) || ((%s < %s) && (%s < %s) && (%s < 0.1) && (%s < 0.1) && (%s < 0.1)))' % (f_bands[0], f_bands[6], f_bands[0], f_bands[3], f_bands[0], f_bands[6], f_bands[0], f_bands[6], f_bands[0], f_bands[3], f_bands[0], f_bands[6], f_bands[3])

	seventh_rule = '(%s - %s)' % (f_bands[1], f_bands[0])
	shadow_rules = '((%s == 1) && (%s < 0.007))' % (sixth_rule, seventh_rule)
	
	expr_s = 'shadow_temp = if( %s, 0, null( ) )' % (shadow_rules)
	
	gscript.mapcalc( expr_s,  overwrite=True)

	gscript.run_command('r.to.vect', input='shadow_temp', output='shadow_temp_v', type='area', flags='s', overwrite=True)

	gscript.run_command('v.clean', input='shadow_temp_v', output='shadow_temp_mask', tool='rmarea', threshold=10000, overwrite=True)

	### end of shadows detection ###


if __name__ == "__main__": 
    main()

