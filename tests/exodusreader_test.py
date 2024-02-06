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

NUM_TIME_STEPS = 4
NUM_NODES = 441
NUM_ELEMS_PER_BLOCK = 200
NUM_BLOCKS = 2
NUM_SIDESETS = 4
NUM_NODE_VARS = 10
NUM_ELEM_VARS = 8
NODES_PER_ELEM = 4


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


def test_get_var(reader: ExodusReader) -> None:
    key = 'coordx'
    check_var = reader.get_var(key)
    assert check_var.shape[0] > 0
    assert check_var.shape == (NUM_NODES,)


def test_get_var_no_key(reader: ExodusReader) -> None:
    no_key = 'no_exist'
    check_var = reader.get_var(no_key)
    assert check_var.shape[0] == 0


def test_get_connectivity_names(reader: ExodusReader) -> None:
    check_names = reader.get_connectivity_names()
    assert check_names.shape == (NUM_BLOCKS,)
    assert (check_names == np.array(['connect1','connect2'])).all()


def test_get_connectivity(reader: ExodusReader) -> None:
    check_connect = reader.get_connectivity()
    assert check_connect is not None
    assert list(check_connect.keys()) == ['connect1','connect2']
    assert check_connect['connect1'].shape == (
        NODES_PER_ELEM,NUM_ELEMS_PER_BLOCK)
    assert check_connect['connect2'].shape == (
        NODES_PER_ELEM,NUM_ELEMS_PER_BLOCK)


def test_get_sideset_names(reader: ExodusReader) -> None:
    check_names = reader.get_sideset_names()
    assert check_names is not None
    assert check_names.shape == (NUM_SIDESETS,)


def test_get_sidesets_none(reader: ExodusReader) -> None:
    check_sidesets  = reader.get_sidesets(None)
    assert check_sidesets is None


def test_get_all_sidesets(reader: ExodusReader) -> None:
    check_sidesets = reader.get_all_sidesets()
    assert check_sidesets is not None
    assert len(check_sidesets.keys()) == 2*NUM_SIDESETS # NOTE: node+elem = *2
    assert check_sidesets[('bottom','node')].shape[0] > 0
    assert check_sidesets[('bottom','elem')].shape[0] > 0


def test_get_node_var_names(reader: ExodusReader) -> None:
    node_var_names = reader.get_node_var_names()
    assert node_var_names is not None
    assert node_var_names.shape == (NUM_NODE_VARS,)


def test_get_node_vars_none(reader: ExodusReader) -> None:
    node_vars = reader.get_node_vars(None)
    assert node_vars is None


def test_get_all_node_vars(reader: ExodusReader) -> None:
    node_vars = reader.get_all_node_vars()
    assert node_vars is not None
    assert len(node_vars.keys()) == NUM_NODE_VARS
    for nn in node_vars:
        assert node_vars[nn].shape == (NUM_NODES,NUM_TIME_STEPS)


def test_get_elem_var_names(reader: ExodusReader) -> None:
    pass


def test_get_num_elem_blocks(reader: ExodusReader) -> None:
    pass


def test_get_elem_var_names_and_blocks(reader: ExodusReader) -> None:
    pass


