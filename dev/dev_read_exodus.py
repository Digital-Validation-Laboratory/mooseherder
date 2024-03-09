"""
==============================================================================
EXMAPLE: Run MOOSE once with mooseherder and read the exodus output

Author: Lloyd Fletcher
==============================================================================
"""
import time
from pprint import pprint
from pathlib import Path
import numpy as np
from typing import Any
from mooseherder import MooseRunner
from mooseherder import MooseConfig
from mooseherder import ExodusReader

USER_DIR = Path.home()


def print_attrs(in_obj: Any) -> None:
    _ = [print(aa) for aa in dir(in_obj) if '__' not in aa]


def main() -> None:
    """main: run moose once and read the exodus output
    """
    print('='*80)
    print('EXAMPLE: Run MOOSE once, read exodus.')
    print('='*80)
    print('Generating exodus output to read by running MOOSE once.')

    # Create the moose runner with correct paths to moose and apps
    moose_config = MooseConfig().read_config(Path.cwd() / 'moose-config.json')
    moose_runner = MooseRunner(moose_config)

    # Set input and parallelisation options
    moose_runner.set_run_opts(n_tasks = 1, n_threads = 4,redirect_out = True)
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

    all_sim_data = exodus_reader.read_all_sim_data()
    print()
    print('Attributes of SimData:')
    print_attrs(all_sim_data)
    print()

    read_config = exodus_reader.get_read_config()
    print('Attributes of SimReadConfig:')
    print_attrs(read_config)
    print()

    sim_data = exodus_reader.read_sim_data(read_config)
    print()


if __name__ == '__main__':
    main()
