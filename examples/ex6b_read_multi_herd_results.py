'''
==============================================================================
EXAMPLE 6b: Run MOOSE in parallel mode then read sweep results

Author: Lloyd Fletcher, Rory Spencer
==============================================================================
'''
import time
import os
from pathlib import Path
from pprint import pprint
from mooseherder import MooseHerd
from mooseherder import MooseRunner
from mooseherder import InputModifier

def main():
    print('-----------------------------------------------------------')
    print('EXAMPLE 6b: Parallel Herd Setup & Run')
    print('-----------------------------------------------------------')

    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    moose_input = 'scripts/moose/moose-mech-simple.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    
    # Start the herd and create working directories
    herd = MooseHerd(moose_runner,moose_modifier)

    # Set the parallelisation options, we have 8 combinations of variables and
    # 4 MOOSE intances running, so 2 runs will be saved in each working directory
    herd.para_opts(n_moose = 4, tasks_per_moose = 1, threads_per_moose = 2,
                   redirect_out = True, create_dirs = False)

     # Send all the output to the examples directory and clear out old output
    herd.set_base_dir('examples/', clear_old_dirs = True)
    herd.clear_dirs()
    herd.create_dirs()

    # Create variables to sweep in a list of dictionaries, 8 combinations possible.
    n_elem_x = [10,20]
    n_elem_y = [10,20]
    e_mod = [1e9,2e9]
    moose_vars = list()
    for nx in n_elem_x:
        for ny in n_elem_y:
            for ee in e_mod:
                moose_vars.append({'n_elem_x':nx,'n_elem_y':ny,'e_modulus':ee})

    print()
    num_runs = 4
    print('Running MOOSE in parallel x{:d}.'.format(num_runs))
    print()

    for rr in range(num_runs):
        herd.run_para(moose_vars)

        print('Run time, {:d} (parallel) = {:.3f}'.format(rr,herd.get_sweep_time())+' seconds')
        print('-----------------------------------------------------------')
        print()

    print('-----------------------------------------------------------')
    print('EXAMPLE 6b: Read All Herd Output')
    print('-----------------------------------------------------------')
    vars_to_read = ['disp_x','disp_y','disp_z','strain_xx']
    elem_blocks = [0,0,0,1]

    print('Variable keys to read as list:')
    pprint(vars_to_read)
    print()
    print('Element blocks associated with variable keys as list:')
    pprint(elem_blocks)
    print()

    all_output = herd.read_all_output_keys()

    print('All output files from multiple calls to run_para:')
    pprint(all_output)

    print('-----------------------------------------------------------')
    print('Reading all output files sequentially as a list(dict).')
    print()

    start_read = time.perf_counter()
    read_all = herd.read_results_sequential(vars_to_read,None,elem_blocks)
    end_read = time.perf_counter()

    print('Read time (sequential) = {:.3f} seconds'.format(end_read-start_read))
    print()   
    print('Number of simulation outputs: {:d}'.format(len(read_all)))
    print('Variable keys for simulation output:')
    print(list(read_all[0].keys()))
    print()

    print('-----------------------------------------------------------')
    print('Reading all output files in parallel as list(dict).')
    print()
    start_read = time.perf_counter()
    read_all = herd.read_results_para(vars_to_read)
    end_read = time.perf_counter()

    print('Read time (parallel) = {:.3f} seconds'.format(end_read-start_read))
    print()   
    print('Number of simulation outputs: {:d}'.format(len(read_all)))
    print('Variable keys for simulation output:')
    print(list(read_all[0].keys()))
    print()

    print('-----------------------------------------------------------')
    
    print('NOTE: depening on hardware and simulations parallel read may be slower!')

if __name__ == '__main__':
    main()
