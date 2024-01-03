'''
==============================================================================
EXAMPLE 3: Run MOOSE in sequential then parallel

Author: Lloyd Fletcher, Rory Spencer
==============================================================================
'''
import os
from pathlib import Path
from mooseherder import MooseHerd
from mooseherder import MooseRunner
from mooseherder import InputModifier

if __name__ == '__main__':
    print('------------------------------------------')
    print('EXAMPLE 3: Herd Setup')
    print('------------------------------------------')

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
    herd.para_opts(n_moose=4,tasks_per_moose=1,threads_per_moose=2,redirect_out=True)

     # Send all the output to the examples directory and clear out old output
    herd.set_base_dir('examples/')
    herd.clear_dirs()
    herd.create_dirs()

    # Create variables to sweep in a list of dictionaries, 8 combinations possible.
    n_elem_y = [25,50]
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]
    moose_vars = list()
    for nn in n_elem_y:
        for ee in e_mod:
            for pp in p_rat:
                moose_vars.append({'n_elem_y':nn,'e_modulus':ee,'p_ratio':pp})
        
    print('------------------------------------------')
    print('EXAMPLE 3c: Run MOOSE in parallel')
    print('------------------------------------------')

    # Run all variable combinations across 4 MOOSE instances with two runs saved in
    # each moose-workdir
    herd.run_para(moose_vars)

    print('Run time (parallel) = '+'{:.3f}'.format(herd.get_sweep_time())+' seconds')
    print('------------------------------------------')
    print()

    herd.read_results_once()

