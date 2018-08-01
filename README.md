# 2018 GSoC project - GRASS GIS module for Sentinel-2 cloud and shadow detection
Public repository for GRASS GIS module of clouds and shadows detection (GSoC 2018 project)

Optical sensors are unable to penetrate clouds leading to related incorrect reflectance values. Unlike Landsat images, Sentinel 2 datasets do not include thermal and Quality Assessment bands that simplify the detection of clouds avoiding erroneous classification. At the same time, clouds shadows on the ground lead to anomalous reflectance values which have to be taken into account during the image processing.<br>
Before GSoC 2018, only a specific module for Landsat automatic cloud coverage assessment was available within GRASS GIS (i.landsat.acca) while regarding shadows, no specific module was available.

The project creates a specific module for GRASS GIS application (<b>i.sentinel.mask</b>) which implements an automatic procedure for clouds and shadows detection in Sentinel 2 images. The procedure is based on an algorithm, developed within my PhD research, which allows to automatically identify clouds and their shadows applying some rules on reflectance values (values thresholds, comparisons between bands, etc.). These have been defined starting from rules found in literature and conveniently refined. In order to increase the accuracy of the final results, a control check is implemented. Clouds and shadows are spatially intersected in order to remove misclassified areas. The final outputs are two different vector files (OGR standard formats), one for clouds and one for shadows.

More information about the algorithm and the module can be found here, <a href="https://grass.osgeo.org/grass74/manuals/addons/i.sentinel.mask.html" target="_blank">i.sentinel.mask</a>.

i.sentinel.mask is a real complete GRASS GIS addon module (with GUI and manual page) and it is now available on the official <a href="https://trac.osgeo.org/grass/browser/grass-addons/grass7/imagery/i.sentinel.mask" target="_blank">GRASS GIS SVN repository</a>.<br>
It can be easyly installed within GRASS GIS using the module g.extension:

<em>g.extension extension=i.sentinel.mask operation=add</em>

<b>The resulting clouds and shadows maps obtained running i.sentinel.mask.</b>
![i_sentinel_mask_ES](i.sentinel.mask/i_sentinel_mask_ES.png)

To run i.sentinel.mask, the bands of the desired Sentinel 2 images have to be imported and the atmospheric correction has to be applied.<br>
In order to make tha data preparation easier, another GRASS GIS addon module has been developend within the GSoC project.

i.sentinel.preproc is a module for the preprocessing of Sentinel 2 images (Level-1C Single Tile product) which wraps the import and the atmospheric correction using respectively two existing GRASS GIS modules, i.sentinel.import and i.atcorr.<br>
The aim is to provide a simplified module which allows importing images and performing the atmospheric correction avoiding users to provide all the required input parameters manually. The module should help users in preparing data to use as input for i.sentinel.mask. In fact, it makes expecially the atmospheric correction procedure easier and faster because it allows performing atmospheric correction of all bands of a Sentinel 2 scene with a single process and it retrieves most of the required input parameters from the image itself. Moreover, one of the possible output of i.sentinel.preproc is a text file to be used as input for i.sentinel.mask.

More information about the module can be found here, ![i.sentinel.preproc.html].

i.sentinel.preproc is a real complete GRASS GIS addon module (with GUI and manual page) and it can be easyly installed from this GitHub repository within GRASS GIS using the module g.extension:

<em>g.extension extension=i.sentinel.mask operation=add url=https://github.com/RobiFag/GRASS_clouds_and_shadows</em>

It will be soon available on the official GRASS GIS SVN repository!

NOTE: the starting idea was to create a single module which wrapped all the functionalities provided by i.sentinel.mask and i.sentinel.preproc but, following the suggestions of the dev community it was decided to develop two different modules.

N.B.All the file concerning i.sentinel.mask have been moved to a subfolder in the GitHub repository in order to make available the new module i.sentinel.preproc from Github using the GRASS GIS module g.extension.
If you want to install i.sentinel.mask you have to use the the official GRASS GIS SVN repository because g.extension for GitHub repository download currently support only module (Makefile) at the top level.



