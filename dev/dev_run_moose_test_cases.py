'''
==============================================================================
GENERATE OUTPUTS FOR TESTS

Author: Lloyd Fletcher
==============================================================================
'''
import time
import os
from pathlib import Path
from mooseherder import MooseRunner

print('------------------------------------------')
print('GENERATE MOOSE HERDER TEST CASES')
print('------------------------------------------')

path_parts = Path(os.getcwd()).parts
user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

# Create the moose runner with correct paths to moose and apps
moose_dir = os.path.join(user_dir,'moose')
moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
moose_app_name = 'proteus-opt'
moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)

# Set input and parallelisation options
moose_runner.set_opts(n_tasks=1,n_threads=4,redirect=True)

# These are all the test cases required
input_path = 'scripts/moose-test-cases/'
'''
input_files = [ 'moose-mech-block-2d-o1.i', \
                'moose-mech-block-2d-o2.i', \
                'moose-mech-block-3d-o1.i', \
                'moose-mech-block-3d-o2.i', \
                'moose-mech-block-2d-o2-moo2.i', \
                'moose-mech-block-3d-o2-moo2.i']
'''
input_files = [ 'moose-mech-block-2d-o2-moo0.i', \
                'moose-mech-block-2d-o2-moo1.i', \
                'moose-mech-block-2d-o2-moo2.i', \
                'moose-mech-subdom-2d-o2-moo0.i', \
                'moose-mech-subdom-2d-o2-moo1.i', \
                'moose-mech-subdom-2d-o2-moo2.i']

for ii in input_files:
    start_time = time.perf_counter()

    moose_runner.set_input_file(input_path+ii)
    print('Running moose test case with:')
    print(moose_runner.get_run_str())

    moose_runner.run()
    end_time = time.perf_counter()
    print('MOOSE run time = '+'{:.3f}'.format(end_time-start_time)+' seconds')
    print()

print('Test data generation complete.')
print()