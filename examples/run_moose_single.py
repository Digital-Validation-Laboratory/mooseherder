#==============================================================================
# RUN GOOSE FROM PYTHON 
# Use the os module and terminal commands to run gmsh and MOOSE from python
#
# Author: Lloyd Fletcher
#==============================================================================
import os, sys
from mooseherder import MooseRunner

moose_dir = '/home/lloydf/moose'
app_dir = '/home/lloydf/moose-workdir/proteus'
app_name = 'proteus-opt'
runner = MooseRunner(moose_dir,app_dir,app_name)

input_file = 'examples/model-mod-vars1.i'

runner.set_para_opts(4,2)
runner.run(input_file)

