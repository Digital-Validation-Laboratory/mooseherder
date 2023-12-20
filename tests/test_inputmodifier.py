'''
==============================================================================
TEST: Input Modifier

Authors: Lloyd Fletcher, Rory Spencer
==============================================================================
'''

import pytest
from mooseherder.inputmodifier import InputModifier

def test_moose_read():
    input_file = 'scripts/moose-mech-simple.i'
    input_mod = InputModifier(input_file,'#','')
    assert input_mod._vars == {'n_elem_y': 100.0, 'e_modulus': 1000000000.0, 'p_ratio': 0.3}

    
'''
def test_params():
    input_file = 'data/gmsh_script_3d.geo'
    input_modifier = InputModifier(input_file,'//',';')
    v = input_modifier.get_var_keys()
    assert v[0] == 'p0'
    assert v[1] == 'p1'
    assert v[2] == 'p2'
'''