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

	expr = 'cloud_def = if( %s, 0, null( ) )' % (cloud_rules)
	
	gscript.mapcalc( expr,  overwrite=True)
	#print expr

	gscript.run_command('r.to.vect', input='cloud_def_script', output='cloud_def_script_v', type='area', flags='s', overwrite=True)

	gscript.run_command('v.clean', input='cloud_def_script_v', output='cloud_clean', tool='rmarea', threshold=50000, overwrite=True)

	### end of Clouds detection ####


	### start of shadows detection ###
	gscript.mapcalc('{r6} = ({a} > {g}) && ({a} < {d}) && ({a} < 0.1) && ({g} < 0.1)'.format(r6='sixth_rule_script', a=f_bands[0], b=f_bands[1], d=f_bands[3], g=f_bands[6]), overwrite=True)

	gscript.mapcalc('{r7} = ({a} < {g}) && ({a} < {d}) && ({a} < 0.1) && ({g} < 0.1) && ({d} < 0.1)'.format(r7='seventh_rule_script', a=f_bands[0], b=f_bands[1], d=f_bands[3], g=f_bands[6]), overwrite=True)

	gscript.mapcalc('{rs} = ({r6} == 1) || ({r7} == 1)'.format(rs='shadow_script', r6='sixth_rule_script', r7='seventh_rule_script'), overwrite=True)

	gscript.run_command('r.mask', raster='shadow_script', maskcats=1)
	
	gscript.mapcalc('{rd} = ({b} - {a})'.format(rd='diff_green_blue', b=f_bands[1], a=f_bands[0]), overwrite=True)

	gscript.mapcalc('{S} = ({rs} == 1) && ({rd} < 0.007)'.format(S='shadow_def_script', rs='shadow_script', rd='diff_green_blue'), overwrite=True)

	gscript.run_command('r.null', map='shadow_def_script', setnull=0, overwrite=True)

	gscript.run_command('r.to.vect', input='shadow_def_script', output='shadow_def_script_v', type='area', flags='s', overwrite=True)

	gscript.run_command('v.clean', input='shadow_def_script_v', output='shadow_clean', tool='rmarea', threshold=50000, overwrite=True)

	### end of shadows detection ###


if __name__ == "__main__": 
    main()

