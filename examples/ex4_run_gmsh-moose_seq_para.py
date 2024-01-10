'''
==============================================================================
EXAMPLE 4: Run parallel gmsh+MOOSE simulation editing the gmsh parameters only

Author: Lloyd Fletcher, Rory Spencer
==============================================================================
'''
import os
from pathlib import Path
from mooseherder import MooseHerd
from mooseherder import MooseRunner
from mooseherder import GmshRunner
from mooseherder import InputModifier

def main():
    print('------------------------------------------')
    print('EXAMPLE 4: Herd Setup')
    print('------------------------------------------')

    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

    # Setup MOOSE
    moose_dir = os.path.join(user_dir,'moose')
    moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
    moose_app_name = 'proteus-opt'
    moose_input = 'scripts/moose/moose-mech-gmsh.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_vars = [moose_modifier.get_vars()]

    # Setup Gmsh
    gmsh_path = os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
    gmsh_input = 'scripts/gmsh/gmsh_tens_spline_2d.geo'

    gmsh_runner = GmshRunner(gmsh_path)
    gmsh_runner.set_input_file(gmsh_input)
    gmsh_modifier = InputModifier(gmsh_input,'//',';')
    
    # Start the herd and create working directories
    herd = MooseHerd(moose_runner,moose_modifier,gmsh_runner,gmsh_modifier)
    # Don't have to clear directories on creation of the herd but we do so here
    # so that directory creation doesn't raise errors
    herd.clear_dirs()
    herd.set_base_dir('examples/')
    herd.create_dirs()

    # Create variables to sweep in a list of dictionaries for mesh parameters 
    # 2^3=8 combinations possible
    p0 = [1E-3,2E-3]
    p1 = [1.5E-3,2E-3]
    p2 = [1E-3,3E-3]
    gmsh_vars = list()
    for nn in p0:
        for ee in p1:
            for pp in p2:
                gmsh_vars.append({'p0':nn,'p1':ee,'p2':pp})

    print('Herd sweep variables:')
    for vv in moose_vars:
        print(vv)

    # Set the parallelisation options
    herd.para_opts(n_moose=4,tasks_per_moose=1,threads_per_moose=2,redirect_out=True)

    print()
    print('------------------------------------------')
    print('EXAMPLE 4a: Run Gmsh+MOOSE once, modify gmsh only')
    print('------------------------------------------')
    
    # Single run saved in moose-workdir-1
    herd.run_once(0,moose_vars[0],gmsh_vars[0])

    print('Run time (once) = '+'{:.3f}'.format(herd.get_iter_time())+' seconds')
    print('------------------------------------------')
    print()
    print('------------------------------------------')
    print('EXAMPLE 4b: Run MOOSE sequentially, modify gmsh only')
    print('------------------------------------------')

    # Run all variable combinations (8) sequentially in moose-workdir-1
    herd.run_sequential(moose_vars,gmsh_vars)

    print('Run time (sequential) = '+'{:.3f}'.format(herd.get_sweep_time())+' seconds')
    print('------------------------------------------')
    print()
    print('------------------------------------------')
    print('EXAMPLE 4c: Run MOOSE in parallel, modify gmsh only')
    print('------------------------------------------')

    # Run all variable combinations across 4 MOOSE instances with two runs saved in
    # each moose-workdir
    herd.run_para(moose_vars,gmsh_vars)

    print('Run time (parallel) = '+'{:.3f}'.format(herd.get_sweep_time())+' seconds')
    print('------------------------------------------')
    print()

if __name__ == '__main__':
    main()

