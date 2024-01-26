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


@pytest.fixture()
def herd_blank() -> MooseHerd:
    (moose_runner,moose_modifier) = hct.create_moose_objs(hct.MOOSE_INPUT)
    dir_manager = DirectoryManager(hct.NUM_DIRS)
    return MooseHerd([moose_runner],[moose_modifier],dir_manager)


@pytest.fixture()
def herd() -> MooseHerd:
    (moose_runner,moose_modifier) = hct.create_moose_objs(hct.MOOSE_INPUT)
    dir_manager = DirectoryManager(hct.NUM_DIRS)
    new_herd = MooseHerd([moose_runner],[moose_modifier],dir_manager)
    dir_manager.set_base_dir(hct.BASE_DIR)
    return new_herd

@pytest.fixture()
def herd_gmsh() -> MooseHerd:
    (moose_runner,moose_modifier) = hct.create_moose_objs(hct.MOOSE_INPUT)
    (gmsh_runner,gmsh_modifier) = hct.create_gmsh_objs(hct.GMSH_INPUT)

    runners = [gmsh_runner,moose_runner]
    modifiers = [gmsh_modifier,moose_modifier]
    dir_manager = DirectoryManager(hct.NUM_DIRS)

    new_herd = MooseHerd(runners,modifiers,dir_manager)
    dir_manager.set_base_dir(hct.BASE_DIR)

    return new_herd

@pytest.fixture(autouse=True)
def setup_teardown(herd,herd_gmsh):
    # Setup here
    yield
    # Teardown here
    herd._dir_manager.clear_dirs()
    herd_gmsh._dir_manager.clear_dirs()

@pytest.fixture()
def moose_sweep():
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]

    moose_vars = list()
    for ee in e_mod:
        for pp in p_rat:
            moose_vars.append([{'e_modulus':ee,'p_ratio':pp}])

    return moose_vars


@pytest.fixture()
def gmsh_sweep():
    p0 = [1E-3,]
    p1 = [1.5E-3,2E-3]

    gmsh_vars = list()
    for ii in p0:
        for jj in p1:
            gmsh_vars.append([{'p0':ii ,'p1':jj},None])

    return gmsh_vars



def test_create_herd_blank(herd_blank: MooseHerd) -> None:
    assert herd_blank is not None

def test_create_herd(herd: MooseHerd) -> None:
    assert herd is not None

def test_create_herd_gmsh(herd_gmsh: MooseHerd) -> None:
    assert herd_gmsh is not None


def test_set_input_copy_name(herd: MooseHerd) -> None:
    new_name = 'sim-name'
    herd.set_input_copy_name(new_name)
    assert herd._input_name == new_name

    herd.set_input_copy_name()
    assert herd._input_name == 'sim'

def test_set_keep_flag(herd: MooseHerd) -> None:
    herd.set_keep_flag(True)
    assert herd._keep_all == True

    herd.set_keep_flag(False)
    assert herd._keep_all == False

    herd.set_keep_flag()
    assert herd._keep_all == True


@pytest.mark.parametrize(
    ('n_para','expected'),
    (
        (0, 1),
        (-1,1),
        (2.5,2),
        (os.cpu_count()+1,os.cpu_count()) # type: ignore
    )
)
def test_set_num_para_sims(n_para: int, expected: int, herd: MooseHerd):
    herd.set_num_para_sims(n_para)
    assert herd._n_para_sims == expected


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
def test_get_worker_num(process: str,
                        expected: str,
                        monkeypatch,
                        herd: MooseHerd) -> None:
    monkeypatch.setattr(MooseHerd,'_get_process_name',lambda _: process)
    worker_num = herd._get_worker_num()
    assert worker_num == expected


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
def test_get_run_num(sim_iter: int,
                     worker_num: str,
                     keep_all: bool,
                     expected: str,
                     herd: MooseHerd) -> None:
    herd.set_num_para_sims(hct.NUM_PARA)
    herd.set_keep_flag(keep_all)
    run_num = herd._get_run_num(sim_iter,worker_num)
    assert run_num == expected


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



