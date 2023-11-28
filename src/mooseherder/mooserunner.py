'''
===============================================================================
MOOSE Runner Class

Used to be able to call MOOSE models from python for parallelisation and 
coupling to python based optimisers.

Author: Lloyd Fletcher
===============================================================================
'''

import os
import subprocess

class MooseRunner:
    def __init__(self,moose_dir,app_dir,app_name):
        self.n_threads = 1
        self.n_tasks = 1
        self.moose_dir = moose_dir
        self.app_dir = app_dir
        self.app_name = app_name

        # Find moose and set environment vars
        self.set_env_vars()

    def set_env_vars(self):
         # Find moose and set environment vars
        os.environ['CC'] = 'mpicc'
        os.environ['CXX'] = 'mpicxx'
        os.environ['F90'] = 'mpif90'
        os.environ['F77'] = 'mpif77'
        os.environ['FC'] = 'mpif90'
        os.environ['MOOSE_DIR'] = self.moose_dir
        os.environ["PATH"] = os.environ["PATH"] + ':' + self.app_dir


    def set_threads(self,n_threads):
        # Need to make sure number of threads is sensible basedon cpu
        if n_threads <= 0:
            n_threads = 1
        if n_threads > os.cpu_count():
            n_threads = os.cpu_count()
        
        self.n_threads = n_threads

    def set_tasks(self,n_tasks):
        # Need to make sure number of threads is sensible basedon cpu
        if n_tasks <= 0:
            n_tasks = 1
        if n_tasks> os.cpu_count():
            n_tasks = os.cpu_count()
        
        self.n_tasks = n_tasks

    def set_para_opts(self,n_tasks,n_threads):
        self.set_threads(n_threads)
        self.set_tasks(n_tasks)

    def run(self,input_file):
        if self.n_tasks > 1:
            self.cmd_str = 'mpirun -np ' + str(self.n_tasks) + ' '\
                            + self.app_name \
                            + ' --n-threads=' + str(self.n_threads) + ' -i ' \
                            + input_file
        else:
            self.cmd_str = self.app_name + \
                            ' --n-threads=' + str(self.n_threads) + ' -i ' \
                            + input_file
        
        #os.system(self.cmd_str)
        subprocess.run(self.cmd_str,shell=True)
