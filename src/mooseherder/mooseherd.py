'''
===============================================================================
MOOSE Herd Class

Author: Lloyd Fletcher, Rory Spencer
===============================================================================
'''

import os, shutil
import multiprocessing as mp
import time
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooserunner import MooseRunner
from mtgo.gmshutils import RunGmsh

class MooseHerd:
    def __init__(self,input_file,moose_dir,app_dir,app_name,input_modifier):
        self._runner = MooseRunner(moose_dir,app_dir,app_name)

        ## Want to be able to change what the modifier is and how it works. I.e. change mesh and run vs change moose input and run.
        # if the former, need to also have a way to give it the MOOSE file as well as mesh file.
        # But still need to give a moose file 
        # Would now need moose file and modified file.
        self._modifier = input_modifier #InputModifier(input_file)
        self.input_file = input_file
        #Check if modifier class is working on the input file
        self._gmsh_path = '/home/rspencer/src/gmsh/bin/gmsh'
        
        self._moose_mod = True # Is the moose file the one that's being modified?
        if self._modifier._input_file != input_file:
            self._moose_mod = False


        # Options for high throughput parallelisation
        self._n_moose = 2
        self._one_dir = True
        self._sub_dir = 'moose-workdir'
        self._input_tag = 'moose-sim'
        self._input_dir = os.path.split(input_file)[0]+'/'
        self._run_dir = self._input_dir + self._sub_dir

        self._keep_input = True
        self._keep_output = True
        self._sweep_vars = list()

    def create_dirs(self,one_dir=True,sub_dir='moose-workdir'):
        self._one_dir = one_dir
        self._sub_dir = sub_dir
        if self._one_dir:
            if not(os.path.isdir(self._run_dir+'-1')):
                os.mkdir(self._run_dir+'-1')  
        else:
            for nn in range(self._n_moose):
                if not(os.path.isdir(self._run_dir+'-'+str(nn+1))):
                    os.mkdir(self._run_dir+'-'+str(nn+1))
 
    def clear_dirs(self):
        if os.path.isdir(self._input_dir):
            all_dirs = os.listdir(self._input_dir)
        else:
            print('Input file and directory do not exist.')
            all_dirs = list()

        for dd in all_dirs:
            if os.path.isdir(self._input_dir+dd):
                if dd[0:dd.rfind('-')] == self._sub_dir:
                    shutil.rmtree(self._input_dir+dd)

    def para_opts(self,n_moose,tasks_per_moose=1, threads_per_moose=1):
        if n_moose < 0:
            n_moose = 1
        
        if self._n_moose != n_moose:
            self._n_moose = n_moose
            self.create_dirs(one_dir=self._one_dir)

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
        
        save_file = run_dir+self._input_tag +'-'+str(iter+1)+'.i'
        
        # Modify the file. Check if we're modifying the moose file or not. 
        if self._moose_mod:
            self._modifier.update_vars(run_vars)
            self._modifier.write_file(save_file)
        else:
            mesh_file = run_dir+'/'+ os.path.split(self._modifier._input_file)[-1].split('.')[0] +'_{}.geo'.format(iter+1)
            self._modifier.update_vars(run_vars)
            self._modifier.write_file(mesh_file)
            RunGmsh(self._gmsh_path,mesh_file) # Generate the mesh
            print(mesh_file)
            #copy in the moose file to run
            shutil.copyfile(self.input_file,save_file)


        # Run MOOSE input file
        self._runner.set_env_vars()
        print('Im running{}'.format(save_file))
        self._runner.run(save_file)
        

        
