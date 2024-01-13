'''
==============================================================================
TEST: MOOSE Herd Tests

Authors: Lloyd Fletcher
==============================================================================
'''

'''
TODO: Tests
- Test 'keep_all' option
- Calling run multiple times 
    - Run once, seq, para
- Reading output after calling run multiple times.
'''

import pytest
import os
from pathlib import Path
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooserunner import MooseRunner
from mooseherder.mooseherd import MooseHerd
from tests.checkmooserun import check_solve_converged

@pytest.fixture()
def herd_blank():
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    moose_input = 'tests/moose/moose-test.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    
    return MooseHerd(moose_runner,moose_modifier)

@pytest.fixture()
def base_dir():
    return 'tests/'

@pytest.fixture()
def herd(base_dir):
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    moose_input = 'tests/moose/moose-test.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    
    herd =  MooseHerd(moose_runner,moose_modifier)
    herd.set_base_dir(base_dir)
    return herd

@pytest.fixture(autouse=True)
def setup_teardown(herd):
    # Setup here
    yield
    # Teardown here 
    herd.clear_dirs()

@pytest.fixture()
def moose_vars():
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]
    moose_vars = list()
    for ee in e_mod:
        for pp in p_rat:
            moose_vars.append({'e_modulus':ee,'p_ratio':pp})
    return moose_vars


def test_set_base_dir(herd_blank,base_dir):
    herd_blank.set_base_dir(base_dir)
    assert herd_blank._base_dir == base_dir

def test_set_base_dir_clear_old(herd_blank,base_dir):
    prev_dir = herd_blank._run_dir
    herd_blank.create_dirs()
    herd_blank.set_base_dir(base_dir, clear_old_dirs = True)
    assert herd_blank._base_dir == base_dir
    assert os.path.isdir(prev_dir+'-1') == False

def test_set_base_dir_err(herd_blank):
    base_dir = 'no_exist/'
    with pytest.raises(FileExistsError) as errinfo:
        herd_blank.set_base_dir(base_dir)
    msg, = errinfo.value.args
    assert msg == "Specified base directory does not exist."

def test_set_names(herd):
    herd.set_names('sim-dir','sim','mesh')
    assert herd._sub_dir == 'sim-dir'
    assert herd._moose_input_name == 'sim'
    assert herd._gmsh_input_name == 'mesh'

    herd.set_names()
    assert herd._sub_dir == 'moose-workdir'
    assert herd._moose_input_name == 'moose-sim'
    assert herd._gmsh_input_name == 'gmsh-mesh'

def test_set_flags(herd):
    herd.set_flags(one_dir = True, keep_all = False)
    assert herd._one_dir == True
    assert herd._keep_all == False

    herd.set_flags()
    assert herd._one_dir == False
    assert herd._keep_all == True

def test_create_dirs_one_dir(herd):
    herd.set_flags(one_dir = True)
    herd.create_dirs()
    assert os.path.isdir(herd._run_dir+'-1')

def test_create_dirs_multi_dir(herd):
    herd.set_flags(one_dir = False)
    herd.create_dirs()
    assert os.path.isdir(herd._run_dir+'-1')
    assert os.path.isdir(herd._run_dir+'-2')

def test_clear_dirs(herd):
    herd.create_dirs()
    herd.clear_dirs()
    assert os.path.isdir(herd._run_dir+'-1') == False
    assert os.path.isdir(herd._run_dir+'-2') == False

@pytest.mark.parametrize(
    ('n_moose','expected'),
    (
        (0, 1),
        (-1,1),
        (2.5,2),
        (os.cpu_count()+1,os.cpu_count())
    )
)
def test_para_opts_no_dirs(n_moose,expected,herd):
    herd.para_opts(n_moose,1,1,True,False)
    assert herd._n_moose == expected

@pytest.mark.parametrize(
    ('n_moose','expected'),
    (
        (0, 1),
        (-1,1),
        (2.5,2),
        (os.cpu_count()+1,os.cpu_count())
    )
)
def test_para_opts_create_dirs(n_moose,expected,herd):
    herd.para_opts(n_moose,1,1,True,True)
    assert herd._n_moose == expected
    assert os.path.isdir(herd._run_dir+'-'+str(expected))

def test_run_once(herd,moose_vars):
    herd.create_dirs()
    output_exodus = herd.run_once(0,moose_vars[0])
    stdout_file = os.path.split(output_exodus)[0] + '/stdout.processor.0'
    assert os.path.isfile(output_exodus), 'Output exodus does not exist, MOOSE run failed.'
    assert os.path.isfile(stdout_file), 'stdout file does not exist, MOOSE run failed or redirect flag set incorrectly.'
    assert check_solve_converged(stdout_file), 'MOOSE run did not converge, check stdout file.'

'''
TODO: Tests to Create
- Call run_para and run_seq twice in a row
'''



