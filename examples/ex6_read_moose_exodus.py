"""
==============================================================================
EXMAPLE 6: Run MOOSE once with mooseherder and read the exodus output

Author: Lloyd Fletcher
==============================================================================
"""
import time
from pprint import pprint
from pathlib import Path
import numpy as np
from mooseherder import MooseRunner
from mooseherder import ExodusReader

USER_DIR = Path.home()

def main() -> None:
    """main: run moose once and read the exodus output
    """
    print('='*80)
    print('EXAMPLE 6: Run MOOSE once, read exodus.')
    print('='*80)
    print('Generating exodus output to read by running MOOSE once.')

    # Create the moose runner with correct paths to moose and apps
    moose_dir = USER_DIR / 'moose'
    moose_app_dir = USER_DIR / 'moose-workdir/proteus'
    moose_app_name = 'proteus-opt'
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name) # type: ignore

    # Set input and parallelisation options
    moose_runner.set_opts(n_tasks = 1, n_threads = 4,redirect_out = True)
    input_file = Path('scripts/moose/moose-mech-simple.i')
    moose_runner.set_input_file(input_file)

    # Run the MOOSE!
    print('Running moose with:')
    print(moose_runner.get_run_str())

    start_time = time.perf_counter()
    moose_runner.run()
    run_time = time.perf_counter() - start_time

    print()
    print(f'MOOSE run time = {run_time:.3f} seconds')
    print('='*80)
    print()

    output_file = Path('scripts/moose/moose-mech-simple_out.e')
    print('Reading exodus file with ExodusReader:')
    print(output_file)
    print()

    exodus_reader = ExodusReader(output_file)

    print('Read all data in the exodus file returning a SimData object with everything.')
    all_sim_data = exodus_reader.read_all_sim_data()
    pprint(type(all_sim_data))
    print()
    print('Attributes of SimData:')
    [print(aa) for aa in dir(all_sim_data) if '__' not in aa]
    print()

    print('Read only specific node/element/global variables using SimReadConfig.')
    print('Use ExodusReader to get SimReadConfig with all variables then edit it.')
    read_config = exodus_reader.get_read_config()
    pprint(type(read_config))
    print()
    print('Attributes of SimReadConfig:')
    [print(aa) for aa in dir(read_config) if '__' not in aa]
    print()

    print('Set any attribute of SimReadConfig to None to not read data.')
    print('This example sets elem_vars to None and reads the exodus:')
    read_config.elem_vars = None
    sim_data = exodus_reader.read_sim_data(read_config)
    print(f'sim_data.elem_vars = {sim_data.elem_vars}')
    print()

    print('Set attributes of SimReadConfig to a list of names as np.array')
    print('This example only reads disp_x from the nodal variables:')
    read_config.node_vars = np.array(['disp_x'])
    sim_data = exodus_reader.read_sim_data(read_config)
    print('sim_data.node_vars =')
    pprint(sim_data.node_vars)
    print()

    print('Element variables are an exception as they also need a block.')
    read_config.elem_vars = [('strain_xx',1),('stress_yy',1)]
    sim_data = exodus_reader.read_sim_data(read_config)
    print("sim_data.elem_vars[('stress_xx',1)] = ")
    pprint(sim_data.elem_vars[('strain_xx',1)]) # type: ignore
    print()

    print('NOTE: depending on output settings element variables may appear as nodal.')
    print('-'*80)
    print()


if __name__ == '__main__':
    main()
