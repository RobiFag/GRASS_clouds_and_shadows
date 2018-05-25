#!/usr/bin/env python 
# coding=utf-8

import grass.script as gscript
import math,os,sys,shutil,re,glob,numpy,time,atexit
import xml.etree.ElementTree as et

def main ():


	#import bands atmospherically corrected using arcsi (scale factor 1000 instead of 10000)

	#############################################
	# INPUT
	#############################################

	#temporary map names
    	global tmp, t
    	tmp = {}
    	t = True

	mapset = gscript.gisenv()['MAPSET']

	# prepare temporary map raster names
    	processid = "%.2f" % time.time()
	processid = processid.replace(".", "_")
	tmp["base_M"] = "base_M_" + processid
	tmp["cloud_v"] = "cloud_v_" + processid
	tmp["shadow_temp_v"] = "shadow_temp_v_" + processid
	tmp["shadow_temp_mask"] = "shadow_temp_mask_" + processid
	tmp["centroid"] = "centroid_" + processid
	tmp["dissolve"] = "dissolve_" + processid
	tmp["delcat"] = "delcat_" + processid
	tmp["addcat"] = "addcat_" + processid
	tmp["cl_shift"] = "cl_shift_" + processid
	tmp["overlay"] = "overlay_" + processid
	

	#check temporary map names are not existing maps
	for key, value in tmp.items():
		if gscript.find_file(value, element = 'vector', mapset = mapset)['file']:
			gscript.fatal(_("Temporary vector map <%s> already exists.") % value)
		if gscript.find_file(value, element = 'cell', mapset = mapset)['file']:
			gscript.fatal(_("Temporary raster map <%s> already exists.") % value)

	#input file
	mtd_file = '/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/sentinel2/MTD_TL.xml' ####change MTD_TL file path!!!####	 
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
	cloud_def = 'cloud_def'
	shadow_temp = 'shadow_temp'
	scale_fac = 1000
	cloud_clean_T = 50000
	shadow_clean_T = 10000
	raster_max = []
	cloud_mask = 'cloud_mask'
	shadow_mask = 'shadow_mask'


	gscript.run_command('g.region', rast=b1, flags='pa')

	for b in bands:
		gscript.mapcalc('{r} = 1.0 * ({a})/{c}'.format(r="%s_%s" % (b, f), a=b, c=scale_fac), overwrite=True)
		f_bands.append ("%s_%s" % (b, f))

	gscript.message('--- All bands are converted to float and the quantification value has been applied ---')
	#print f_bands

	for fb in f_bands:
		stats = gscript.parse_command('r.univar', flags='g', map=fb)
		raster_max.append (float(stats['max']))
	#print raster_max

	gscript.message('--- Statistics have been computed! ---')


	#### start of Clouds detection  (some rules from litterature)###

	first_rule = '((%s > (0.08*%s)) && (%s > (0.08*%s)) && (%s > (0.08*%s)))' % (f_bands[0], raster_max[0], f_bands[1], raster_max[1], f_bands[2], raster_max[2])
	second_rule = '((%s < ((0.08*%s)*1.5)) && (%s > %s*1.3))' % (f_bands[2], raster_max[2], f_bands[2], f_bands[6])
	third_rule = '((%s < (0.1*%s)) && (%s < (0.1*%s)))' % (f_bands[5], raster_max[5], f_bands[6], raster_max[6])
	fourth_rule = '(if(%s == max(%s, 2 * %s,  2 * %s,  2 * %s)))' % (f_bands[4], f_bands[4], f_bands[0], f_bands[1], f_bands[2])
	fifth_rule = '(%s > 0.2)' % (f_bands[0])
	cloud_rules = '(%s == 1) && (%s == 0) && (%s == 0) && (%s == 0) && (%s == 1)' % (first_rule, second_rule, third_rule, fourth_rule, fifth_rule)

	expr_c = '%s = if( %s, 0, null( ) )' % (cloud_def, cloud_rules)
	
	gscript.mapcalc( expr_c,  overwrite=True)
	#print expr

	gscript.run_command('r.to.vect', input=cloud_def, output=tmp["cloud_v"], type='area', flags='s', overwrite=True)

	gscript.run_command('v.clean', input=tmp["cloud_v"], output=cloud_mask, tool='rmarea', threshold=cloud_clean_T, overwrite=True)

	### end of Clouds detection ####


	### start of shadows detection ###

	sixth_rule = '(((%s > %s) && (%s < %s) && (%s < 0.1) && (%s < 0.1)) || ((%s < %s) && (%s < %s) && (%s < 0.1) && (%s < 0.1) && (%s < 0.1)))' % (f_bands[0], f_bands[6], f_bands[0], f_bands[3], f_bands[0], f_bands[6], f_bands[0], f_bands[6], f_bands[0], f_bands[3], f_bands[0], f_bands[6], f_bands[3])
	seventh_rule = '(%s - %s)' % (f_bands[1], f_bands[0])
	shadow_rules = '((%s == 1) && (%s < 0.007))' % (sixth_rule, seventh_rule)
	
	expr_s = '%s = if( %s, 0, null( ) )' % (shadow_temp, shadow_rules)
	
	gscript.mapcalc( expr_s,  overwrite=True)

	gscript.run_command('r.to.vect', input=shadow_temp, output=tmp["shadow_temp_v"], type='area', flags='s', overwrite=True)

	gscript.run_command('v.clean', input=tmp["shadow_temp_v"], output=tmp["shadow_temp_mask"], tool='rmarea', threshold=shadow_clean_T, overwrite=True)

	### end of shadows detection ###


	#####################################################################
	# START shadows cleaning Procedure (remove shadows misclassification)
	#####################################################################

	### start shadow mask preparation ###

	gscript.message('--- start working! ---')
	
	gscript.run_command('v.centroids', input=tmp["shadow_temp_mask"], output=tmp["centroid"], overwrite=True, quiet=True)

	gscript.run_command('v.db.droptable', map=tmp["centroid"], flags='f')

	gscript.run_command('v.db.addtable', map=tmp["centroid"], columns='value')

	gscript.run_command('v.db.update', map=tmp["centroid"], layer=1, column='value', value=1)
	
	gscript.run_command('v.dissolve', input=tmp["centroid"], column='value', output=tmp["dissolve"], overwrite=True, quiet=True)

	gscript.run_command('v.category', input=tmp["dissolve"], type='point,line,boundary,centroid,area,face,kernel', output=tmp["delcat"], option='del', cat=-1, overwrite=True, quiet=True)
	
	gscript.run_command('v.category', input=tmp["delcat"], type='centroid,area', output=tmp["addcat"], option='add', overwrite=True, quiet=True)

	gscript.run_command('v.db.droptable', map=tmp["addcat"], flags='f')

	gscript.run_command('v.db.addtable', map=tmp["addcat"], columns='value')

	### end shadow mask preparation ### 

	### start cloud mask preparation ###

	gscript.run_command('v.db.droptable', map=cloud_mask, flags='f')

	gscript.run_command('v.db.addtable', map=cloud_mask, columns='value')

	### end cloud mask preparation ###   

	### shift cloud mask using dE e dN ###
	# start reading mean sun zenith and azimuth from xml file to compute dE and dN automatically #

	xml_tree = et.parse(mtd_file)
	root = xml_tree.getroot()

	ZA = []

	for elem in root[1]:  
		for subelem in elem[1]:
			ZA.append (subelem.text)

	#print ZA

	z = float(ZA[0])
	a = float(ZA[1])

	gscript.message('--- the mean sun Zenith is: %.3f deg ---'% z)

	gscript.message('--- the mean sun Azimuth is: %.3f deg ---'% a)

	#print Ze
	#print Az
	#print z
	#print a

	# stop reading mean sun zenith and azimuth from xml file to compute dE and dN automatically #

	H = 1000
	dH = 100
	HH = []
	dE = []
	dN = []
	AA = []

	while H <= 4000:

		z_deg_to_rad = math.radians(z)

		tan_Z = math.tan(z_deg_to_rad)
		#print tan_Z

		a_deg_to_rad = math.radians(a)
		cos_A = math.cos(a_deg_to_rad)
		sin_A = math.sin(a_deg_to_rad)
		#print cos_A
		#print sin_A

		E_shift = (-H * tan_Z * sin_A)
		N_shift = (-H * tan_Z * cos_A)

		dE.append (E_shift)
		#print dE

		dN.append (N_shift)
		#print dN

		HH.append(H)
	
		H = H + dH

		gscript.run_command('v.transform', input=cloud_mask, output=tmp["cl_shift"], xshift=E_shift, yshift=N_shift, overwrite=True, quiet=True)
		
		gscript.run_command('v.overlay', ainput=tmp["addcat"], binput=tmp["cl_shift"], operator='and', output=tmp["overlay"], overwrite=True, quiet=True)

		gscript.run_command('v.db.addcolumn', map=tmp["overlay"], columns='area double')

		area = gscript.read_command('v.to.db', map=tmp["overlay"], option='area', columns='area', flags='c')

		area2 = gscript.parse_key_val(area, sep='|')

		AA.append (float(area2['total area']))

	#print AA
	#print HH
	#print dE
	#print dN

	index_maxAA = numpy.argmax(AA)

	gscript.run_command('v.transform', input=cloud_mask, output=tmp["cl_shift"], xshift=dE[index_maxAA], yshift=dN[index_maxAA], overwrite=True, quiet=True)
		
	gscript.run_command('v.select', ainput=tmp["addcat"], atype='point,line,boundary,centroid,area', binput=tmp["cl_shift"], btype='point,line,boundary,centroid,area', output=shadow_mask, operator='intersects', overwrite=True, quiet=True)

	gscript.message('--- the estimated clouds height is: %d m ---'% HH[index_maxAA])

	gscript.message('--- the estimated east shift is: %.2f m ---'% dE[index_maxAA])

	gscript.message('--- the estimated north shift is: %.2f m ---'% dN[index_maxAA])

def cleanup():
        gscript.run_command("g.remove", flags="f", type='raster,vector', name=",".join([tmp[m] for m in tmp.keys()]), quiet=True)

if __name__ == "__main__":
	atexit.register(cleanup)
    	main()

