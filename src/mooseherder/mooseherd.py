'''
===============================================================================
MOOSE Herd Class

Authors: Lloyd Fletcher, Rory Spencer
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

        self._one_dir = False
        self._keep_all = True

        self._moose_vars = list()
        self._gmsh_vars = list()

        self._sweep_start_time = -1.0
        self._sweep_run_time = -1.0
        self._iter_start_time = -1.0
        self._iter_run_time = -1.0

    def set_base_dir(self, base_dir: str) -> None:
        """Changes the base directory in which the series of working 
        directories are will be created by the create_dirs function.

        Args:
            base_dir (str): path string to the base directory

        Raises:
            FileExistsError: the specified directory does not exist
        """        
        if not(os.path.isdir(base_dir)):
            raise FileExistsError("Specified base directory does not exist.")
        else:
            self._base_dir = base_dir

    def set_names(self, sub_dir = 'moose-workdir', moose_name = 'moose-sim', gmsh_name = 'gmsh_name') -> None:
        """Sets the names of the working directories for each MOOSE instance
        and the default names for the MOOSE and gmsh inputs that will be 
        copied to those directories.

        Args:
            sub_dir (str, optional): name of directories that will be created 
                in the base_dir. Defaults to 'moose-workdir'.
            moose_name (str, optional): name of the created/modified MOOSE 
                input files. Defaults to 'moose-sim'.
            gmsh_name (str, optional): name of the created/modified gmsh input 
                files. Defaults to 'gmsh_name'.
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
        if os.path.isdir(self._base_dir):
            all_dirs = os.listdir(self._base_dir)
        else:
            all_dirs = list()
            raise FileNotFoundError('Base directory does not exist.')
            
        for dd in all_dirs:
            if os.path.isdir(self._base_dir+dd):
                if dd[0:dd.rfind('-')] == self._sub_dir:
                    shutil.rmtree(self._base_dir+dd)

    def para_opts(self, n_moose: int, tasks_per_moose=1, threads_per_moose=1, redirect_out=False, create_dirs=True) -> None:
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

        if n_moose < 0:
            n_moose = 1
        
        if self._n_moose != n_moose:
            self._n_moose = n_moose
            if create_dirs:
                self.create_dirs()

        self._moose_runner.set_opts(tasks_per_moose,threads_per_moose,redirect_out)

    ''' TODO: is this needed or should we just pass in the list to the run functions?
    def set_sweep_vars(self, moose_vars: list(dict), gmsh_vars=None) -> None:
        """Sets the list of variables that will be swept by running the herder.
        One simulation is run per element in the list using the dictionary of
        variables specified. 

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
        self._moose_vars = moose_vars
        self._gmsh_vars = gmsh_vars
    '''

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

    def run_once(self, iter: int, moose_vars: dict, gmsh_vars=None) -> None:
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
        with mp.Pool(self._n_moose) as pool:
            self._sweep_start_time = time.perf_counter()

            processes = []
            if gmsh_var_list == None:
                for ii,vv in enumerate(moose_var_list):
                        processes.append(pool.apply_async(self.run_once, args=(ii,vv)))
            else:
                ii = 0
                for vv in moose_var_list:
                    for ww in gmsh_var_list:
                        processes.append(pool.apply_async(self.run_once, args=(ii,vv,ww)))
                        ii += 1
                
            self._para_res = [pp.get() for pp in processes]
 
            self._sweep_run_time = time.perf_counter() - self._sweep_start_time

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
        self._sweep_start_time = time.perf_counter()

        if gmsh_var_list == None:
            for ii,vv in enumerate(moose_var_list):
                self.run_once(ii,vv)
        else:
            ii = 0
            for vv in moose_var_list:
                for ww in gmsh_var_list:
                    self.run_once(ii,vv,ww)
                    ii += 1

        self._sweep_run_time = time.perf_counter() - self._sweep_start_time

    #TODO: need to write once, sequential and parallel reader functions.
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
