'''
==============================================================================
EXAMPLE: Run MOOSE in sequential then parallel mode then read sweep results

Author: Lloyd Fletcher, Rory Spencer
==============================================================================
'''
import time
from pathlib import Path
from pprint import pprint
from mooseherder import MooseHerd
from mooseherder import MooseRunner
from mooseherder import MooseConfig
from mooseherder import GmshRunner
from mooseherder import InputModifier
from mooseherder import DirectoryManager
from mooseherder import SweepReader

USER_DIR = Path.home()

def main() -> None:
    """main: parallel herd run once and read
    """
    print("-"*80)
    print('EXAMPLE: Parallel Herd Setup & Run')
    print("-"*80)
    # Setup the MOOSE input modifier and runner
    moose_input = Path('scripts/moose/moose-mech-simple.i')
    moose_modifier = InputModifier(moose_input,'#','')

    moose_config = MooseConfig().read_config(Path.cwd() / 'moose-config.json')
    moose_runner = MooseRunner(moose_config)
    moose_runner.set_run_opts(n_tasks = 1,
                              n_threads = 2,
                              redirect_out = True)

    # Setup Gmsh
    gmsh_input = Path('scripts/gmsh/gmsh_tens_spline_2d.geo')
    gmsh_modifier = InputModifier(gmsh_input,'//',';')

    gmsh_path = USER_DIR / 'moose-workdir/gmsh/bin/gmsh'
    gmsh_runner = GmshRunner(gmsh_path)
    gmsh_runner.set_input_file(gmsh_input)

    # Setup herd composition
    sim_runners = [gmsh_runner,moose_runner]
    input_modifiers = [gmsh_modifier,moose_modifier]
    dir_manager = DirectoryManager(n_dirs=4)

    # Start the herd and create working directories
    herd = MooseHerd(sim_runners,input_modifiers,dir_manager)
    # Set the parallelisation options, we have 8 combinations of variables and
    # 4 MOOSE intances running, so 2 runs will be saved in each working directory
    herd.set_num_para_sims(n_para=4)

     # Send all the output to the examples directory and clear out old output
    dir_manager.set_base_dir(Path('examples/'))
    dir_manager.clear_dirs()
    dir_manager.create_dirs()

    # Create variables to sweep in a list of dictionaries, 8 combinations possible.
    p0 = [1E-3,2E-3]
    p1 = [1.5E-3,2E-3]
    p2 = [1E-3,3E-3]
    var_sweep = list([])
    for nn in p0:
        for ee in p1:
            for pp in p2:
                var_sweep.append([{'p0':nn,'p1':ee,'p2':pp},None])

    print('Herd sweep variables:')
    pprint(var_sweep)

    print()
    print('Running MOOSE in parallel.')
    herd.run_para(var_sweep)

    print(f'Run time (parallel) = {herd.get_sweep_time():.3f} seconds')
    print("-"*80)
    print()

    print("-"*80)
    print('EXAMPLE: Read Herd Output')
    print("-"*80)
    sweep_reader = SweepReader(dir_manager,num_para_read=4)
    output_files = sweep_reader.read_all_output_keys()

    print('Herd output files (from output_keys.json):')
    pprint(output_files)
    print()

    print("-"*80)
    print('Reading the first output file, no SimReadConfig = read all.')
    print('Returns the first sim chain as list of SimData objects.')
    print()
    sim_data_chain = sweep_reader.read_results_once(output_files[1])
    print(sim_data_chain[0])
    print()

    print("-"*80)
    print('Reading all output files sequentially as a list(SimData).')
    print('All function parameters blank to read everything.')
    print()
    start_time = time.perf_counter()
    sweep_results_seq = sweep_reader.read_results_sequential()
    read_time_seq = time.perf_counter() - start_time

    print(f'Number of simulations read: {len(sweep_results_seq):d}')

    print("-"*80)
    print('Reading all output files in parallel as list(SimData).')
    print('All function parameters blank to read everything.')
    print()
    start_time = time.perf_counter()
    sweep_results_para = sweep_reader.read_results_para()
    read_time_para = time.perf_counter() - start_time

    print(f'Number of simulations outputs: {len(sweep_results_para):d}')

    print()
    print("="*80)
    print(f'Read time sequential = {read_time_seq:.6f} seconds')
    print(f'Read time parallel   = {read_time_para:.6f} seconds')
    print("="*80)
    print()


if __name__ == '__main__':
    main()
