'''
===============================================================================
MOOSE Herd Class

Author: Lloyd Fletcher, Rory Spencer
===============================================================================
'''
import os, shutil
import time
import multiprocessing as mp
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooserunner import MooseRunner
from mooseherder.gmshrunner import GmshRunner

class MooseHerd:
    """Class to run MOOSE and gmsh in parallel.
    Manages folders, running and reading.
    """
    def __init__(self,moose_runner: MooseRunner,moose_mod: InputModifier,gmsh_runner=None,gmsh_mod=None):
        """_summary_

        Args:
            moose_runner (MooseRunner): _description_
            moose_mod (InputModifier): _description_
            gmsh_runner (GmshRunner, optional): _description_. Defaults to None.
            gmsh_mod (InputModifier, optional): _description_. Defaults to None.
        """        
        self._moose_runner = moose_runner
        self._moose_modifier = moose_mod
        self._gmsh_runner = gmsh_runner
        self._gmsh_modifier = gmsh_mod
        
        self._n_moose = 2
        self._sub_dir = 'moose-workdir'
        self._moose_input_tag = 'moose-sim'
        self._gmsh_input_tag = 'gmsh-mesh'
        self._base_dir = os.path.split(self._moose_modifier.get_input_file())[0]+'/'
        self._run_dir = self._base_dir + self._sub_dir

        self._one_dir = True
        self._keep_all = True

        self._moose_vars = list()
        self._gmsh_vars = list()

        self._sweep_start_time = -1.0
        self._sweep_run_time = -1.0
        self._iter_start_time = -1.0
        self._iter_run_time = -1.0

    def set_base_dir(self,base_dir: str) -> None:
        """_summary_

        Args:
            run_dir (str): _description_

        Raises:
            FileExistsError: _description_
        """        
        if not(os.path.isdir(base_dir)):
            raise FileExistsError("Run directory does not exist.")
        else:
            self._base_dir = base_dir

    def set_flags(self,one_dir: bool,keep_all: bool) -> None:
        """_summary_

        Args:
            one_dir (_type_): _description_
            keep_all (_type_): _description_
        """        
        self._one_dir = one_dir
        self._keep_all = keep_all

    def create_dirs(self,one_dir=True,sub_dir='moose-workdir') -> None:
        """Create Directories to store the MOOSE instance outputs.

        Args:
            one_dir (bool, optional): Is there only one folder?. Defaults to True.
            sub_dir (str, optional): Name of the subdirectory. Defaults to 'moose-workdir'.
        """
        self._one_dir = one_dir
        self._sub_dir = sub_dir
        self._run_dir = self._base_dir + self._sub_dir
        if self._one_dir:
            if not(os.path.isdir(self._run_dir+'-1')):
                os.mkdir(self._run_dir+'-1')  
        else:
            for nn in range(self._n_moose):
                if not(os.path.isdir(self._run_dir+'-'+str(nn+1))):
                    os.mkdir(self._run_dir+'-'+str(nn+1))
 
    def clear_dirs(self) -> None:
        """Delete the existing directories and their contents.
        """
        if os.path.isdir(self._base_dir):
            all_dirs = os.listdir(self._base_dir)
        else:
            all_dirs = list()
            raise FileNotFoundError('Input file and directory do not exist.')
            
        for dd in all_dirs:
            if os.path.isdir(self._base_dir+dd):
                if dd[0:dd.rfind('-')] == self._sub_dir:
                    shutil.rmtree(self._base_dir+dd)

    def para_opts(self,n_moose: int,tasks_per_moose=1, threads_per_moose=1, redirect_out=False, create_dirs=True) -> None:
        """Set MOOSE parallelisation options.

        Args:
            n_moose (int): Number of MOOSE instances running in paralle
            tasks_per_moose (int, optional): Number of MPI tasks per MOOSE instance. Defaults to 1.
            threads_per_moose (int, optional): Number of threads per MOOSE instance. Defaults to 1.
            redirect_out (bool, optional): Redirect MOOSE console output to file stdout. Defaults to False.
            create_dirs (bool, optional): If n_moose changes then create new directories. Defaults to True.
        """        

        if n_moose < 0:
            n_moose = 1
        
        if self._n_moose != n_moose:
            self._n_moose = n_moose
            if create_dirs:
                self.create_dirs(one_dir=self._one_dir,sub_dir=self._sub_dir)

        self._moose_runner.set_opts(tasks_per_moose,threads_per_moose,redirect_out)

    def set_sweep_vars(self,moose_vars: dict, gmsh_vars=None) -> None:
        """_summary_

        Args:
            moose_vars (dict): _description_
            gmsh_vars (dict, optional): _description_. Defaults to None.
        """        
        self._moose_vars = moose_vars
        self._gmsh_vars = gmsh_vars

    def get_sweep_time(self) -> float:
        return self._sweep_run_time
    
    def get_iter_time(self) -> float:
        return self._iter_run_time

    def run_once(self,iter,moose_vars,gmsh_vars=None) -> None:
        """Run a single simulation. Writes relevant moose and gmsh input decks to process working directory.

        Args:
            iter (int): Index of process number. 
            run_vars (dict): Parameters to be passed to update the input.
        """
        self._iter_start_time = time.perf_counter()

        name = mp.current_process().name
        # If we are calling this from main we need to set the process number
        if name == 'MainProcess':
            process_num = '1'
        else:
            process_num = name.split('-',1)[1]

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
            gmsh_save = run_dir+self._gmsh_input_tag +'-'+run_num+'.geo'
            self._gmsh_modifier.update_vars(gmsh_vars)
            self._gmsh_modifier.write_file(gmsh_save)
            self._gmsh_runner.run(gmsh_save)

        # Save the moose file with the current iteration to not overwrite
        moose_save = run_dir+self._moose_input_tag +'-'+run_num+'.i'
        self._moose_modifier.update_vars(moose_vars)
        self._moose_modifier.write_file(moose_save)

        self._moose_runner.set_env_vars()
        self._moose_runner.run(moose_save)

        self._iter_run_time = time.perf_counter() - self._iter_start_time

    def run_para(self,moose_vars: list(dict()), gmsh_vars=None) -> None:
        """Run MOOSE in parallel using multiprocessing async.

        Args:
            para_vars (list of dict): List containing the parameters to use for each process.
        """
        with mp.Pool(self._n_moose) as pool:
            self._sweep_start_time = time.perf_counter()

            processes = []
            if gmsh_vars == None:
                for ii,vv in enumerate(moose_vars):
                        processes.append(pool.apply_async(self.run_once, args=(ii,vv)))
            else:
                ii = 0
                for vv in moose_vars:
                    for ww in gmsh_vars:
                        processes.append(pool.apply_async(self.run_once, args=(ii,vv,ww)))
                        ii += 1
                
            self._para_res = [pp.get() for pp in processes]
 
            self._sweep_run_time = time.perf_counter() - self._sweep_start_time

    def run_sequential(self,moose_vars: list(dict()), gmsh_vars=None) -> None:
        """_summary_

        Args:
            moose_vars (_type_): _description_
            gmsh_vars (_type_, optional): _description_. Defaults to None.
        """        
        self._sweep_start_time = time.perf_counter()

        if gmsh_vars == None:
            for ii,vv in enumerate(moose_vars):
                self.run_once(ii,vv)
        else:
            ii = 0
            for vv in moose_vars:
                for ww in gmsh_vars:
                    self.run_once(ii,vv,ww)
                    ii += 1

        self._sweep_run_time = time.perf_counter() - self._sweep_start_time

    def read_results_para(self, reader):
        """Read results in parallel. 

        Args:
            reader (ReaderClass): Class for reading files, should have a read() method. Either csv or .e currently.
        
        Returns:
            list: List of whatever reader reads.
        """
        
   
        # Iterate over folders to get results. if no results, throw error
        with mp.Pool(self._n_moose) as pool:
            processes = []
            for iter in range(self._n_moose):
                folderpath = self._run_dir+'-'+str(iter+1)
                result_path = folderpath + '/' + self._input_tag + '-' + str(iter+1) + '_out.' + reader._extension
                processes.append(pool.apply_async(reader.read, (result_path,))) # tuple is important, otherwise it unpacks strings for some reason

            # Occasionally seems to error, but not sure why. 
            # Hangs, but can read files when run afterwards.
            data_list=[pp.get() for pp in processes]


        return data_list
