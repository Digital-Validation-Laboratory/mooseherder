'''
==============================================================================
TEST: ExodusReader

Authors: Lloyd Fletcher
==============================================================================
'''
from pathlib import Path
import pytest
from mooseherder.exodusreader import ExodusReader
import tests.herdchecker as hc


@pytest.fixture
def output_exodus() -> Path:
    return Path('tests/output/sim-workdir-1/sim-1_out.e')


@pytest.fixture
def reader(output_exodus) -> ExodusReader:
    return ExodusReader(output_exodus)


def test_init_reader(reader) -> None:
    assert reader is not None
    assert reader._data is not None


