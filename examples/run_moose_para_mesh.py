#==============================================================================
# RUN PARALLEL MOOSE FROM PYTHON 
#
# Author: Lloyd Fletcher, Rory Spencer
#==============================================================================

from mooseherder import MooseHerd
from mooseherder.inputmodifier import InputModifier

if __name__ == '__main__':
    moose_dir = '/home/rspencer/moose'
    app_dir = '/home/rspencer/proteus'
    app_name = 'proteus-opt'

    input_file = 'examples/creep_mesh_test.i'

    geo_file = 'data/gmsh_script_3d.geo'
    
    input_modifier = InputModifier(geo_file,'//',';')
    #input_modifier = InputModifier(input_file,'#','')
    # Start the herd and create working directories
    herd = MooseHerd(input_file,moose_dir,app_dir,app_name,input_modifier)
    herd.clear_dirs()
    herd.create_dirs(one_dir=False)

    # Create variables to sweep in a list of dictionaries for mesh.
    p0 = [1E-3,2E-3]
    p1 = [1.5E-3,2E-3]
    p2 = [1E-3,3E-3]
    para_vars = list()
    for nn in p0:
        for ee in p1:
            for pp in p2:
                para_vars.append({'p0':nn,'p1':ee,'p2':pp})


    # Set the parallelisation options
    herd.para_opts(n_moose=len(para_vars),tasks_per_moose=1,threads_per_moose=2)

    # Run in parallel
    herd.run_para(para_vars)
    print()
    print('------------------------------------------')
    print('Run time = '+str(herd._run_time)+' seconds')
    print('------------------------------------------')

