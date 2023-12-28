'''
==============================================================================
TEST: MOOSE Runner

Authors: Lloyd Fletcher
==============================================================================
'''

import pytest
import os
from pathlib import Path
from mooseherder.mooserunner import MooseRunner

@pytest.fixture
def runner():
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])
    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    return MooseRunner(moose_dir,moose_app_dir,moose_app_name)

@pytest.mark.parametrize(
    ('n_threads','expected'),
    (
        (0, 1),
        (-1,1),
        
    )
)
def test_set_threads(runner,):
    runner
