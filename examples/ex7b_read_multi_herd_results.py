'''
==============================================================================
EXAMPLE 7b: Run MOOSE in sequential then parallel mode then read sweep results

Author: Lloyd Fletcher, Rory Spencer
==============================================================================
'''
import time
from pathlib import Path
from pprint import pprint
from mooseherder import MooseHerd
from mooseherder import MooseRunner
from mooseherder import InputModifier
from mooseherder import DirectoryManager
from mooseherder import SweepReader

NUM_PARA_RUNS = 3
USER_DIR = Path.home()

def main() -> None:
    """main: parallel herd run once and read
    """
    print('-----------------------------------------------------------')
    print('EXAMPLE 7b: Parallel Herd Setup & Run')
    print('-----------------------------------------------------------')
    moose_dir = USER_DIR / 'moose'
    moose_app_dir = USER_DIR / 'moose-workdir/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = Path('scripts/moose/moose-mech-simple.i')

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_runner.set_opts(n_tasks = 1,
                          n_threads = 2,
                          redirect_out = True)

    dir_manager = DirectoryManager(n_dirs=4)

    # Start the herd and create working directories
    herd = MooseHerd([moose_runner],[moose_modifier],dir_manager)

    # Set the parallelisation options, we have 8 combinations of variables and
    # 4 MOOSE intances running, so 2 runs will be saved in each working directory
    herd.set_num_para_sims(n_para=4)

     # Send all the output to the examples directory and clear out old output
    dir_manager.set_base_dir(Path('examples/'))
    dir_manager.clear_dirs()
    dir_manager.create_dirs()

    # Create variables to sweep in a list of dictionaries, 8 combinations possible.
    n_elem_y = [10,20]
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]
    moose_vars = list([])
    for nn in n_elem_y:
        for ee in e_mod:
            for pp in p_rat:
                # Needs to be list[list[dict]] - outer list is simulation iteration,
                # inner list is what is passed to each runner/inputmodifier
                moose_vars.append([{'n_elem_y':nn,'e_modulus':ee,'p_ratio':pp}])

    print('Herd sweep variables:')
    pprint(moose_vars)

    # Run all variable combinations across 4 MOOSE instances with two runs saved in
    # each moose-workdir
    for rr in range(NUM_PARA_RUNS):
        herd.run_para(moose_vars)

        print(f'Run time (para {rr+1}) = {herd.get_sweep_time():.3f} seconds')
        print('------------------------------------------')


    print('-----------------------------------------------------------')
    print('EXAMPLE 7b: Read Herd Output')
    print('-----------------------------------------------------------')
    sweep_reader = SweepReader(dir_manager)
    output_files = sweep_reader.read_all_output_keys()

    print('Herd output files (from output_keys.json):')
    pprint(output_files)
    print()

    vars_to_read = ['disp_x','disp_y','disp_z','strain_xx']
    elem_blocks = [0,0,0,1]

    print('Variable keys to read as list:')
    pprint(vars_to_read)
    print()

    print('Element blocks associated with variable keys as list:')
    pprint(elem_blocks)
    print()

    print('-----------------------------------------------------------')
    print('Reading the first output file, no element blocks specified.')
    print('Variables returned as dict.')
    read_vars = sweep_reader.read_results_once(output_files[0][0],
                                               vars_to_read)
    print()

    print('Variables read from file, time and coords are always read:')
    pprint(list(read_vars.keys()))
    print()

    print('Variable = Time (t): ', end='')
    print(type(read_vars['time']))
    print(read_vars['time'].shape)
    print()

    print('Variable = Coords, num nodes by (x,y,z): ', end='')
    print(type(read_vars['coords']))
    print(read_vars['coords'].shape)
    print()

    print('Variable = disp_x, num nodes by t: ', end='')
    print(type(read_vars['disp_x']))
    print(read_vars['disp_x'].shape)
    print()

    print('Variable = disp_z: ', end='')
    print(type(read_vars['disp_z']))
    print('NOTE: disp_z does not exist in the simulation so returns None')
    print()

    print('Variable = strain_xx: ', end='')
    print(type(read_vars['strain_xx']))
    print('NOTE: no elem block provided so strain_xx = None.')
    print()

    print('-----------------------------------------------------------')
    print('Reading the first output file, element blocks specified.')
    read_vars = sweep_reader.read_results_once(output_files[0][0],
                                       vars_to_read,
                                       elem_blocks)

    print('Variable = strain_xx, : ', end='')
    print(type(read_vars['strain_xx']))
    print(read_vars['strain_xx'].shape)
    print()

    print('-----------------------------------------------------------')
    print('Reading all output files sequentially as a list(dict).')
    print()
    start_time = time.perf_counter()
    read_all = sweep_reader.read_results_sequential(vars_to_read,
                                                    None,
                                                    elem_blocks)
    read_time_seq = time.perf_counter() - start_time

    print(f'Number of simulations outputs: {len(read_all):d}')
    print('Variable keys for simulation output:')
    print(list(read_all[0].keys()))
    print()

    print('-----------------------------------------------------------')
    print('Reading all output files in parallel as list(dict).')
    print()
    start_time = time.perf_counter()
    read_all = sweep_reader.read_results_para(vars_to_read,
                                              None,
                                              elem_blocks)
    read_time_para = time.perf_counter() - start_time

    print(f'Number of simulations outputs: {len(read_all):d}')
    print('Variable keys for simulation output:')
    print(list(read_all[0].keys()))
    print()
    print('-----------------------------------------------------------')
    print(f'Read time sequential = {read_time_seq} seconds')
    print(f'Read time parallel   = {read_time_para} seconds')
    print('-----------------------------------------------------------')
    print()



if __name__ == '__main__':
    main()
