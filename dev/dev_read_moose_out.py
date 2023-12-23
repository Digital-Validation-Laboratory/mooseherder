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

def debug_var(tag,var):
    print(tag)
    print(type(var))
    print(var.shape)
    print()

# Read the results
output_dir = 'scripts/moose-test-cases/'
output_file = 'moose-mech-subdom-2d-o2-moo2_out.e'

ex_data = ExodusReader(output_dir+output_file)

coords = ex_data.get_coords()
print()
print('NODE COORDS')
print(type(coords))
print(coords.shape)
print()

var_str = 'strain_xx'

try:
    node_data = ex_data.get_node_data(var_str)
except:
    node_data = np.array([])

elem_data = ex_data.get_elem_data(var_str,1)

debug_var(var_str,node_data)
debug_var(var_str,elem_data)


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