#==============================================================================
# RUN PARALLEL MOOSE FROM PYTHON 
#
# Author: Lloyd Fletcher, Rory Spencer
#==============================================================================

from mooseherder import MooseHerd

if __name__ == '__main__':
    moose_dir = '/home/rspencer/moose'
    app_dir = '/home/rspencer/proteus'
    app_name = 'proteus-opt'

    input_file = 'examples/model-mech-test.i'

    # Start the herd and create working directories
    herd = MooseHerd(input_file,moose_dir,app_dir,app_name)
    herd.clear_dirs()
    herd.create_dirs(one_dir=False)

    # Create variables to sweep in a list of dictionaries
    n_elem_y = [50,100]
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]
    para_vars = list()
    for nn in n_elem_y:
        for ee in e_mod:
            for pp in p_rat:
                para_vars.append({'n_elem_y':nn,'e_modulus':ee,'p_ratio':pp})


    # Set the parallelisation options
    herd.para_opts(n_moose=4,tasks_per_moose=1,threads_per_moose=2)

    # Run in parallel
    herd.run_para(para_vars)
    print()
    print('------------------------------------------')
    print('Run time = '+str(herd._run_time)+' seconds')
    print('------------------------------------------')

