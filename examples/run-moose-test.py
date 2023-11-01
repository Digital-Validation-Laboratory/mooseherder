#==============================================================================
# RUN GMSH+MOOSE FROM PYTHON 
# Use the os module and terminal commands to run gmsh and MOOSE from python
# Allows for parallelisation with python
#
# Author: Lloyd Fletcher
#==============================================================================

import os, sys

# Add the main parent directory to the path to 
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from pysrc.moosetamer import MooseTamer

# Run moose with tamer
moose_dir = '/home/lloydf/moose'
app_dir = '/home/lloydf/moose-workdir/proteus'
app_name = 'proteus-opt'
tamer = MooseTamer(moose_dir,app_dir,app_name)

input_file = 'model-tensile-test.i'
tamer.set_para_opts(4,2)
tamer.run(input_file)

print('Finished')