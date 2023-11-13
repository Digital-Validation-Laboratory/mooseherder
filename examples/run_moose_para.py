#==============================================================================
# RUN PARALLEL MOOSE FROM PYTHON 
#
# Author: Lloyd Fletcher
#==============================================================================

from mooseherder import MooseHerd

if __name__ == '__main__':
    moose_dir = '/home/lloydf/moose'
    app_dir = '/home/lloydf/moose-workdir/proteus'
    app_name = 'proteus-opt'

    input_file = 'examples/model-mech-test.i'

    # Start the herd and create working directories
    herd = MooseHerd(input_file,moose_dir,app_dir,app_name)
    herd.create_dirs(True)

    # Create variables to sweep in a list of dictionaries
    n_elem_y = [50,100]
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]
    para_vars = list()
    for nn in n_elem_y:
        for ee in e_mod:
            for pp in p_rat:
                para_vars.append({'n_elem_y':nn,'e_modulus':ee,'p_ratio':pp})


    # Run in parallel
    herd.run_para(para_vars)
    print('------------------------------------------')
    print('Run time = '+str(herd._run_time)+' seconds')
    print('------------------------------------------')


