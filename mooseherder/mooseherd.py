'''
===============================================================================
MOOSE Herd Class

Author: Lloyd Fletcher
===============================================================================
'''

import os
import multiprocessing as mp
import time
from .inputmodifier import InputModifier
from .mooserunner import MooseRunner

class MooseHerd:
    def __init__(self,input_file,moose_dir,app_dir,app_name):
        #self._input_file = input_file
        #self._moose_dir = moose_dir
        #self._app_dir = app_dir
        #self._app_name = app_name

        self._runner = MooseRunner(moose_dir,app_dir,app_name)
        self._modifier = InputModifier(input_file)

        # Options for high throughput parallelisation
        self._n_moose = 4
        self._one_dir = True
        self._sub_dir = 'moose-task'
        self._input_tag = 'moose-sim'
        self._run_dir = os.path.split(input_file)[0]+'/'+self._sub_dir
        self._keep_input = True
        self._keep_output = True
        self._sweep_vars = list()

        self._test_count = 0

    def create_dirs(self,one_dir=True):
        self._one_dir = one_dir
        if self._one_dir:
            try:  
                os.mkdir(self._run_dir+'-1')  
            except OSError as error:  
                print(error)   
        else:
            for nn in range(self._n_moose):
                try:
                    os.mkdir(self._run_dir+'-'+str(nn+1))
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
        self._sweep_vars = in_vars

    def run_para(self,para_vars):
        with mp.Pool(self._n_moose) as pool:
            self._start_time = time.perf_counter()

            processes = []
            for ii,vv in enumerate(para_vars):
                processes.append(pool.apply_async(self._run_sim, args=(ii,vv)))

            self._para_res = [pp.get() for pp in processes]

            self._end_time = time.perf_counter()
            self._run_time = self._end_time - self._start_time

    def _run_sim(self,iter,run_vars):
        name = mp.current_process().name
        process_num = name.split('-',1)[1]
            
        if self._one_dir:
            run_dir = self._run_dir+'-1/'
        else:
            run_dir = self._run_dir+'-'+process_num+'/'
        
        save_file = run_dir+self._input_tag +'-'+str(iter)+'.i'
        
        # Modify MOOSE input file and save to correct directory
        # save_file = ''
        self._modifier.write_mod_input(run_vars,save_file)

        # Run MOOSE input file
        self._runner.run(save_file)
