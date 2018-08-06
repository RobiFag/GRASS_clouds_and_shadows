#####This bash script represents the first main step of those listed in the proposal
##The other two steps, shape index and spatial relation between clouds and shadows, are carried out with qgis at the moment


#import bands atmospherically corrected using arcsi (scale factor 1000 instead of 10000)


#############################################
# INPUT
#############################################

#bands 
b1=blu
b2=green
b3=red
b4=nir
b5=nir8a
b7=swir11
b8=swir12

#############################################
# START Procedure
#############################################
g.region -pa rast=$b1

r.mapcalc --overwrite "blu_float = 1.0*($b1)/1000"
r.mapcalc --overwrite "green_float = 1.0*($b2)/1000"
r.mapcalc --overwrite "red_float = 1.0*($b3)/1000"
r.mapcalc --overwrite "nir_float = 1.0*($b4)/1000"
r.mapcalc --overwrite "nir8a_float = 1.0*($b5)/1000"
r.mapcalc --overwrite "swir11_float = 1.0*($b7)/1000"
r.mapcalc --overwrite "swir12_float = 1.0*($b8)/1000"

fb1=blu_float
fb2=green_float
fb3=red_float
fb4=nir_float
fb5=nir8a_float
fb7=swir11_float
fb8=swir12_float


r.mapcalc --overwrite "base_M = 1"
r.stats.zonal base=base_M cover=$fb1 method=max output=blu_float_max --overwrite
r.stats.zonal base=base_M cover=$fb2 method=max output=green_float_max --overwrite
r.stats.zonal base=base_M cover=$fb3 method=max output=red_float_max --overwrite
r.stats.zonal base=base_M cover=$fb4 method=max output=nir_float_max --overwrite
r.stats.zonal base=base_M cover=$fb5 method=max output=nir8a_float_max --overwrite
r.stats.zonal base=base_M cover=$fb7 method=max output=swir11_float_max --overwrite
r.stats.zonal base=base_M cover=$fb8 method=max output=swir12_float_max --overwrite

#### start of Clouds detection  (some rules from litterature)###
                                                 
r.mapcalc --overwrite "first_rule = ($fb1 > (0.08*blu_float_max)) && ($fb2 > (0.08*green_float_max)) && ($fb3 > (0.08*red_float_max))"
                                                   
r.mapcalc --overwrite "second_rule = ($fb3 < (0.08*red_float_max) *1.5) &&( $fb3  > $fb8 *1.3)"
                                                                                                          
r.mapcalc --overwrite "third_rule = ($fb7 <(0.1*swir11_float_max)) &&( $fb8 <(0.1*swir12_float_max))"

r.mapcalc --overwrite "sixth_rule = if($fb5 == max($fb5 , 2 * $fb1, 2 *$fb2 , 2 * $fb3))"

r.mapcalc --overwrite "cloud_def = (first_rule ==1) && (second_rule ==0) && (third_rule ==0) && (sixth_rule ==0) && ($fb1 > 0.2)"  ### blue_band > 0.2 added to exclude lots of misclassification (fields, roofs, etc.) ###

r.null map=cloud_def setnull=0 --overwrite 

r.to.vect -s input=cloud_def output=cloud_def_v type=area --overwrite

v.clean --overwrite input=cloud_def_v output=cloud_def_v_clean tool=rmarea threshold=50000

### end of Clouds detection ####


### start of shadows detection (It seems to be land cover dependent) ###

r.mapcalc --overwrite expression="rule_blue_max_or_min_swir12 = ( (  $fb1 > $fb8 ) || ($fb1 <  $fb8  ) ) &&   ( $fb1  < $fb4 )   && ( $fb1 <0.1 )  && ( $fb8 <0.1 ) && ($fb4<0.1 )" 

r.mask raster=rule_blue_max_or_min_swir12 maskcats=1

r.mapcalc --overwrite "diff_blu_green_2nd = ($fb2 - $fb1)"

r.mapcalc --overwrite "shadow_def_2nd = (rule_blue_max_or_min_swir12 == 1) && (diff_blu_green_2nd < 0.007)"

r.null map=shadow_def_2nd setnull=0 --overwrite

r.to.vect -s input=shadow_def_2nd output=shadow_def_2nd_v type=area --overwrite

v.clean --overwrite input=shadow_def_2nd_v output=shadow_def_2nd_v_clean tool=rmarea threshold=10000

### end of shadows detection ###

r.mask -r

##############################################################################################
# END Procedure - the final outputs are two vector "masks", one for clouds and one for shadows
##############################################################################################

                      
                      
