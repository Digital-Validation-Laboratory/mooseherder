#==============================================================================
# RUN PARALLEL MOOSE FROM PYTHON 
#
# Author: Lloyd Fletcher
#==============================================================================

import os
import numpy as np
import multiprocessing as mp
from mooseherder import MooseRunner
from mooseherder import InputModifier

#------------------------------------------------------------------------------
class MooseHerd:
    def __init__(self,input_file,moose_dir,app_dir,app_name):
        self._runners = MooseRunner(moose_dir,app_dir,app_name)
        self._modifiers = InputModifier(input_file)
        #self._reader = OutputReader()

        # Options for high throughput parallelisation
        self._n_moose = 4
        self._one_dir = True
        self._sub_dir = 'moose-run'
        self._run_dir = os.path.split(input_file)[0]+'/'+self._sub_dir
        self._keep_input = True
        self._keep_output = True
        self._sweep_vars = list()

    def create_dirs(self,one_dir=True):
        self._one_dir = one_dir
        if self._one_dir:
            try:  
                os.mkdir(self._run_dir)  
            except OSError as error:  
                print(error)   
        else:
            for nn in range(self._n_moose):
                try:
                    os.mkdir(self._run_dir+'-'+str(nn))
                except OSError as error:  
                    print(error)    

    def para_opts(self,n_moose,tasks_per_moose, threads_per_moose):
        if n_moose < 0:
            n_moose = 1
        
        if self._n_moose != n_moose:
            self._n_moose = n_moose
            self.create_dirs()

        self._runner.set_para_opts(tasks_per_moose,threads_per_moose)

    def set_sweep_vars(self,in_vars):
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

if __name__ == '__main__':
    moose_dir = '/home/lloydf/moose'
    app_dir = '/home/lloydf/moose-workdir/proteus'
    app_name = 'proteus-opt'

    input_file = 'examples/model-mech-test.i'

    herd = MooseHerd(input_file,moose_dir,app_dir,app_name)
    herd.create_dirs(False)

    n_elem_y = np.array([50,100])
    e_mod = np.array([1e9,2e9])
    p_rat = np.array([0.3,0.35])



    default_vars = {'n_elem_y':100,'e_modulus':1e9,'p_ratio':0.3}

