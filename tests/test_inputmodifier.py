#
#
#

import pytest
from mooseherder.inputmodifier import InputModifier

def test_moose_write():
    input_file = 'examples/model-mech-test.i'
    input_modifier = InputModifier(input_file,'#','')
    input_modifier.write_file('/home/rspencer/mooseherder/examples/model-mech-test_mod.i')

def test_params():
    input_file = 'data/gmsh_script_3d.geo'
    input_modifier = InputModifier(input_file,'//',';')
    v = input_modifier.get_var_keys()
    assert v[0] == 'p0'
    assert v[1] == 'p1'
    assert v[2] == 'p2'