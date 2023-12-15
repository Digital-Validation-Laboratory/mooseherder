#
#
#

import pytest
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder.outputreader import output_csv_reader


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
    
def test_reader():
    moose_dir = '/home/rspencer/moose'
    app_dir = '/home/rspencer/proteus'
    app_name = 'proteus-opt'

    input_file = '/home/rspencer/mtgo/examples/creep_mesh_test_dev.i'
    
    geo_file = 'data/gmsh_script.geo'
    
    input_modifier = InputModifier(geo_file,'//',';')

    # Start the herd and create working directories
    herd = MooseHerd(input_file,moose_dir,app_dir,app_name,input_modifier)
    herd.para_opts(n_moose=8,tasks_per_moose=1,threads_per_moose=1)
    data_list = herd.read_results(output_csv_reader,'csv')
    assert len(data_list) ==8
    print(data_list)