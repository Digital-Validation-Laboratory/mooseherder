'''
==============================================================================
TEST: MOOSE Herd Tests

Authors: Lloyd Fletcher
==============================================================================
'''

'''
TODO: Test create dirs
- Include new run_dirs list
'''

import pytest
from pytest import MonkeyPatch
import os
from pathlib import Path
import multiprocessing as mp
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooserunner import MooseRunner
from mooseherder.mooseherd import MooseHerd
import tests.herdchecktools as hct

@pytest.fixture()
def base_dir():
    return 'tests/'

@pytest.fixture()
def moose_input():
    return 'tests/moose/moose-test.i'

@pytest.fixture()
def gmsh_input():
    return 'tests/gmsh/gmsh-test.geo'

@pytest.fixture()
def herd_blank(moose_input):
    (moose_runner,moose_modifier) = hct.create_moose_objs(moose_input)
    return MooseHerd(moose_runner,moose_modifier)

@pytest.fixture()
def herd(base_dir,moose_input):
    (moose_runner,moose_modifier) = hct.create_moose_objs(moose_input)
    herd = MooseHerd(moose_runner,moose_modifier)
    herd.set_base_dir(base_dir)
    return herd

@pytest.fixture()
def herd_gmsh(base_dir,gmsh_input):
    moose_input = 'tests/moose/moose-test-gmsh.i'
    (moose_runner,moose_modifier) = hct.create_moose_objs(moose_input)
    (gmsh_runner,gmsh_modifier) = hct.create_gmsh_objs(gmsh_input)
    herd = MooseHerd(moose_runner,moose_modifier,gmsh_runner,gmsh_modifier)
    herd.set_base_dir(base_dir)
    return herd

@pytest.fixture(autouse=True)
def setup_teardown(herd,herd_gmsh):
    # Setup here
    yield
    # Teardown here 
    herd.clear_dirs()
    herd_gmsh.clear_dirs()

@pytest.fixture()
def moose_vars():
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]

    moose_vars = list()
    for ee in e_mod:
        for pp in p_rat:
            moose_vars.append({'e_modulus':ee,'p_ratio':pp})

    return moose_vars

@pytest.fixture()
def gmsh_vars():
    p0 = [1E-3,]
    p1 = [1.5E-3,2E-3]

    gmsh_vars = list()
    for ii in p0:
        for jj in p1:
            gmsh_vars.append({'p0':ii ,'p1':jj})
    
    return gmsh_vars

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


@pytest.mark.parametrize(
    ('process','expected'),
    (
        ('MainProcess', '1'),
        ('process-1','1'),
        ('process-2','2'),
        ('process-3','2'),
        ('process-4','1'),
    )   
)
def test_get_worker_num(process,expected,monkeypatch,herd) -> None:
    monkeypatch.setattr(MooseHerd,'_get_process_name',lambda _: process)
    worker_num = herd._get_worker_num()
    assert worker_num == expected

@pytest.mark.parametrize(
    ('worker_num','one_dir','expected'),
    (
        ('4',False, '-4/'),
        ('1',True, '-1/'),
        ('2',True, '-1/'),
        ('4',True, '-1/'),
    )   
)
def test_get_run_dir(worker_num,one_dir,expected,herd):
    herd.para_opts(n_moose = 2)
    herd.set_flags(one_dir = one_dir)
    run_dir = herd._get_run_dir(worker_num)
    assert run_dir == herd._run_dir+expected


@pytest.mark.parametrize(
    ('sim_iter','worker_num','keep_all','expected'),
    (
        (0,'1',False, '1'),
        (4,'2',False, '2'),
        (10,'3',False, '3'),
        (0,'1',True, '1'),
        (1,'2',True, '2'),
        (3,'5',True, '4'),
    )   
)
def test_get_run_num(sim_iter,worker_num,keep_all,expected,herd):
    herd.para_opts(n_moose = 2)
    herd.set_flags(one_dir = False, keep_all = keep_all)
    run_num = herd._get_run_num(sim_iter,worker_num)
    assert run_num == expected

def test_run_gmsh(herd_gmsh,gmsh_vars):
    herd = herd_gmsh
    herd.para_opts(n_moose = 2)
    
    worker_num = '1'
    sim_iter = 0

    run_dir = herd._get_run_dir(worker_num)
    run_num = herd._get_run_num(sim_iter,worker_num)

    gmsh_save = herd._run_gmsh(gmsh_vars[0],run_dir,run_num)

    assert gmsh_vars[0]['p0'] == herd._gmsh_modifier._vars['p0']
    assert gmsh_vars[0]['p1'] == herd._gmsh_modifier._vars['p1']
    assert os.path.isfile(gmsh_save)
    assert os.path.isfile(os.path.split(gmsh_save)[0]+'/gmsh-test.msh')

def test_run_moose(herd,moose_vars):
    herd.para_opts(n_moose = 2)
    
    worker_num = '1'
    sim_iter = 0

    run_dir = herd._get_run_dir(worker_num)
    run_num = herd._get_run_num(sim_iter,worker_num)

    moose_save = herd._run_moose(moose_vars[0],run_dir,run_num)

    assert moose_vars[0]['e_modulus'] == herd._moose_modifier._vars['e_modulus']
    assert moose_vars[0]['p_ratio'] == herd._moose_modifier._vars['p_ratio']
    assert os.path.isfile(moose_save)
    assert os.path.isfile(os.path.split(moose_save)[0]+'/moose-sim-1_out.e')

@pytest.mark.parametrize(
    ('sim_iter','worker_num'),
    (
        (0,'1'),
        (8,'4'),
    )   
)
def test_run_once_moose_only(sim_iter,worker_num,herd,moose_vars,monkeypatch):
    # Force the process number to be not the main process
    monkeypatch.setattr(MooseHerd, '_get_worker_num', lambda _: worker_num)

    herd.para_opts(n_moose = 4)

    output_exodus = herd.run_once(sim_iter,moose_vars[0])

    worker_path = os.path.split(output_exodus)[0]
    stdout_file =  worker_path + '/stdout.processor.0'

    assert os.path.isfile(output_exodus), 'Output exodus does not exist, MOOSE run failed.'
    assert os.path.isfile(stdout_file), 'stdout file does not exist, MOOSE run failed or redirect flag set incorrectly.'
    assert hct.check_solve_converged(stdout_file), 'MOOSE run did not converge, check stdout file.'
    assert herd._iter_start_time >= 0, 'Iteration start time is less than 0'
    assert herd._iter_run_time >= 0, 'Iteration run time is less than 0'

@pytest.mark.parametrize(
    ('sim_iter','worker_num'),
    (
        (0,'1'),
        (8,'4'),
    )   
)
def test_run_once_with_gmsh(sim_iter, worker_num, herd_gmsh, gmsh_vars, monkeypatch):
    # Force the process number to be not the main process
    monkeypatch.setattr(MooseHerd, '_get_worker_num', lambda _: worker_num)
    moose_vars = herd_gmsh._moose_modifier.get_vars()

    herd_gmsh.para_opts(n_moose = 4)

    output_exodus = herd_gmsh.run_once(sim_iter,moose_vars,gmsh_vars[0])

    worker_path = os.path.split(output_exodus)[0]
    stdout_file =  worker_path + '/stdout.processor.0'

    assert os.path.isfile(worker_path+'/gmsh-test.msh'), 'Gmsh mesh was not created.'
    assert os.path.isfile(output_exodus), 'Output exodus does not exist, MOOSE run failed.'
    assert os.path.isfile(stdout_file), 'stdout file does not exist, MOOSE run failed or redirect flag set incorrectly.'
    assert hct.check_solve_converged(stdout_file), 'MOOSE run did not converge, check stdout file.'
    assert herd_gmsh._iter_start_time >= 0, 'Iteration start time is less than 0'
    assert herd_gmsh._iter_run_time >= 0, 'Iteration run time is less than 0'

@pytest.mark.parametrize(
    ('keep_all', 'expected'),
    (
        (True, 2),
        (False, 1),
    )   
)
def test_run_sequential_moose_only(keep_all,expected,herd,moose_vars):
    gmsh_vars = None
    run_sequential(keep_all,expected,herd,moose_vars,gmsh_vars)

@pytest.mark.parametrize(
    ('keep_all', 'expected'),
    (
        (True, 2),
        (False, 1),
    )   
)
def test_run_sequential_with_gmsh(keep_all,expected,herd_gmsh,gmsh_vars):
    moose_vars = [herd_gmsh._moose_modifier.get_vars()]
    run_sequential(keep_all,expected,herd_gmsh,moose_vars,gmsh_vars)

def run_sequential(keep_all,expected,run_herd,moose_vars,gmsh_vars):
    run_herd.set_flags(one_dir = False, keep_all = keep_all)
    run_herd.para_opts(n_moose = 2)

    run_herd.run_sequential(moose_vars,gmsh_vars)
    check_run_sweep(check_herd = run_herd, run_call = 1)
    
    run_herd.run_sequential(moose_vars,gmsh_vars)
    check_run_sweep(check_herd = run_herd, run_call = expected)

@pytest.mark.parametrize(
    ('keep_all', 'expected'),
    (
        (True, 2),
        (False, 1),
    )   
)
def test_run_para_moose_only(keep_all,expected,herd,moose_vars):
    gmsh_vars = None
    run_para(keep_all,expected,herd,moose_vars,gmsh_vars)

@pytest.mark.parametrize(
    ('keep_all', 'expected'),
    (
        (True, 2),
        (False, 1),
    )   
)
def test_run_para_with_gmsh(keep_all,expected,herd_gmsh,gmsh_vars):
    moose_vars = [herd_gmsh._moose_modifier.get_vars()]
    run_para(keep_all,expected,herd_gmsh,moose_vars,gmsh_vars)

def run_para(keep_all,expected,run_herd,moose_vars,gmsh_vars):
    run_herd.para_opts(n_moose = 4)
    run_herd.set_flags(one_dir = False, keep_all = keep_all)

    run_herd.run_para(moose_vars,gmsh_vars)
    check_run_sweep(check_herd = run_herd, run_call = 1)
 
    run_herd.run_para(moose_vars,gmsh_vars)
    check_run_sweep(check_herd = run_herd, run_call = expected)

def check_run_sweep(check_herd: MooseHerd, run_call: int):
    for ff in check_herd._output_files:
        assert os.path.isfile(ff), f"Simulation output {ff} does not exist."

    # Go through all work directories and count the inputs/exoduses
    input_count = 0
    output_count = 0
    for rr in check_herd._run_dirs:
        dir_files = os.listdir(rr)
        for ff in dir_files:
            if '_out.e' in ff: 
                output_count += 1
            elif '.i' in ff:
                input_count += 1

    num_gmsh_vars = 1
    if check_herd._gmsh_var_list != None:
        num_gmsh_vars = len(check_herd._gmsh_var_list)

    num_sims = run_call*len(check_herd._moose_var_list)*num_gmsh_vars

    assert input_count == num_sims
    assert output_count == num_sims
    assert check_herd._sweep_start_time >= 0, 'Sweep start time is less than 0.'
    assert check_herd._sweep_run_time >= 0, 'Sweep run time is less than 0.'
    assert os.path.isfile(check_herd.get_output_key_file()), 'Output key file was not written.'
    assert hct.check_output_key_file_count(check_herd._run_dir + '-1/') == run_call

    