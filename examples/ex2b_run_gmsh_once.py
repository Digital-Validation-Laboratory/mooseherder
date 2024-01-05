"""
==============================================================================
EXAMPLE 2b: Run gmsh with mooseherder once

Author: Lloyd Fletcher
==============================================================================
"""
import time
import os
from pathlib import Path
from mooseherder import GmshRunner

def main():
    path_parts = Path(os.getcwd()).parts
    user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

    print('------------------------------------------')
    print('EXAMPLE 2b: Run Gmsh 2D once')
    print('------------------------------------------')
    gmsh_path = os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
    gmsh_runner = GmshRunner(gmsh_path)

    gmsh_input = 'scripts/gmsh/gmsh_tens_spline_2d.geo'
    gmsh_runner.set_input_file(gmsh_input)

    print('Gmsh path:' + gmsh_path)
    print('Gmsh input:' + gmsh_runner._input_file)

    print('Running gmsh...')
    start_time = time.perf_counter()
    gmsh_runner.run()
    end_time = time.perf_counter()

    print()
    print('Gmsh 2D run time = '+'{:.3f}'.format(end_time-start_time)+' seconds')
    print('------------------------------------------')
    print()

    print('------------------------------------------')
    print('EXAMPLE 2b: Run Gmsh 3D once')
    print('------------------------------------------')
    gmsh_path = os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
    gmsh_runner = GmshRunner(gmsh_path)

    gmsh_input = 'scripts/gmsh/gmsh_tens_spline_3d.geo'
    gmsh_runner.set_input_file(gmsh_input)

    print('Gmsh path:' + gmsh_path)
    print('Gmsh input:' + gmsh_runner._input_file)

    print('Running gmsh...')
    start_time = time.perf_counter()
    gmsh_runner.run()
    end_time = time.perf_counter()

    print()
    print('Gmsh 3D run time = '+'{:.3f}'.format(end_time-start_time)+' seconds')
    print('------------------------------------------')
    print()

if __name__ == '__main__':
    main()


