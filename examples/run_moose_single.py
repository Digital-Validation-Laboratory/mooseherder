#==============================================================================
# RUN GOOSE FROM PYTHON 
# Use the os module and terminal commands to run gmsh and MOOSE from python
#
# Author: Lloyd Fletcher
#==============================================================================

import os, sys
import mooseherder

# Run moose with tamer
moose_dir = '/home/lloydf/moose'
app_dir = '/home/lloydf/moose-workdir/proteus'
app_name = 'proteus-opt'
tamer = mooseherder.MooseTamer(moose_dir,app_dir,app_name)

input_file = 'examples/model-mech-test.i'

tamer.set_para_opts(4,2)
tamer.run(input_file)

