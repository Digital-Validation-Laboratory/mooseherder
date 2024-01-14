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

def create_moose_objs(input_file: str) -> (InputModifier,MooseRunner):
    user_dir = get_user_dir()
    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    moose_input = input_file

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)

    return (moose_runner,moose_modifier)

def create_gmsh_objs(input_file: str) -> (InputModifier,GmshRunner):
    user_dir = get_user_dir()
    gmsh_path = os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
    gmsh_input = input_file

    gmsh_modifier = InputModifier(gmsh_input,'//',';')
    gmsh_runner = GmshRunner(gmsh_path)
    gmsh_runner.set_input_file(gmsh_input)

    return (gmsh_runner,gmsh_modifier)

def get_user_dir() -> str:
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])
    return user_dir

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
