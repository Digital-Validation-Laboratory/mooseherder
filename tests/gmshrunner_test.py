'''
==============================================================================
TEST: gmsh Runner

Authors: Lloyd Fletcher
==============================================================================
'''
import pytest
import os
from pathlib import Path
from mooseherder.gmshrunner import GmshRunner

def get_user_dir() -> str:
    path_parts = Path(os.getcwd()).parts
    return os.path.join(path_parts[0],path_parts[1],path_parts[2])

def test_gmsh_exists():
    gmsh_path = os.path.join(get_user_dir(),'moose-workdir/gmsh/bin/gmsh')
    assert os.path.isfile(gmsh_path) == True

@pytest.fixture()
def gmsh_path():
    return os.path.join(get_user_dir(),'moose-workdir/gmsh/bin/gmsh')

@pytest.fixture()
def runner(gmsh_path):
    return GmshRunner(gmsh_path)

@pytest.fixture()
def input_file():
    return 'tests/gmsh/gmsh-test.geo'


@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup here
    yield
    # Teardown here - remove output files
    script_dir = 'tests/gmsh/'
    all_files = os.listdir('tests/gmsh/')
    for ff in all_files:
        if '.msh' in ff:
            os.remove(os.path.join('tests/gmsh/' + ff))

def test_create_runner(runner,gmsh_path):
    assert runner._gmsh_app == gmsh_path

def test_create_runner_err():
    gmsh_path = get_user_dir() + 'wrong_dir/'
    with pytest.raises(FileNotFoundError) as err_info:
        runner = GmshRunner(gmsh_path)

    msg, = err_info.value.args
    assert msg == 'Gmsh app not found at given path.'

def test_set_gmsh_app(gmsh_path):
    runner = GmshRunner()
    runner.set_gmsh_app(gmsh_path)
    assert runner._gmsh_app == gmsh_path

def test_set_gmsh_app_err():
    gmsh_path = get_user_dir() + 'wrong_dir/'
    with pytest.raises(FileNotFoundError) as err_info:
        runner = GmshRunner()
        runner.set_gmsh_app(gmsh_path)

    msg, = err_info.value.args
    assert msg == 'Gmsh app not found at given path.'

def test_set_input_file(runner,input_file):
    runner.set_input_file(input_file)
    assert runner._input_file == input_file

def test_set_input_err_geo(runner):
    input_file = 'tests/gmsh/gmsh-test.i'
    with pytest.raises(FileNotFoundError) as err_info:
        runner.set_input_file(input_file)
    msg, = err_info.value.args
    assert msg == 'Incorrect file type. Must be *.geo.'

def test_set_input_err_exist(runner):
    input_file = 'tests/gmsh/gmsh-test-noexist.geo'
    with pytest.raises(FileNotFoundError) as err_info:
        runner.set_input_file(input_file)
    msg, = err_info.value.args
    assert msg == 'Specified gmsh geo file does not exist.'

def test_run(runner,input_file):
    runner.set_input_file(input_file)
    runner.run()
    assert os.path.isfile('tests/gmsh/mesh-test.msh'), 'Output mesh *.msh file not generated by gmsh.'

def test_run_with_input(runner,input_file):
    runner.run(input_file)
    assert os.path.isfile('tests/gmsh/mesh-test.msh'), 'Output mesh *.msh file not generated by gmsh.'

def test_run_err_no_gmsh():
    runner = GmshRunner()
    with pytest.raises(RuntimeError) as err_info:
        runner.run()
    msg, = err_info.value.args
    assert msg == "Specify the full path to the gmsh app before calling run."

def test_run_err_no_geo(runner):
    with pytest.raises(RuntimeError) as err_info:
        runner.run()
    msg, = err_info.value.args
    assert msg == "Specify input *.geo file before running gmsh."