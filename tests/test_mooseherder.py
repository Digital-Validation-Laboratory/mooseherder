#
#
#

import pytest
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier



def test_input_modifier():
    input_file = 'examples/model-mech-test.i'
    input_modifier = InputModifier(input_file,'#','')
    vars= input_modifier._vars
    assert vars['n_elem_y'] ==100
    assert vars['e_modulus'] == pytest.approx(1E9)
    assert vars['p_ratio'] == pytest.approx(0.3)

def test_file_check():
    moose_dir = '/home/rspencer/moose'
    app_dir = '/home/rspencer/proteus'
    app_name = 'proteus-opt'

    input_file = 'examples/model-mech-test.i'
    
    geo_file = 'data/gmsh_script.geo'
    
    input_modifier = InputModifier(geo_file,'//',';')

    # Start the herd and create working directories
    herd = MooseHerd(input_file,moose_dir,app_dir,app_name,input_modifier)
    assert herd._moose_mod == False

    input_modifier = InputModifier(input_file,'#','')
     
    herd = MooseHerd(input_file,moose_dir,app_dir,app_name,input_modifier)
    assert herd._moose_mod == True
    