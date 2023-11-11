#==============================================================================
# RUN PARALLEL MOOSE FROM PYTHON 
#
# Author: Lloyd Fletcher
#==============================================================================

import os
import numpy as np
from mooseherder import MooseRunner
from mooseherder import InputModifier

#------------------------------------------------------------------------------
class MooseHerd:
    def __init__(self,input_file,moose_dir,app_dir,app_name):
        self._runner = MooseRunner(moose_dir,app_dir,app_name)
        self._modifier = InputModifier(input_file)
        #self._reader = OutputReader()

        # Options for high throughput parallelisation
        self._n_moose = 4
        self._one_dir = True
        self._sub_dir = 'moose'

    def para_opts(self,n_moose,tasks_per_moose, threads_per_moose):
        if n_moose < 0:
            n_moose = 1
        elif self._n_moose != n_moose:
            self._n_moose = n_moose

        self._runner.set_para_opts(tasks_per_moose,threads_per_moose)

    def run_opts(self):
        pass
    
    def run_para(self):
        pass

#------------------------------------------------------------------------------
# Run the herd!
'''
ALL REQUIRED OPTIONS:
0) set dirs for moose, moose-app and moose-app name
1) run in one directory or one directory per moose, option to name directory
2) tasks/threads per moose
3) save all runs *.e or only keep last run per moose
    - rename 
4) ability to read *.e and collect QOIs (quantities of interest)
5) use of multiprocessing or command line dump without wait

VERSION 1
- Multi-dir run option
- Keep all output *.e
'''

# Initialise:
# 1) create dirs
# 2) read base input
# 3) create variable sweep var


n_tasks = os.cpu_count()
print(n_tasks)