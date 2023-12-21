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
moose_runner.set_opts(n_tasks=4,n_threads=2,redirect=True)

# These are all the test cases required
input_files = [ 'scripts/moose-mech-simple.i', \
                'scripts/moose-mech-sub-dom.i', \
                'scripts/moose-mech-sub-dom-order2.i', \
                'scripts/moose-mech-two-beams.i', \
                'scripts/moose-mech-thermal-exp.i']

for ii in input_files:
    start_time = time.perf_counter()

    moose_runner.set_input_file(ii)
    print('Running moose test case with:')
    print(moose_runner.get_run_str())

    moose_runner.run()
    end_time = time.perf_counter()
    print('MOOSE run time = '+'{:.3f}'.format(end_time-start_time)+' seconds')
    print()

print('Test data generation complete.')
print()