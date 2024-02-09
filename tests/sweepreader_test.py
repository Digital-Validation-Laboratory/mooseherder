'''
==============================================================================
TEST: SweepReader

Authors: Lloyd Fletcher
==============================================================================
'''
import pytest
from mooseherder.sweepreader import SweepReader
from mooseherder.directorymanager import DirectoryManager
import tests.herdchecker as hc


@pytest.fixture
def dir_manager() -> DirectoryManager:
    dir_manager.set_base_dir(hc)
    return DirectoryManager(hc.NUM_DIRS)


@pytest.fixture
def sweep_reader(dir_manager) -> SweepReader:
    return SweepReader(dir_manager,hc.NUM_PARA)


def test_init_sweep_reader(sweep_reader: SweepReader) -> None:
    assert sweep_reader is not None