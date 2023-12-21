'''
==============================================================================
DEV: READ EXODUS FILE

Author: Lloyd Fletcher
==============================================================================
'''
import time
import netCDF4 as nc
import numpy as np
from pprint import pprint
from mooseherder import ExodusReader

# Read the results
output_file = 'scripts/moose-test-cases/moose-mech-block-2d-o1.e'
ex_data = ExodusReader(output_file)

coords = ex_data.get_coords()

ex_data.get_elem_data('strain_xx',1)

node_map = ex_data.get_var('node_num_map')
print()
print(type(node_map))
print(node_map)
print(node_map.shape)
print()

elem_map = ex_data.get_var('elem_num_map')
print()
print(type(elem_map))
print(elem_map)
print(elem_map.shape)
print()

connect = ex_data.get_var('connect1')
print()
print(type(connect))
print(connect)
print(connect.shape)
print()

ex_data.print_vars()

print()
print('node var names')
pprint(ex_data.node_var_names)
print()
print('elem var names')
pprint(ex_data.elem_var_names)
print()

#print()
#print(ex_data._data.variables['elem_var_tab'])

'''
Required Variables:
time_whole
coordx
coordy
coordz
name_elem_var
vals_nod_var1
vals_nod_var2
'coor_names'
'node_num_map'
'connect1'
'elem_num_map'
'name_elem_var'
'vals_elem_var1eb1'
'vals_elem_var2eb1'
'vals_elem_var3eb1'
'vals_elem_var4eb1'
'''
