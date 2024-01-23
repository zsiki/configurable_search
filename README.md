# configurable_search
QGIS plugin for attribute search

Seach configurations are set in a configuration file. In the configuration file 
group of parameters can be given The default configuration, which is loaded 
automatic when the plug-in loaded, is located in the folder of the plugin 
(called default.cfg). Before you start using this plug-in, you have to customize
that. There are three types of available groups in configuration file.

[base]

There is only one parameter for this group *dir* which is a base directory 
for all the following relative paths of data sets files.
*dir* can be empty in that case full paths have to be given in the search 
groups. 

[search_group*n*]

Where *n* is a number to make the group name unique. For the search you can define
a *name* which will be visible in the UI. The *path* parameter is a comma 
separated list of paths to the datasource or layer names to search. 
The *layer* parameter is an alternative definition to define search layers
by a comma separated list of layer names in QGIS.
You have to use layer name for database (e.g. PostGIS) layers.
For file based vector layers both *path* and *layer* can be used.
The *field* parameter defines the table column, all sources must have the same 
column name to search in.

[include]

You can use this group to redirect to an external file giving a path. The rest
of the config file is not considered. This can be useful for a group of users
using common projects/layers from a network drive. They can create a local 
configuration to include a common configuration on a network drive. So a single 
config can be administered centraly.

## 1st Sample configuration file

Sample for file based layers (shp, tab).

```
	[base]
	dir = /home/siki/work
	[search_group1]
	name = HRSZ
	path = full/parcels.tab,org/parcels.shp
	layer = Parcel
	field = parcel_id
	[search_group2]
	name = address
	path = full/address_points.shp
	field = address
	[search_group3]
	name=annotations
	path = full/anno.tab
	field = txt
```

## 2nd Sample configuration file

Sample using layer names of the QGIS project. It can be used for database
layers. This case layer names or absolut pathes are given in layer and path parameters respectively.
If path is emmpty the layer with the group name will be searched.

```
    [base]
    dir=
    [search_group1]
    name=Street names
    layer=streets
    field=name
    [searc_group2]
    layer=Address
    field=addr
    [search_group2]
    name=POI
    path=/home/user/shapes/pois.shp
    field=description
```

The sources of Search Layers plugin were used to create this plugin
https://github.com/NationalSecurityAgency/qgis-searchlayers-plugin
