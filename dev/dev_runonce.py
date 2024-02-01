import time
from pathlib import Path
from mooseherder import MooseRunner

USER_DIR = Path.home()

def main() -> None:
    """main: run moose once with runner class
    """
    print('------------------------------------------')
    print('EXAMPLE 2a: Run MOOSE once')
    print('------------------------------------------')
    # Create the moose runner with correct paths to moose and apps
    moose_dir = USER_DIR / 'moose'
    moose_app_dir = USER_DIR / 'moose-workdir/proteus'
    moose_app_name = 'proteus-opt'
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name) # type: ignore

    # Set input and parallelisation options
    moose_runner.set_opts(n_tasks = 1, n_threads = 4,redirect_out = False)
    input_file = Path('scripts/moose/moose-mech-outtest.i')
    moose_runner.set_input_file(input_file)

    # Run the MOOSE!
    print('Running moose with:')
    print(moose_runner.get_run_str())

    start_time = time.perf_counter()
    moose_runner.run()
    run_time = time.perf_counter() - start_time

    print()
    print(f'MOOSE run time = {run_time:.3f} seconds')
    print('------------------------------------------')
    print()

if __name__ == '__main__':
    main()

