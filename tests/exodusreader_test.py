'''
==============================================================================
TEST: ExodusReader

Authors: Lloyd Fletcher
==============================================================================
'''
from pathlib import Path
import pytest
import numpy as np
from mooseherder.exodusreader import ExodusReader
import tests.herdchecker as hc


@pytest.fixture
def exodus_path() -> Path:
    return hc.OUTPUT_PATH / 'moose-mech-outtest_out.e'

@pytest.fixture
def reader(exodus_path: Path) -> ExodusReader:
    return ExodusReader(exodus_path)


def test_init_reader(reader: ExodusReader,
                     exodus_path: Path) -> None:
    assert reader._exodus_path == exodus_path
    assert reader._data is not None


def tests_init_reader_path_err() -> None:
    err_path = Path().home() / 'no-exist/no_exodus_here.wrong'
    with pytest.raises(FileNotFoundError) as err_info:
        check_reader = ExodusReader(err_path)

    (msg,) = err_info.value.args
    assert msg == 'Exodus file not found at specified path'


def test_get_names(reader: ExodusReader) -> None:
    check_names = reader.get_names('ss_names')
    ss_names = np.array(['bottom','right','top','left'])
    assert (ss_names == check_names).all()


def test_get_names_none(reader: ExodusReader) -> None:
    check_names = reader.get_names(None)
    assert check_names is None


def test_get_names_no_key(reader: ExodusReader) -> None:
    check_names = reader.get_names('no-exist')
    assert check_names is None





