'''
==============================================================================
CheckMooseRun: Helper functions for checking moose run output for tests

Authors: Lloyd Fletcher
==============================================================================
'''


import os

def check_solve_converged(check_stdout: str) -> bool:
    solve_converged = False
    if os.path.isfile(check_stdout):
        with open(check_stdout,'r') as so:
            stdout_lines = so.readlines()
            for ll in stdout_lines:
                if 'Solve Converged!' in ll:
                    solve_converged = True
    return solve_converged

def check_exodus_exists():
    pass