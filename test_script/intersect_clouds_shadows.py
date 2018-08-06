#!/usr/bin/env python 
# coding=utf-8

import grass.script as gscript
import math,os,sys,shutil,re,glob,numpy,time,atexit
import xml.etree.ElementTree as et

def main ():

	#temporary map names
    	global tmp, t
    	tmp = {}
    	t = True

	#input file
	mtd_file = '/home/roberta/remote/Progetti_convegni/ricerca/2015_2018_PhD_roberta/sentinel2/MTD_TL.xml' ####change MTD_TL file path!!!####
	
	mapset = gscript.gisenv()['MAPSET']	

	# prepare temporary map raster names
    	processid = "%.7f" % time.time()
	processid = processid.replace(".", "_")
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
	
	#####################################################################
	# START shadows cleaning Procedure (remove shadows misclassification)
	#####################################################################

	### start shadow mask preparation ###

	gscript.message('--- start working! ---')
	
	gscript.run_command('v.centroids', input='shadow_temp_mask', output=tmp["centroid"], overwrite=True, quiet=True)

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

	gscript.run_command('v.db.droptable', map='cloud_mask', flags='f')

	gscript.run_command('v.db.addtable', map='cloud_mask', columns='value')

	### end cloud mask preparation ###   


	### shift cloud mask using dE e dN ###

	# start reading mean sun zenith and azimuth from xml file to compute dE and dN automatically #

	#z = 50.83 #zenith
	#a = 165.51 #azimuth

	xml_tree = et.parse(mtd_file)
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

		gscript.run_command('v.transform', input='cloud_mask', output=tmp["cl_shift"], xshift=E_shift, yshift=N_shift, overwrite=True, quiet=True)
		
		gscript.run_command('v.overlay', ainput=tmp["addcat"], binput=tmp["cl_shift"], operator='and', output=tmp["overlay"], overwrite=True, quiet=True)

		gscript.run_command('v.db.addcolumn', map=tmp["overlay"], columns='area double')
		#print tmp["overlay"]

		area = gscript.read_command('v.to.db', map=tmp["overlay"], option='area', columns='area', flags='c')
		#print area

		area2 = gscript.parse_key_val(area, sep='|')

		AA.append (float(area2['total area']))

	#print AA
	#print HH
	#print dE
	#print dN

	index_maxAA = numpy.argmax(AA)

	gscript.run_command('v.transform', input='cloud_mask', output=tmp["cl_shift"], xshift=dE[index_maxAA], yshift=dN[index_maxAA], overwrite=True, quiet=True)
		
	gscript.run_command('v.select', ainput=tmp["addcat"], atype='point,line,boundary,centroid,area', binput=tmp["cl_shift"], btype='point,line,boundary,centroid,area', output='shadow_mask', operator='intersects', overwrite=True, quiet=True)

	gscript.message('--- the estimated clouds height is: %d m ---'% HH[index_maxAA])

	gscript.message('--- the estimated east shift is: %.2f m ---'% dE[index_maxAA])

	gscript.message('--- the estimated north shift is: %.2f m ---'% dN[index_maxAA])
    
def cleanup():
        gscript.run_command("g.remove", flags="f", type='vector', name=",".join([tmp[m] for m in tmp.keys()]), quiet=True)


if __name__ == "__main__":
    	atexit.register(cleanup) 
    	main()
