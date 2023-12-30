'''
==============================================================================
TEST: Input Modifier

Authors: Lloyd Fletcher
==============================================================================
'''

import pytest
import os
from mooseherder.inputmodifier import InputModifier

'''
-------------------------------------------------------------------------------
MOOSE Tests
TODO: create tests for case with custom variable block characters
-------------------------------------------------------------------------------
''' 
@pytest.fixture
def moose_mod():
    input_file = 'tests/moose/moose-vartest.i'
    return InputModifier(input_file,'#','')

def test_moose_find_vars(moose_mod):
    moose_mod.find_vars()
    assert moose_mod._var_start_ind == 3
    assert moose_mod._var_end_ind == 14

def test_moose_read_vars(moose_mod):
    moose_mod.read_vars()
    assert moose_mod._vars == {'n_elem_y': 20.0, 
                               'e_modulus': 1000000000.0, 
                               'p_ratio': 0.3, 
                               'e_type': 'QUAD4', 
                               'add_vars': 'true', 
                               'y_max': 1.0, 
                               'x_max': '${fparse2*y_max}'}
    
def test_moose_get_vars(moose_mod):
    assert moose_mod.get_vars()  == {'n_elem_y': 20.0, 
                                    'e_modulus': 1000000000.0, 
                                    'p_ratio': 0.3, 
                                    'e_type': 'QUAD4', 
                                    'add_vars': 'true', 
                                    'y_max': 1.0, 
                                    'x_max': '${fparse2*y_max}'}
    
def test_moose_update_vars(moose_mod):
    # Changes number of y elements, elastic modulus and element type
    # Does not change add_vars or other variables
    new_vars = {'n_elem_y': 25, 
                'e_modulus': 2e9, 
                'e_type': 'QUAD8', 
                'add_vars': 'true'}
    moose_mod.update_vars(new_vars)
    assert moose_mod._vars == {'n_elem_y': 25, 
                                'e_modulus': 2e9, 
                                'p_ratio': 0.3, 
                                'e_type': 'QUAD8', 
                                'add_vars': 'true', 
                                'y_max': 1.0, 
                                'x_max': '${fparse2*y_max}'}
    
def test_moose_update_vars_error(moose_mod):
    new_vars = {'n_elem_y': 25, 
                'n_elem_x': 50}
    with pytest.raises(KeyError) as errinfo:
        moose_mod.update_vars(new_vars)
    msg, = errinfo.value.args
    assert msg == "Key n_elem_x does not exist in the variables found in the input file. Check input file to make sure the variable exists."

def test_moose_write_file(moose_mod):
    new_vars = {'n_elem_y': 25,
                'e_modulus': 2e9, 
                'e_type': 'QUAD8'}
    moose_mod.update_vars(new_vars)

    mod_file = 'tests/moose/moose-vartest-mod.i'
    moose_mod.write_file(mod_file)
    assert os.path.isfile(mod_file)

    moose_mod_check = InputModifier(mod_file,'#','')
    assert moose_mod_check._vars == {'n_elem_y': 25, 
                                    'e_modulus': 2e9, 
                                    'p_ratio': 0.3, 
                                    'e_type': 'QUAD8', 
                                    'add_vars': 'true', 
                                    'y_max': 1.0, 
                                    'x_max': '${fparse2*y_max}'}
    
def test_moose_get_var_keys(moose_mod):
    assert moose_mod.get_var_keys() == ['n_elem_y', 
                                        'e_modulus', 
                                        'p_ratio', 
                                        'e_type', 
                                        'add_vars', 
                                        'y_max', 
                                        'x_max']
    
def test_moose_get_input_file(moose_mod):
    assert moose_mod.get_input_file() == 'tests/moose/moose-vartest.i'

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
def test_extract_var_str_moose(input_str,expected,moose_mod):
    ext_strs = moose_mod._extract_var_str(input_str)
    assert ext_strs == expected


'''
-------------------------------------------------------------------------------
Gmsh Tests
TODO: flesh out gmsh tests
-------------------------------------------------------------------------------
'''    
@pytest.fixture
def gmsh_mod():
    input_file = 'tests/gmsh/gmsh_vartest.geo'
    return InputModifier(input_file,'//',';')

def test_gmsh_find_vars(gmsh_mod):
    gmsh_mod.find_vars()
    assert gmsh_mod._var_start_ind == 11
    assert gmsh_mod._var_end_ind == 17

def test_gmsh_read_vars(gmsh_mod):
    gmsh_mod.read_vars()
    assert gmsh_mod._vars == {'p0': 0.0015, 
                               'p1': 0.001, 
                               'p2': 0.0012, 
                               'filename': '"mesh_tens_spline_2d.msh"'}
    
def test_gmsh_get_vars(gmsh_mod):
    assert gmsh_mod.get_vars()  == {'p0': 0.0015, 
                                    'p1': 0.001, 
                                    'p2': 0.0012, 
                                    'filename': '"mesh_tens_spline_2d.msh"'}

def test_gmsh_update_vars(gmsh_mod):
    new_vars = {'p1': 0.0009, 
                'p2': 0.001}
    gmsh_mod.update_vars(new_vars)
    assert gmsh_mod._vars == {'p0': 0.0015, 
                                'p1': 0.0009, 
                                'p2': 0.001, 
                                'filename': '"mesh_tens_spline_2d.msh"'}

    
def test_gmsh_update_vars_error(gmsh_mod):
    new_vars = {'p1': 0.0009, 
                'p7': 0.001}
    with pytest.raises(KeyError) as errinfo:
        gmsh_mod.update_vars(new_vars)
    msg, = errinfo.value.args
    assert msg == "Key p7 does not exist in the variables found in the input file. Check input file to make sure the variable exists."

def test_gmsh_write_file(gmsh_mod):
    new_vars = {'p1': 0.0009, 
                'p2': 0.001}
    gmsh_mod.update_vars(new_vars)

    mod_file = 'tests/gmsh/gmsh_vartest-mod.geo'
    gmsh_mod.write_file(mod_file)
    assert os.path.isfile(mod_file)

    gmsh_mod_check = InputModifier(mod_file,'//',';')
    assert gmsh_mod_check._vars == {'p0': 0.0015, 
                                    'p1': 0.0009, 
                                    'p2': 0.001, 
                                    'filename': '"mesh_tens_spline_2d.msh"'}


@pytest.mark.parametrize(
        ('input_str','expected'),
        (
            pytest.param('',('','',''),id='Degenerate blank case'),
            pytest.param('x1 = 1;',('x1',1.0,''),id='Variable only, int case'),
            pytest.param('x2 = 100.0;',('x2',100.0,''),id='Variable only, float case'),
            pytest.param('x3 = 1e3;',('x3',1000.0,''),id='Variable only, exponential case'),
            pytest.param('order = SECOND;',('order','SECOND',''),id='Variable only, string case'),
            pytest.param('x=10; // comment',('x',10.0,' comment'),id='Numeric variable and comment case'),
            pytest.param('// comment',('','',' comment'),id='Comment only case'),
        )
)
def test_extract_var_str_gmsh(input_str,expected,gmsh_mod):
    ext_strs = gmsh_mod._extract_var_str(input_str)
    assert ext_strs == expected
