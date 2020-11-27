# configurable_search
QGIS plugin for attribute search

Seach configurations are set in a configuration file. In the configuration file 
group of parameters can be given The default configuration, which is loaded 
automatic when the plug-in loaded, is located in the folder of the plugin 
(called default.cfg). Before you start using this plug-in, you have to customize
that. There are three type of available groups in configuration file.

[base]

There is only one parameter for this group *dir* which is a base directory 
for all the following relative paths of data sets files.

[search_group*n*]

Where n is a number to make the group name unique. For the search you can define
a *name* which will be visible in the UI. Tha *path* parameter is a comma 
separated list of paths to the datasource to search.
The *field* parameter defines the table column, all sources must have the same 
column name to search in.

[include]

You can use this group to redirect to an external file giving a path. The rest
of the config file is not considered. This can be useful for a group of users
using common projects/layers from a network drive. They can create a local 
configuration to include a common configuration on a network drive. So a single 
config can be administered centraly.

The sources of Search Layers plugin were used to create this plugin
https://github.com/NationalSecurityAgency/qgis-searchlayers-plugin
