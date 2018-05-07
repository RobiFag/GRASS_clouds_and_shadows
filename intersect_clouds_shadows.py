#!/usr/bin/env python 
# coding=utf-8

import grass.script as gscript
import math,os,sys,shutil,re,glob,numpy
import xml.etree.ElementTree as et

def main ():
	
	#####################################################################
	# START shadows cleaning Procedure (remove shadows misclassification)
	#####################################################################

	### start shadow mask preparation ###

	gscript.message('--- start working! ---')
	
	gscript.run_command('v.centroids', input='shadow_def_3rd_v_clean', output='shadow_def_3rd_v_clean_cen', overwrite=True, quiet=True)

	gscript.run_command('v.db.droptable', map='shadow_def_3rd_v_clean_cen', flags='f')

	gscript.run_command('v.db.addtable', map='shadow_def_3rd_v_clean_cen', columns='value')

	gscript.run_command('v.db.update', map='shadow_def_3rd_v_clean_cen', layer=1, column='value', value=1)
	
	gscript.run_command('v.dissolve', input='shadow_def_3rd_v_clean_cen', column='value', output='shadow_def_3rd_v_clean_cen_dis', overwrite=True, quiet=True)

	gscript.run_command('v.category', input='shadow_def_3rd_v_clean_cen_dis', type='point,line,boundary,centroid,area,face,kernel', output='shadow_def_3rd_v_clean_cen_dis_delcat', option='del', cat=-1, overwrite=True, quiet=True)
	
	gscript.run_command('v.category', input='shadow_def_3rd_v_clean_cen_dis_delcat', type='centroid,area', output='shadow_def_3rd', option='add', overwrite=True, quiet=True)

	gscript.run_command('v.db.droptable', map='shadow_def_3rd', flags='f')

	gscript.run_command('v.db.addtable', map='shadow_def_3rd', columns='value')

	### end shadow mask preparation ### 

	### start cloud mask preparation ###

	gscript.run_command('v.db.droptable', map='cloud_def_v_clean', flags='f')

	gscript.run_command('v.db.addtable', map='cloud_def_v_clean', columns='value')

	### end cloud mask preparation ###   

	### shift cloud mask using dE e dN ###

	# start reading mean sun zenith and azimuth from xml file to compute dE and dN automatically #

	#z = 50.83 #zenith
	#a = 165.51 #azimuth

	xml_tree = et.parse('/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/sentinel2/MTD_TL.xml')
	root = xml_tree.getroot()

	ZA = []

	for elem in root[1]:  
		for subelem in elem[1]:
			ZA.append (subelem.text)

	#print ZA

	z = float(ZA[0])
	a = float(ZA[1])

	#zz = round(Ze, 3)
	#aa = round(Az, 3)

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

		gscript.run_command('v.transform', input='cloud_def_v_clean', output='cloud_def_v_clean_shift', xshift=E_shift, yshift=N_shift, overwrite=True, quiet=True)
		
		gscript.run_command('v.overlay', ainput='shadow_def_3rd', binput='cloud_def_v_clean_shift', operator='and', output='intersect_cloud_shadow', overwrite=True, quiet=True)

		gscript.run_command('v.db.addcolumn', map='intersect_cloud_shadow', columns='area double')

		area = gscript.read_command('v.to.db', map='intersect_cloud_shadow', option='area', columns='area', flags='c')

		area2 = gscript.parse_key_val(area, sep='|')

		AA.append (float(area2['total area']))

	#print AA
	#print HH
	#print dE
	#print dN

	index_maxAA = numpy.argmax(AA)

	gscript.run_command('v.transform', input='cloud_def_v_clean', output='cloud_def_v_clean_shift', xshift=dE[index_maxAA], yshift=dN[index_maxAA], overwrite=True, quiet=True)
		
	gscript.run_command('v.select', ainput='shadow_def_3rd', atype='point,line,boundary,centroid,area', binput='cloud_def_v_clean_shift', btype='point,line,boundary,centroid,area', output='shadow_mask', operator='intersects', overwrite=True, quiet=True)

	gscript.message('--- the estimated clouds height is: %d m ---'% HH[index_maxAA])

	gscript.message('--- the estimated east shift is: %.2f m ---'% dE[index_maxAA])

	gscript.message('--- the estimated north shift is: %.2f m ---'% dN[index_maxAA])


if __name__ == "__main__": 
    main()
