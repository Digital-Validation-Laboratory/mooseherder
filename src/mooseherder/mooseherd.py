'''
===============================================================================
MOOSE Herd Class

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
'''
import os, shutil
import time
import json
import numpy as np
import multiprocessing as mp
from multiprocessing.pool import Pool
from multiprocessing.pool import ThreadPool 
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooserunner import MooseRunner
from mooseherder.gmshrunner import GmshRunner
from mooseherder.exodusreader import ExodusReader

class MooseHerd:
    """Class to run MOOSE and gmsh in parallel.
    Manages folders, running and reading.
    """
    def __init__(self, moose_runner: MooseRunner, moose_mod: InputModifier, gmsh_runner=None, gmsh_mod=None):
        """Creates the herd. Number of moose instances defaults to 2. Sets the
        default strings for the working directories and names of input files
        (MOOSE and gmsh) when they are copied to the working directories to 
        run.

        Args:
            moose_runner (MooseRunner): calls MOOSE instance to run input files.
            moose_mod (InputModifier): modifies variables at the top of the 
                MOOSE input file for the sweep.
            gmsh_runner (GmshRunner, optional): calls gmsh to create mesh for 
                the simulation. Defaults to None.
            gmsh_mod (InputModifier, optional): modifies variables in the gmsh 
                geo file. Defaults to None.
        """        
        self._moose_runner = moose_runner
        self._moose_modifier = moose_mod
        self._gmsh_runner = gmsh_runner
        self._gmsh_modifier = gmsh_mod
        
        self._n_moose = 2
        self._sub_dir = 'moose-workdir'
        self._moose_input_name = 'moose-sim'
        self._gmsh_input_name = 'gmsh-mesh'
        self._base_dir = os.path.split(self._moose_modifier.get_input_file())[0]+'/'
        self._run_dir = self._base_dir + self._sub_dir

        self._output_files = list()
        self._sweep_results = list()

        self._one_dir = False
        self._keep_all = True

        self._moose_vars = list()
        self._gmsh_vars = list()

        self._sweep_iter = 0
        self._sweep_start_time = -1.0
        self._sweep_run_time = -1.0

        self._sim_iter = 0
        self._iter_start_time = -1.0
        self._iter_run_time = -1.0

    def set_base_dir(self, base_dir: str, clear_dirs = False) -> None:
        """Changes the base directory in which the series of working 
        directories are will be created by the create_dirs function.

        Args:
            base_dir (str): path string to the base directory

        Raises:
            FileExistsError: the specified directory does not exist
        """
        #TODO check if the sweep directories exist in previous base_dir - give option to clear them
        if clear_dirs:
            self.clear_dirs()

        if not(os.path.isdir(base_dir)):
            raise FileExistsError("Specified base directory does not exist.")
        else:
            self._base_dir = base_dir

    def set_names(self, sub_dir = 'moose-workdir', moose_name = 'moose-sim', gmsh_name = 'gmsh-mesh') -> None:
        """Sets the names of the working directories for each MOOSE instance
        and the default names for the MOOSE and gmsh inputs that will be 
        copied to those directories.

        Args:
            sub_dir (str, optional): name of directories that will be created 
                in the base_dir. Defaults to 'moose-workdir'.
            moose_name (str, optional): name of the created/modified MOOSE 
                input files. Defaults to 'moose-sim'.
            gmsh_name (str, optional): name of the created/modified gmsh input 
                files. Defaults to 'gmsh-mesh'.
        """        
        self._sub_dir = sub_dir
        self._moose_input_name = moose_name
        self._gmsh_input_name = gmsh_name

    def set_flags(self, one_dir = False, keep_all = True) -> None:
        """Set boolean flags to control working directory and output file 
        management.

        Args:
            one_dir (bool, optional): true, run all simulations in a single 
                working directory. false, run in one working directory per 
                MOOSE instance. Defaults to False.
            keep_all (bool, optional): true, keep all created inputs and output
                files from simulations. false, only one run per directory is 
                kept. Defaults to True.
        """        
        self._one_dir = one_dir
        self._keep_all = keep_all

    #TODO
    '''
    def run_dir_exists(self) -> bool:
        all_dirs = os.listdir(self._base_dir)
    '''
        
    def create_dirs(self) -> None:
        """Create directories to store the MOOSE instance outputs.
        """
        self._run_dir = self._base_dir + self._sub_dir
        if self._one_dir:
            if not(os.path.isdir(self._run_dir+'-1')):
                os.mkdir(self._run_dir+'-1')  
        else:
            for nn in range(self._n_moose):
                if not(os.path.isdir(self._run_dir+'-'+str(nn+1))):
                    os.mkdir(self._run_dir+'-'+str(nn+1))
 
    def clear_dirs(self) -> None:
        """Delete the existing working directories in the base_dir and their 
        contents.
        """
        all_dirs = os.listdir(self._base_dir)            
        for dd in all_dirs:
            if os.path.isdir(self._base_dir+dd):
                if self._sub_dir in dd:
                    shutil.rmtree(self._base_dir+dd)

    def para_opts(self, n_moose = 1, tasks_per_moose = 1, threads_per_moose = 1, redirect_out = False, create_dirs=True) -> None:
        """Set MOOSE parallelisation options.

        Args:
            n_moose (int): Number of MOOSE instances running in parallel.
            tasks_per_moose (int, optional): Number of MPI tasks per MOOSE 
                instance. Defaults to 1.
            threads_per_moose (int, optional): Number of threads per MOOSE 
                instance. Defaults to 1.
            redirect_out (bool, optional): Redirect MOOSE console output to 
                file stdout. Defaults to False.
            create_dirs (bool, optional): If n_moose changes then create new 
                directories. Defaults to True.
        """
        n_moose = int(n_moose)        
        if n_moose < 0:
            n_moose = 1
        elif n_moose > os.cpu_count():
            n_moose = os.cpu_count()
        
        if self._n_moose != n_moose:
            self._n_moose = n_moose
            if create_dirs:
                self.create_dirs()

        self._moose_runner.set_opts(tasks_per_moose,threads_per_moose,redirect_out)

    def get_sweep_time(self) -> float:
        """Getter for performance timer of whole sweep.

        Returns:
            float: time to complete the whole variable sweep in seconds
        """        
        return self._sweep_run_time
    
    def get_iter_time(self) -> float:
        """Getter for performance timer of single iteration.

        Returns:
            float: time to complete specific iteration.
        """        
        return self._iter_run_time
        
    def _get_process_num(self) -> str:
        """Helper function to get the process number for directory naming.

        Returns:
            str: One character string with the process number. If this is the 
                main process returns '1' 
        """        
        name = mp.current_process().name
        # If we are calling this from main we need to set the process number
        if name == 'MainProcess':
            process_num = '1'
        else:
            process_num = name.split('-',1)[1]
        return process_num

    def run_once(self, iter: int, moose_vars: dict, gmsh_vars = None) -> str:
        """Run a single simulation. Writes relevant moose and gmsh input decks 
        to process working directory.

        Args:
            iter (int): iteration number used to label the input files 
                (MOOSE and gmsh), ensures multiple runs in the same directory
                do not overwrite. Not used if keep_all = False.
            moose_vars (dict): keys are variable names and variable values are 
                associated to the keys. Used by InputModifier to create a new
                MOOSE input file to run in the 
            gmsh_vars (dict, optional): same as moose_vars but applies to gmsh
                input file. Defaults to None.

        Returns:
            str: full path to the output exodus file.
        """        

        self._iter_start_time = time.perf_counter()

        process_num = self._get_process_num()
        if int(process_num) > self._n_moose:
            process_num = str((int(process_num) % self._n_moose)+1)

        if self._one_dir:
            run_dir = self._run_dir+'-1/'
        else:
            # Each moose has it's own directory but multiple files can be save in this directory
            run_dir = self._run_dir+'-'+process_num+'/'
        
        if self._keep_all:
            run_num = str(iter+1)
        else: # Set to overwrite based on working directory
            run_num = process_num

        # Need to create the mesh first, if required
        if (self._gmsh_modifier != None) or (gmsh_vars != None):
            gmsh_save = run_dir+self._gmsh_input_name +'-'+run_num+'.geo'
            self._gmsh_modifier.update_vars(gmsh_vars)
            self._gmsh_modifier.write_file(gmsh_save)
            self._gmsh_runner.run(gmsh_save)

        # Save the moose file with the current iteration to not overwrite
        moose_save = run_dir+self._moose_input_name +'-'+run_num+'.i'
        self._moose_modifier.update_vars(moose_vars)
        self._moose_modifier.write_file(moose_save)

        self._moose_runner.set_env_vars()
        self._moose_runner.run(moose_save)
        
        self._iter_run_time = time.perf_counter() - self._iter_start_time

        return self._moose_runner.get_output_exodus_path()
    
    def _start_sweep(self):
        """_summary_
        """     
           
        if not self._keep_all:
            self._sim_iter = 0
            self.clear_dirs()
            self.create_dirs()
        self._sweep_start_time = time.perf_counter()

    def _end_sweep(self):
        """_summary_
        """        
        self._sweep_run_time = time.perf_counter() - self._sweep_start_time
        self._sweep_iter += 1
        self._write_output_key()

    def run_sequential(self,moose_var_list: list(dict()), gmsh_var_list=None) -> None:
        """Runs MOOSE (and gmsh if specified) sequentially. Each item in the 
        list of variables is a single simulation, the total number of 
        simulations is given by len(moose_var_list). 

        Args:
            moose_vars (list(dict)): list of MOOSE variables combinations to be
                run by the herder. The dictionary keys must correspond to the 
                variables names in the MOOSE file. See the InputModifier class 
                for help.
            gmsh_vars (list(dict), optional): list of gmsh variables to be run 
                by the herder. The dictionary keys must correspond to the 
                variables names in the gmsh file. See the InputModifier class 
                for help. Defaults to None.
        """        
        self._start_sweep()

        output_files = list()
        if gmsh_var_list == None:
            ii = self._sim_iter
            for vv in moose_var_list:
                output_files.append(self.run_once(ii,vv))
                ii += 1

            self._sim_iter += len(moose_var_list)
        else:
            ii = self._sim_iter
            for vv in moose_var_list:
                for ww in gmsh_var_list:
                    output_files.append(self.run_once(ii,vv,ww))
                    ii += 1

                self._sim_iter += len(moose_var_list)*len(gmsh_var_list)

        self._output_files = output_files

        self._end_sweep()

    def run_para(self, moose_var_list: list(dict()), gmsh_var_list=None) -> None:
        """Runs MOOSE (and gmsh if specified) in parallel using multiprocessing
        apply_async. Each item in the list of variables is a single simulation,
        the total number of simulations is given by len(moose_var_list) and is 
        spread across the number of MOOSE instances specified by n_mooose.

        Args:
            moose_vars (list(dict)): list of MOOSE variables combinations to be
                run by the herder. The dictionary keys must correspond to the 
                variables names in the MOOSE file. See the InputModifier class 
                for help.
            gmsh_vars (list(dict), optional): list of gmsh variables to be run 
                by the herder. The dictionary keys must correspond to the 
                variables names in the gmsh file. See the InputModifier class 
                for help. Defaults to None.
        """
        self._start_sweep()

        with Pool(self._n_moose) as pool:
            processes = list()
            if gmsh_var_list == None:
                ii = self._sim_iter
                for vv in moose_var_list:
                        processes.append(pool.apply_async(self.run_once, args=(ii,vv)))
                        ii += 1

                self._sim_iter += len(moose_var_list)
            else:
                ii = self._sim_iter
                for vv in moose_var_list:
                    for ww in gmsh_var_list:
                        processes.append(pool.apply_async(self.run_once, args=(ii,vv,ww)))
                        ii += 1

                self._sim_iter += len(moose_var_list)*len(gmsh_var_list)
                
            self._output_files = [pp.get() for pp in processes]

        self._end_sweep()

    def get_output_key_file(self, sweep_iter = None) -> str:
        """_summary_

        Args:
            sweep_iter (int, optional): _description_. Defaults to None.

        Returns:
            str: _description_
        """        
        if sweep_iter == None:
            sweep_iter = self._sweep_iter

        return self._run_dir + '-1/' + 'output-key-{:d}.json'.format(sweep_iter)  
    
    def _write_output_key(self) -> None:
        """_summary_
        """        
        with open(self.get_output_key_file(), "w") as okf:
            json.dump(self._output_files, okf)

    def read_output_key(self, sweep_iter = None) -> list():
        """_summary_

        Args:
            sweep_iter (_type_, optional): _description_. Defaults to None.
        """   
        with open(self.get_output_key_file(sweep_iter)) as okf:
            output_files = json.load(okf)
            if sweep_iter != None:
                self._sweep_iter = sweep_iter

        return output_files

    def read_all_output_keys(self) -> list(str()):
        """_summary_

        Args:
            self (_type_): _description_

        Raises:
            FileNotFoundError: _description_

        Returns:
            _type_: _description_
        """        
        check_dir = self._run_dir+'-1'
        work_dir_files = os.listdir(check_dir)

        key_count = 0
        for ff in work_dir_files:
            if 'output-key' in ff:
                key_count += 1
        
        if key_count == 0:
            raise FileNotFoundError("No output key files found.")

        output_files = list()
        for kk in range(key_count):
            output_files = output_files + self.read_output_key(kk+1)

        self._output_files = output_files
        self._sweep_iter = len(self._output_files)

        return self._output_files

    def get_output_files(self) -> list(str()):
        """_summary_

        Returns:
            _type_: _description_
        """        
        return self._output_files
    
    def read_results_once(self, output_file: str, var_keys: list, elem_var_blocks = None) -> dict:
        """_summary_

        Args:
            output_file (str): _description_
            var_keys (list): _description_
            elem_var_blocks (_type_, optional): _description_. Defaults to None.

        Returns:
            dict: _description_
        """        

        # Create the 
        reader = ExodusReader(output_file)         
        read_vars = dict()

        # Always get the nodal coords and the time vector
        read_vars['coords'] = reader.get_coords()
        read_vars['time'] = reader.get_time()

        # Three cases:
        # 1) nodal data (no block)
        # 2) element data (with block)
        # 3) standard variable string to access anything in exodus
        for ii,kk in enumerate(var_keys):
            if kk in reader.get_node_var_names():
                read_vars[kk] = reader.get_node_data(kk)
            elif (elem_var_blocks != None) and (kk in reader.get_elem_var_names()): 
                read_vars[kk] = reader.get_elem_data(kk,elem_var_blocks[ii])
            elif kk in reader.get_all_var_names():
                read_vars[kk] = reader.get_var(kk)
            else:
                read_vars[kk] = None

        return read_vars

    def read_results_sequential(self, var_keys: list, sweep_iter = None, elem_var_blocks=None) -> list:
        """_summary_

        Args:
            var_keys (list): _description_
            elem_var_blocks (_type_, optional): _description_. Defaults to None.

        Returns:
            list: _description_
        """        
        self._start_read(sweep_iter)      

        self._sweep_results = list()
        for ff in self._output_files:
            self._sweep_results.append(
                self.read_results_once(ff,var_keys,elem_var_blocks))

        return self._sweep_results
            
    def read_results_para(self, var_keys: list, sweep_iter = None, elem_var_blocks = None) -> list:
        """_summary_

        Args:
            var_keys (list): _description_
            elem_var_blocks (_type_, optional): _description_. Defaults to None.

        Returns:
            list: _description_
        """        
        self._start_read(sweep_iter)      

        with Pool(self._n_moose) as pool:
            processes = list()
            for ff in self._output_files:
                processes.append(pool.apply_async(
                    self.read_results_once, args=(ff,var_keys,elem_var_blocks))) 

            self._sweep_results = [pp.get() for pp in processes]

        return self._sweep_results
    
    def read_results_para_generic(self, reader) -> list:
        """_summary_

        Args:
            reader (class) : class with a read() method that will read the exodus files 

        Returns:
            list: list of whatever reader.read() returns
        """        
        #self._start_read(sweep_iter)      

        with Pool(self._n_moose) as pool:
            processes = list()
            for ff in self._output_files:
                processes.append(pool.apply_async(reader.read, args=(ff,))) 

            self._sweep_results = [pp.get() for pp in processes]

        return self._sweep_results
    
    def _start_read(self,sweep_iter):
        if self._output_files == '':
            self._output_files = self.read_output_key(sweep_iter=1)

        if sweep_iter == None:
            self.read_all_output_keys()



