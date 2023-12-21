"""
==============================================================================
EXAMPLE 2c: 
Use the os module and terminal commands to run gmsh and MOOSE from python

Author: Lloyd Fletcher
==============================================================================
"""
import time
import os, shutil
from pathlib import Path
from mooseherder import GmshRunner
from mooseherder import MooseRunner

path_parts = Path(os.getcwd()).parts
user_dir = os.path.join(path_parts[0],path_parts[1],path_parts[2])

print('------------------------------------------')
print('EXAMPLE 2c: Run Gmsh+MOOSE once')
print('------------------------------------------')
gmsh_path = os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
gmsh_runner = GmshRunner(gmsh_path)

gmsh_input = 'scripts/gmsh/gmsh_tens_spline_2d.geo'
gmsh_runner.set_input_file(gmsh_input)

print('Gmsh path:' + gmsh_path)
print('Gmsh input:' + gmsh_runner._input_file)
print()

print('Running gmsh...')
print()
gmsh_start = time.perf_counter()
gmsh_runner.run()
gmsh_end = time.perf_counter()

# Create the moose runner with correct paths to moose and apps
moose_dir = os.path.join(user_dir,'moose')
moose_app_dir = os.path.join(user_dir,'moose-workdir/proteus')
moose_app_name = 'proteus-opt'
moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)

print('MOOSE directory:' + moose_dir)
print('MOOSE app directory: ' + moose_app_dir)
print('MOOSE app name: ' + moose_app_name)
print()

# Set input and parallelisation options
moose_runner.set_opts(n_tasks=4,n_threads=2,redirect=True)
input_file = 'scripts/moose/moose-mech-gmsh.i'
moose_runner.set_input_file(input_file)

# Copy mesh file into the directory
moose_mesh_file = os.path.split(input_file)[0]+'/mesh_tens_spline_2d.msh'
msh_file = 'scripts/gmsh/mesh_tens_spline_2d.msh'
shutil.copyfile(msh_file,moose_mesh_file)

# Run the MOOSE!
print('Running moose with:')
print(moose_runner.get_run_str())
print()

moose_start = time.perf_counter()
moose_runner.run()
moose_end = time.perf_counter()

print('Gmsh run time = '+'{:.2f}'.format(gmsh_end-gmsh_start)+' seconds')
print('MOOOSE run time = '+'{:.2f}'.format(moose_end-moose_start)+' seconds')
print('------------------------------------------')
print()


