'''
==============================================================================
TEST: MOOSE Herd Tests

Authors: Lloyd Fletcher
==============================================================================
'''
import os
from pathlib import Path
import multiprocessing as mp
import pytest
from pytest import MonkeyPatch
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooserunner import MooseRunner
from mooseherder.mooseherd import MooseHerd
from mooseherder.directorymanager import DirectoryManager
import tests.herdchecker as hct










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
    hct.run_check_sequential(keep_all,expected,herd,moose_vars,gmsh_vars)


@pytest.mark.parametrize(
    ('keep_all', 'expected'),
    (
        (True, 2),
        (False, 1),
    )
)
def test_run_sequential_with_gmsh(keep_all,expected,herd_gmsh,gmsh_vars):
    moose_vars = [herd_gmsh._moose_modifier.get_vars()]
    hct.run_check_sequential(keep_all,expected,herd_gmsh,moose_vars,gmsh_vars)


@pytest.mark.parametrize(
    ('keep_all', 'expected'),
    (
        (True, 2),
        (False, 1),
    )
)
def test_run_para_moose_only(keep_all,expected,herd,moose_vars):
    gmsh_vars = None
    hct.run_check_para(keep_all,expected,herd,moose_vars,gmsh_vars)


@pytest.mark.parametrize(
    ('keep_all', 'expected'),
    (
        (True, 2),
        (False, 1),
    )
)
def test_run_para_with_gmsh(keep_all,expected,herd_gmsh,gmsh_vars):
    moose_vars = [herd_gmsh._moose_modifier.get_vars()]
    hct.run_check_para(keep_all,expected,herd_gmsh,moose_vars,gmsh_vars)


