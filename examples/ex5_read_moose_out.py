#==============================================================================
# RUN MOOSE FROM PYTHON 
# Use the os module and terminal commands to run gmsh and MOOSE from python
#
# Author: Lloyd Fletcher
#==============================================================================
import time
import netCDF4
import numpy as np
from mooseherder import MooseRunner
from pprint import pprint

#------------------------------------------------------------------------------
class ExodusReader:
    def __init__(self):
        pass

    
#------------------------------------------------------------------------------

# Read the results
output_file = 'examples/model-mech-test_out.e'
mout = netCDF4.Dataset(output_file)
X = np.array(mout.variables['coordx'])
Y = np.array(mout.variables['coordy'])

for vv in mout.variables:
    pprint(vv)

vs = 'name_elem_var'
'''
Required Variables:
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

print()
pprint(mout.variables[vs])
print()

nn = netCDF4.chartostring(np.array(mout.variables[vs]))
print()
pprint(nn)
print()
