import time
from pathlib import Path
from mooseherder import MooseConfig
from mooseherder import MooseRunner

USER_DIR = Path.home()

def main() -> None:
    """main: run moose once with runner class
    """
    print('------------------------------------------')
    print('EXAMPLE 2a: Run MOOSE once')
    print('------------------------------------------')
    # Create the moose runner with correct paths to moose and apps
    config_path = Path.cwd() / 'moose-config.json'
    moose_config = MooseConfig().read_config(config_path)
    print(f'Reading MOOSE config from: \n{str(config_path)}\n')

    print('Creating the MooseRunner with the specified config.\n')
    moose_runner = MooseRunner(moose_config)

    # Set input and parallelisation options
    moose_runner.set_run_opts(n_tasks = 1,
                              n_threads = 4,
                              redirect_out = False)
    input_file = Path('tests/output/moose-mech-outtest.i')
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

