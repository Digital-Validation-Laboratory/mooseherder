'''
==============================================================================
Herd Check Tools: Helper functions for testing MooseHerder

Authors: Lloyd Fletcher
==============================================================================
'''

import os
from pathlib import Path
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooserunner import MooseRunner
from mooseherder.gmshrunner import GmshRunner
from mooseherder.mooseherd import MooseHerd

USER_DIR = Path.home()

def create_moose_objs(input_file: Path) -> tuple[MooseRunner,InputModifier]:
    moose_dir = USER_DIR / 'moose'
    moose_app_dir = USER_DIR / 'moose-workdir/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = input_file

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)

    return (moose_runner,moose_modifier)


def create_gmsh_objs(input_file: Path) -> tuple[GmshRunner,InputModifier]:
    gmsh_path = USER_DIR / 'moose-workdir/gmsh/bin/gmsh'
    gmsh_input = input_file

    gmsh_modifier = InputModifier(gmsh_input,'//',';')
    gmsh_runner = GmshRunner(gmsh_path)
    gmsh_runner.set_input_file(gmsh_input)

    return (gmsh_runner,gmsh_modifier)

def check_solve(check_file: str, check_str: str) -> int:
    check_count = 0
    if os.path.isfile(check_file):
        with open(check_file,'r') as so:
            stdout_lines = so.readlines()
            for ll in stdout_lines:
                if check_str in ll:
                    check_count += 1
    return check_count


def check_solve_converged(check_stdout: str) -> int:
    return check_solve(check_stdout,'Solve Converged!')

def check_solve_error(check_stdout: str) -> int:
    return check_solve(check_stdout,'*** ERROR ***')

def check_output_key_file_count(check_dir: str) -> int:
    work_dir_files = os.listdir(check_dir)

    key_count = 0
    for ff in work_dir_files:
        if 'output-key' in ff:
            key_count += 1

    return key_count


def check_run_sweep(check_herd: MooseHerd, run_call: int):
    for ff in check_herd._output_files:
        assert os.path.isfile(ff), f"Simulation output {ff} does not exist."

    assert check_herd._sweep_start_time >= 0, 'Sweep start time is less than 0.'
    assert check_herd._sweep_run_time >= 0, 'Sweep run time is less than 0.'
    assert os.path.isfile(check_herd.get_output_key_file()), 'Output key file was not written.'
    assert check_output_key_file_count(check_herd._run_dir + '-1/') == run_call


def check_input_output_count_sequential(check_herd: MooseHerd, run_call: int):
    (input_count, output_count) = get_input_output_count(check_herd._run_dirs)

    if not check_herd._keep_all:
        num_sims = 1
    else:
        num_sims = get_num_sims(check_herd._moose_var_list, check_herd._gmsh_var_list, run_call)

    assert input_count == num_sims
    assert output_count == num_sims


def check_input_output_count_para(check_herd: MooseHerd, run_call: int):
    (input_count, output_count) = get_input_output_count(check_herd._run_dirs)

    num_sims = get_num_sims(check_herd._moose_var_list, check_herd._gmsh_var_list, run_call)

    assert input_count == num_sims
    assert output_count == num_sims


def get_input_output_count(run_dirs: list[str]) -> tuple[int,int]:
    # Go through all work directories and count the inputs/exoduses
    input_count = 0
    output_count = 0

    for rr in run_dirs:
        dir_files = os.listdir(rr)
        for ff in dir_files:
            if '_out.e' in ff:
                output_count += 1
            elif '.i' in ff:
                input_count += 1

    return (input_count, output_count)


def get_num_sims(moose_var_list: list[dict], gmsh_var_list: list[dict], run_call: int) -> int:
    num_gmsh_vars = 1
    if gmsh_var_list != None:
        num_gmsh_vars = len(gmsh_var_list)

    return run_call*len(moose_var_list)*num_gmsh_vars


def run_check_sequential(keep_all,expected,run_herd,moose_vars,gmsh_vars):
    run_herd.set_flags(one_dir = False, keep_all = keep_all)
    run_herd.para_opts(n_moose = 2)

    run_herd.run_sequential(moose_vars,gmsh_vars)
    check_run_sweep(check_herd = run_herd, run_call = 1)
    check_input_output_count_sequential(check_herd = run_herd, run_call = 1)

    run_herd.run_sequential(moose_vars,gmsh_vars)
    check_run_sweep(check_herd = run_herd, run_call = expected)
    check_input_output_count_sequential(check_herd = run_herd, run_call = expected)


def run_check_para(keep_all,expected,run_herd,moose_vars,gmsh_vars):
    run_herd.para_opts(n_moose = 4)
    run_herd.set_flags(one_dir = False, keep_all = keep_all)

    run_herd.run_para(moose_vars,gmsh_vars)
    check_run_sweep(check_herd = run_herd, run_call = 1)
    check_input_output_count_para(check_herd = run_herd, run_call = 1)

    run_herd.run_para(moose_vars,gmsh_vars)
    check_run_sweep(check_herd = run_herd, run_call = expected)
    check_input_output_count_para(check_herd = run_herd, run_call = expected)
