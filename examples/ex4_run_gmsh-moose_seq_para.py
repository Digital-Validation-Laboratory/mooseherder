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
from mooseherder import DirectoryManager


USER_DIR = Path.home()

def main():
    """main _summary_
    """
    print('------------------------------------------')
    print('EXAMPLE 4: Herd Setup')
    print('------------------------------------------')
    user_dir = Path.home()


    # Setup MOOSE
    moose_dir = USER_DIR / 'moose'
    moose_app_dir = USER_DIR / 'moose-workdir/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = Path('scripts/moose/moose-mech-simple.i')

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_runner.set_opts(n_tasks = 1,
                          n_threads = 2,
                          redirect_out = True)

    # Setup Gmsh
    gmsh_path = USER_DIR / 'moose-workdir/gmsh/bin/gmsh'
    gmsh_input = Path('scripts/gmsh/gmsh_tens_spline_2d.geo')

    gmsh_runner = GmshRunner(gmsh_path)
    gmsh_runner.set_input_file(gmsh_input)
    gmsh_modifier = InputModifier(gmsh_input,'//',';')

    # Setup herd composition
    sim_runners = [gmsh_runner,moose_runner]
    input_modifiers = [gmsh_modifier,moose_modifier]
    dir_manager = DirectoryManager(n_dirs=4)

    # Start the herd and create working directories
    herd = MooseHerd(sim_runners,input_modifiers,dir_manager)
    # Don't have to clear directories on creation of the herd but we do so here
    # so that directory creation doesn't raise errors
    dir_manager.set_base_dir(Path('examples/'))
    dir_manager.clear_dirs()
    dir_manager.create_dirs()

    # Create variables to sweep in a list of dictionaries for mesh parameters
    # 2^3=8 combinations possible
    p0 = [1E-3,2E-3]
    p1 = [1.5E-3,2E-3]
    p2 = [1E-3,3E-3]
    var_sweep = list([])
    for nn in p0:
        for ee in p1:
            for pp in p2:
                var_sweep.append([{'p0':nn,'p1':ee,'p2':pp},None])

    print('Herd sweep variables:')
    for vv in var_sweep:
        print(vv)

    print()
    print('------------------------------------------')
    print('EXAMPLE 4a: Run Gmsh+MOOSE once, modify gmsh only')
    print('------------------------------------------')

    # Single run saved in moose-workdir-1
    herd.run_once(0,var_sweep[0])

    print('Run time (once) = '+'{:.3f}'.format(herd.get_iter_time())+' seconds')
    print('------------------------------------------')
    print()

    return
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

