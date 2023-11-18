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

# Create the runner
moose_dir = '/home/lloydf/moose'
app_dir = '/home/lloydf/moose-workdir/proteus'
app_name = 'proteus-opt'
runner = MooseRunner(moose_dir,app_dir,app_name)

# Set parallelisation options
runner.set_para_opts(n_tasks=4,n_threads=2)

# Specify the input file to run with relative path
input_file = 'examples/model-mech-test.i'

# Start the run timer
start_time = time.perf_counter()

# Run the MOOSE input file
# runner.run(input_file)

# Print the run time
end_time = time.perf_counter()
print()
print('------------------------------------------')
print('Run time = '+str(end_time-start_time)+' seconds')
print('------------------------------------------')

# Read the results
output_file = 'examples/model-mech-test_out.e'
mout = netCDF4.Dataset(output_file)
X = np.array(mout.variables['coordx'])
Y = np.array(mout.variables['coordy'])

for vv in mout.variables:
    pprint(vv)

#pprint(mout.variables)

