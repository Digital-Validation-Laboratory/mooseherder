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

@pytest.fixture()
def herd_blank():
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    moose_input = 'scripts/moose/moose-mech-simple.i'

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
    moose_input = 'scripts/moose/moose-mech-simple.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    
    herd =  MooseHerd(moose_runner,moose_modifier)
    herd.set_base_dir(base_dir)
    return herd

@pytest.fixture(autouse=True)
def setup_teardown(herd):
    # Setup here
    yield
    # Teardown here - remove output exodus files
    # herd.clear_dirs()

  
def test_set_base_dir(herd_blank,base_dir):
    herd_blank.set_base_dir(base_dir)
    assert herd_blank._base_dir == base_dir

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
def test_para_opts(n_moose,expected,herd):
    pass


