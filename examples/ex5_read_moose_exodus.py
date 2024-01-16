"""
==============================================================================
EXAMPLE 5: Run MOOSE once with mooseherder and read the exodus output

Author: Lloyd Fletcher
==============================================================================
"""
import time
import os
from pathlib import Path
from pprint import pprint
from mooseherder import MooseRunner
from mooseherder import ExodusReader

def main():
    user_dir = Path.home()

    print('------------------------------------------')
    print('EXAMPLE 5: Run MOOSE once, read exodus.')
    print('------------------------------------------')
    # Create the moose runner with correct paths to moose and apps
    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)

    # Set input and parallelisation options
    moose_runner.set_opts(n_tasks=1, n_threads=4, redirect=True)
    input_file = 'scripts/moose/moose-mech-simple.i'
    moose_runner.set_input_file(input_file)

    # Run the MOOSE!
    print('Running moose with:')
    print(moose_runner.get_run_str())

    start_time = time.perf_counter()
    moose_runner.run()
    end_time = time.perf_counter()

    print()
    print('MOOSE run time = '+'{:.3f}'.format(end_time-start_time)+' seconds')
    print()
    print('------------------------------------------')

    output_file = 'scripts/moose/moose-mech-simple_out.e'
    print('Reading exodus file:')
    print(output_file)
    print()

    exodus_reader = ExodusReader(output_file)

    coords = exodus_reader.get_coords()
    print('Nodal Coordinates N[x,y,z]:')
    print(type(coords))
    print(coords.shape)
    print()

    sim_time = exodus_reader.get_time()
    print('Simulation time [t]:')
    print(type(sim_time))
    print(sim_time.shape)
    print()

    disp = exodus_reader.get_node_data('disp_x')
    print('X Displacement at nodes [N,t]:')
    print(type(disp))
    print(disp.shape)
    print()

    strain = exodus_reader.get_elem_data('strain_xx',1)
    print('XX Strain at elements [E,t]')
    print(type(strain))
    print(strain.shape)
    print()

    print('Printing all variable keys in exodus file:')
    exodus_reader.print_vars()
    print()

    print('Extracting variable: connect1 [E,4]')
    print('Note: simulation uses QUAD4 2D elements = 4 nodes per element.')
    ext_var = exodus_reader.get_var('connect1')
    print(type(ext_var))
    print(ext_var.shape)
    print()

    print('------------------------------------------')
    print()

if __name__ == '__main__':
    main()