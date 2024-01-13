'''
==============================================================================
CheckMooseRun: Helper functions for checking moose run output for tests

Authors: Lloyd Fletcher
==============================================================================
'''

import os

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

