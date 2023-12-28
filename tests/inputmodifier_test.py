'''
==============================================================================
TEST: Input Modifier

Authors: Lloyd Fletcher
==============================================================================
'''

import pytest
from mooseherder.inputmodifier import InputModifier

@pytest.fixture
def moose_mod():
    input_file = 'scripts/moose/moose-mech-simple.i'
    return InputModifier(input_file,'#','')

@pytest.fixture
def gmsh_mod():
    input_file = 'scripts/gmsh/gmsh_tens_spline_2d.geo'
    return InputModifier(input_file,'//',';')

def test_moose_read_vars(moose_mod):
    assert moose_mod._vars == {'n_elem_y': 50.0, 'e_modulus': 1e9, 'p_ratio': 0.3}

def test_moose_get_vars(moose_mod):
    assert moose_mod.get_vars() == {'n_elem_y': 50.0, 'e_modulus': 1e9, 'p_ratio': 0.3}

def test_read_moose_str_vars():
    input_file = 'scripts/moose/moose-mech-vartest.i'
    input_mod = InputModifier(input_file,'#','')
    assert input_mod.get_vars() == {'n_elem_y': 120.0, 'e_modulus': 3300000000.0, 'p_ratio': 0.33, 'order': 'SECOND', 'func': '$fparse{2*x}'} 

def test_moose_find_vars(moose_mod):
    assert moose_mod._var_start_ind == 3
    assert moose_mod._var_end_ind == 9

def test_gmsh_read_vars(gmsh_mod):
    assert gmsh_mod.get_vars() == {'p0': 0.0015, 'p1': 0.001, 'p2': 0.0012}


@pytest.mark.parametrize(
        ('input_str','expected'),
        (
            pytest.param('',('','',''),id='Degenerate blank case'),
            pytest.param('x1 = 1',('x1',1.0,''),id='Variable only, int case'),
            pytest.param('x2 = 100.0',('x2',100.0,''),id='Variable only, float case'),
            pytest.param('x3 = 1e3',('x3',1000.0,''),id='Variable only, exponential case'),
            pytest.param('order = SECOND',('order','SECOND',''),id='Variable only, string case'),
            pytest.param('x=10 # comment',('x',10.0,' comment'),id='Numeric variable and comment case'),
            pytest.param('fun = $fparse{2*x} # comment',('fun','$fparse{2*x}',' comment'),id='String variable and comment case'),
            pytest.param('# comment',('','',' comment'),id='Comment only case'),
        )
)
def test_extract_var_str_moose(input_str,expected):
    input_file = 'scripts/moose/moose-mech-simple.i'
    input_mod = InputModifier(input_file,'#','')
    ext_strs = input_mod._extract_var_str(input_str)
    assert ext_strs == expected

