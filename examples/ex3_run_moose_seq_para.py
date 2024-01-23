'''
==============================================================================
EXAMPLE 3: Run MOOSE in sequential then parallel mode with mooseherder

Author: Lloyd Fletcher, Rory Spencer
==============================================================================
'''
import os
from pathlib import Path
from mooseherder import MooseHerd
from mooseherder import MooseRunner
from mooseherder import InputModifier


USER_DIR = Path.home()

def main():
    """main: run moose once, sequential then parallel.
    """
    print('------------------------------------------')
    print('EXAMPLE 3: Herd Setup')
    print('------------------------------------------')

    moose_dir = USER_DIR / 'moose'
    moose_app_dir = USER_DIR / 'moose-workdir/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = Path('scripts/moose/moose-mech-simple.i')

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_runner.set_opts(n_tasks = 1, n_threads = 2, redirect_out = True)

    # Start the herd and create working directories
    herd = MooseHerd([moose_runner],[moose_modifier])

    # Set the parallelisation options, we have 8 combinations of variables and
    # 4 MOOSE intances running, so 2 runs will be saved in each working directory
    herd.set_opts(n_moose = 4, create_dirs = False)

     # Send all the output to the examples directory and clear out old output
    herd.set_base_dir(Path('examples/'), clear_old_dirs = True)
    herd.clear_dirs()
    herd.create_dirs()

    # Create variables to sweep in a list of dictionaries, 8 combinations possible.
    n_elem_y = [10,20]
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]
    moose_vars = list([])
    for nn in n_elem_y:
        for ee in e_mod:
            for pp in p_rat:
                moose_vars.append({'n_elem_y':nn,'e_modulus':ee,'p_ratio':pp})

    print('Herd sweep variables:')
    for vv in moose_vars:
        print(vv)

    print()
    print('------------------------------------------')
    print('EXAMPLE 3a: Run MOOSE once')
    print('------------------------------------------')

    # Single run saved in moose-workdir-1
    herd.run_once(0,moose_vars[0])

    print('Run time (once) = '+'{:.3f}'.format(herd.get_iter_time())+' seconds')
    print('------------------------------------------')
    print()

    print('------------------------------------------')
    print('EXAMPLE 3b: Run MOOSE sequentially')
    print('------------------------------------------')

    # Run all variable combinations (8) sequentially in moose-workdir-1
    herd.run_sequential(moose_vars)

    print('Run time (sequential) = '+'{:.3f}'.format(herd.get_sweep_time())+' seconds')
    print('------------------------------------------')
    print()
    print('------------------------------------------')
    print('EXAMPLE 3c: Run MOOSE in parallel')
    print('------------------------------------------')

    # Run all variable combinations across 4 MOOSE instances with two runs saved in
    # each moose-workdir
    herd.run_para(moose_vars)

    print('Run time (parallel) = '+'{:.3f}'.format(herd.get_sweep_time())+' seconds')
    print('------------------------------------------')
    print()

if __name__ == '__main__':
    main()


