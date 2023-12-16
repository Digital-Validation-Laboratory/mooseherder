#==============================================================================
# RUN MOOSE FROM PYTHON 
# Use the os module and terminal commands to run gmsh and MOOSE from python
#
# Author: Lloyd Fletcher
#==============================================================================
import time
import os
from pathlib import Path
from mooseherder import MooseRunner

path_parts = Path(os.getcwd()).parts
user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

# Create the moose runner with correct paths to moose and apps
moose_dir = os.path.join(user_dir,'moose')
moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
moose_app_name = 'proteus-opt'
moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)

# Set input and parallelisation options
moose_runner.set_para_opts(n_tasks=4,n_threads=2)
input_file = 'scripts/moose-mech.i'

# Run the MOOSE input file
start_time = time.perf_counter()
moose_runner.run(input_file)
end_time = time.perf_counter()

print()
print('------------------------------------------')
print('Run time = '+str(end_time-start_time)+' seconds')
print('------------------------------------------')

