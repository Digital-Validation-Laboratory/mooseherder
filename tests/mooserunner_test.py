'''
==============================================================================
TEST: MOOSE Runner

Authors: Lloyd Fletcher
==============================================================================
'''

import pytest
import os
from pathlib import Path
from mooseherder.mooserunner import MooseRunner
import tests.herdchecktools as hct

def test_moose_dir_exists():
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])
    
    moose_dir = os.path.join(user_dir,'moose')
    assert os.path.isdir(moose_dir) == True

    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    assert os.path.isdir(moose_app_dir) == True

@pytest.fixture()
def runner():
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])
    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    return MooseRunner(moose_dir,moose_app_dir,moose_app_name)

@pytest.fixture()
def input_file():
    return 'tests/moose/moose-test.i'

@pytest.fixture()
def input_noexist():
    return 'tests/moose/moose-test-noexist.i'

@pytest.fixture()
def input_broken():
    return 'tests/moose/moose-test-broken.i'

@pytest.fixture()
def input_runner(input_file):
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])
    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    runner.set_input_path(input_file)
    return runner

@pytest.fixture(autouse=True)
def setup_teardown(input_runner):
    # Setup here
    yield
    # Teardown here - remove output exodus files
    moose_files = os.listdir(input_runner.get_input_dir())
    for ff in moose_files:
        if '.e' in ff:
            os.remove(os.path.join(input_runner.get_input_dir() + ff))

    stdout_files = os.listdir(input_runner.get_input_dir())
    for ff in stdout_files:
        if 'stdout.processor' in ff:
            os.remove(input_runner.get_input_dir() + '/' + ff)
            
def test_set_env_vars(runner):
    runner.set_env_vars()
    assert os.environ['CC'] == 'mpicc'
    assert os.environ['CXX'] == 'mpicxx'
    assert os.environ['F90'] == 'mpif90'
    assert os.environ['F77'] == 'mpif77'
    assert os.environ['FC'] == 'mpif90'
    assert os.environ['MOOSE_DIR'] == runner._moose_dir

@pytest.mark.parametrize(
    ('n_threads','expected'),
    (
        (0, 1),
        (-1,1),
        (2.5,2),
        (os.cpu_count()+1,os.cpu_count())
    )
)
def test_set_threads(n_threads,expected,runner):
    runner.set_threads(n_threads)
    assert runner._n_threads == expected

@pytest.mark.parametrize(
    ('n_tasks','expected'),
    (
        (0, 1),
        (-1,1),
        (2.5,2),
        (os.cpu_count()+1,os.cpu_count())
    )
)
def test_set_tasks(n_tasks,expected,runner):
    runner.set_tasks(n_tasks)
    assert runner._n_tasks == expected

@pytest.mark.parametrize(
    ('in_flag','expected'),
    (
        (0, 0),
        (1,1),
        (True,True),
        (False,False)
    )
)
def test_set_stdout(in_flag,expected,runner):
    runner.set_stdout(in_flag)
    assert runner._redirect_stdout == expected

def test_set_input_file(runner,input_file):
    runner.set_input_file(input_file)

    assert runner._input_file == os.path.split(input_file)[1]
    assert runner._input_dir == 'tests/moose/'
    assert runner._input_tag == 'moose-test'

def test_set_input_file_err(runner):
    with pytest.raises(FileNotFoundError) as err_info:
        new_input = 'tests/moose/moose-test-noexist.i'
        runner.set_input_file(new_input)

    msg, = err_info.value.args
    assert msg == 'Input file does not exist.'

def test_get_input_strs(runner,input_runner):
    assert runner.get_input_dir() == ''
    assert runner.get_input_tag() == ''
    assert input_runner.get_input_dir() == 'tests/moose/'
    assert input_runner.get_input_tag() == 'moose-test'

def test_get_output_exodus_file(runner,input_runner):
    assert runner.get_output_exodus_file() == ''
    assert input_runner.get_output_exodus_file() == 'moose-test_out.e'

def test_get_output_exodus_file(runner,input_runner):
    assert runner.get_output_exodus_path() == ''
    assert input_runner.get_output_exodus_path() == 'tests/moose/moose-test_out.e'
     
@pytest.mark.parametrize(
    ('opts','expected'),
    (
        ((1,1,False), 'proteus-opt --n-threads=1 -i moose-test.i'),
        ((1,2,False), 'proteus-opt --n-threads=2 -i moose-test.i'),
        ((1,2,True), 'proteus-opt --n-threads=2 -i moose-test.i --redirect-stdout'),
        ((2,2,False), 'mpirun -np 2 proteus-opt --n-threads=2 -i moose-test.i'),
        ((2,2,True), 'mpirun -np 2 proteus-opt --n-threads=2 -i moose-test.i --redirect-stdout'),
    )
)
def test_assemble_run_str(opts, expected, input_runner):
    input_runner.set_opts(opts[0],opts[1],opts[2])
    assert input_runner.assemble_run_str() == expected

@pytest.mark.parametrize(
    ('opts','expected'),
    (
        ((1,1,False), 'proteus-opt --n-threads=1 -i moose-test.i'),
        ((1,2,False), 'proteus-opt --n-threads=2 -i moose-test.i'),
        ((1,2,True), 'proteus-opt --n-threads=2 -i moose-test.i --redirect-stdout'),
        ((2,2,False), 'mpirun -np 2 proteus-opt --n-threads=2 -i moose-test.i'),
        ((2,2,True), 'mpirun -np 2 proteus-opt --n-threads=2 -i moose-test.i --redirect-stdout'),
    )
)
def test_assemble_run_str_with_input(opts,expected,runner,input_file):
    runner.set_opts(opts[0],opts[1],opts[2])
    assert runner.assemble_run_str(input_file) == expected

def test_assemble_run_str_err(runner):
    with pytest.raises(RuntimeError) as err_info:
        runner.assemble_run_str()

    msg, = err_info.value.args
    assert msg == 'No input file specified, set one using set_input_file or by passing on into this function.'

def test_assemble_run_str_err_with_input(runner,input_noexist):
    with pytest.raises(FileNotFoundError) as err_info:
        runner.assemble_run_str(input_noexist)

    msg, = err_info.value.args
    assert msg == 'Input file does not exist.'

@pytest.mark.parametrize(
    ('opts','stdout_exist'),
    (
        ((1,1,False), (False,False)),
        ((1,4,False), (False,False)),
        ((1,4,True), (True,False)),
        ((2,4,False), (False,False)),
        ((2,4,True), (True,True)),
    )
)
def test_run(opts,stdout_exist,input_runner):
    input_runner.set_opts(opts[0],opts[1],opts[2])
    input_runner.run()

    assert os.path.isfile(input_runner.get_output_exodus_path()) == True, 'No exodus output.'
    assert os.path.isfile(input_runner.get_input_dir() + 'stdout.processor.0') == stdout_exist[0], 'stdout.processor.0 does not exist.'
    assert os.path.isfile(input_runner.get_input_dir() + 'stdout.processor.1') == stdout_exist[1], 'stdout.processor.1 does not exist.'
    if opts[2]: # If there is a stdout it can be read to check for convergence
        check_path = input_runner.get_input_dir() + 'stdout.processor.0'
        assert hct.check_solve_converged(check_path) >= 1, 'Solve has not converged.' 
'''
def check_solve_converged(check_stdout: str) -> bool:
    solve_converged = False
    if os.path.isfile(check_stdout):
        with open(check_stdout,'r') as so:
            stdout_lines = so.readlines()
            for ll in stdout_lines:
                if 'Solve Converged!' in ll:
                    solve_converged = True
    return solve_converged
'''
def test_run_broken(runner,input_broken):
    runner.set_opts(1,4,True)
    runner.run(input_broken)

    stdout_file = runner.get_input_dir() + 'stdout.processor.0'

    assert os.path.isfile(runner.get_output_exodus_path()) == False
    assert os.path.isfile(stdout_file) == True

    assert hct.check_solve_error(stdout_file) >= 1, 'Error string not found in stdout'
    assert hct.check_solve_converged(stdout_file) == 0, 'Solve converged when it should have errored'

def test_run_noexist(runner,input_noexist):
    with pytest.raises(FileNotFoundError) as err_info:
        runner.run(input_noexist)

    msg, = err_info.value.args
    assert msg == 'Input file does not exist.'

    assert os.path.isfile(runner.get_output_exodus_path()) == False, 'Exodus output exists but input should not.'
    assert hct.check_solve_converged(runner.get_input_dir() + 'stdout.processor.0') == 0, 'Solve converged when input file should not exist.'

def test_run_with_input(runner,input_file):
    runner.set_opts(1,4,True)
    runner.run(input_file)

    assert os.path.isfile(runner.get_output_exodus_path()) == True, 'Exodus output does not exist when solve should have run'
    assert os.path.isfile(runner.get_input_dir() + 'stdout.processor.0') == True, 'Stdout does not exist when it should.'
    assert hct.check_solve_converged(runner.get_input_dir() + 'stdout.processor.0') >= 1, 'Solve did not converge when it should have.'