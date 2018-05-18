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

	gscript.message('--- tutte le bande sono state rese float e scalate! ---')
	print f_bands

	gscript.mapcalc('{r} = 1'.format(r='base_M'), overwrite=True)
	
	for fb in f_bands:
		gscript.run_command('r.stats.zonal', base='base_M', cover=fb, method='max', output="%s_%s" % (fb, m), overwrite=True)
		stats.append ("%s_%s" % (fb, m))

	gscript.message('--- tutte le statistiche sono state calcolate! ---')
	print stats

	#### start of Clouds detection  (some rules from litterature)###
	gscript.mapcalc('{r1} = ({a} > (0.08*{ma})) && ({b} > (0.08*{mb})) && ({c} > (0.08*{mc}))'.format(r1='first_rule_script', a=f_bands[0], ma=stats[0], b=f_bands[1], mb=stats[1], c=f_bands[2], mc=stats[2]), overwrite=True)
	
	gscript.mapcalc('{r2} = ({c} < ((0.08*{mc})*1.5)) && ({c} > {g}*1.3)'.format(r2='second_rule_script', c=f_bands[2], mc=stats[2], g=f_bands[6]), overwrite=True)
	
	gscript.mapcalc('{r3} = ({f} < (0.1*{mf})) && ({g} < (0.1*{mg}))'.format(r3='third_rule_script', f=f_bands[5], mf=stats[5], g=f_bands[6], mg=stats[6]), overwrite=True)
	
	gscript.mapcalc('{r4} = if({e} == max({e}, 2 * {a},  2 * {b},  2 * {c}))'.format(r4='fourth_rule_script', e=f_bands[4], a=f_bands[0], b=f_bands[1], c=f_bands[2]), overwrite=True)
	
	gscript.mapcalc('{r5} = {a} > 0.2'.format(r5='fifth_rule_script', a=f_bands[0]), overwrite=True)

	gscript.mapcalc('{rf} = ({r1} == 1) && ({r2} == 0) && ({r3} == 0) && ({r4} == 0) && ({r5} == 1)'.format(rf='cloud_def_script', r1='first_rule_script', r2='second_rule_script', r3='third_rule_script', r4='fourth_rule_script', r5='fifth_rule_script'), overwrite=True)

	gscript.run_command('r.null', map='cloud_def_script', setnull=0, overwrite=True)

	gscript.run_command('r.to.vect', input='cloud_def_script', output='cloud_def_script_v', type='area', flags='s', overwrite=True)

	gscript.run_command('v.clean', input='cloud_def_script_v', output='cloud_clean', tool='rmarea', threshold=50000, overwrite=True)

	### end of Clouds detection ####


if __name__ == "__main__": 
    main()

