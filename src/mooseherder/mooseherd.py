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
from mooseherder.outputreader import output_csv_reader
from mooseherder.mooserunner import MooseRunner
from mtgo.gmshutils import RunGmsh

class MooseHerd:
    """Class to run MOOSE in parallel.
    Manages folders, running and reading.
    """
    def __init__(self,input_file,moose_dir,app_dir,app_name,input_modifier):
        """Initialise class.

        Args:
            input_file (str): Path to the input file. Should be a MOOSE .i file.
            moose_dir (str): Path to where MOOSE is installed on the system.
            app_dir (str): Path to the specific MOOSE application installed, i.e. proteus
            app_name (str): Name of the MOOSE application e.g. proteus-opt.
            input_modifier (InputModifier): Instance of input modifier class.  
        """
        
        self._runner = MooseRunner(moose_dir,app_dir,app_name)

        # Might want to change behaviour to allow herd to be initialised without deleting folders etc. Helpful for debugging.
         
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
        """Create Directories to store the MOOSE instances.

        Args:
            one_dir (bool, optional): Is there only one folder?. Defaults to True.
            sub_dir (str, optional): Name of the subdirectory. Defaults to 'moose-workdir'.
        """
        self._one_dir = one_dir
        self._sub_dir = sub_dir
        self._run_dir = self._input_dir + self._sub_dir
        if self._one_dir:
            if not(os.path.isdir(self._run_dir+'-1')):
                os.mkdir(self._run_dir+'-1')  
        else:
            for nn in range(self._n_moose):
                if not(os.path.isdir(self._run_dir+'-'+str(nn+1))):
                    os.mkdir(self._run_dir+'-'+str(nn+1))
 
    def clear_dirs(self):
        """Delete the existing directories and their contents.
        """
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
        """Set the parallelisation options. 

        Args:
            n_moose (_type_): _description_
            tasks_per_moose (int, optional): _description_. Defaults to 1.
            threads_per_moose (int, optional): _description_. Defaults to 1.
        """
        if n_moose < 0:
            n_moose = 1
        
        if self._n_moose != n_moose:
            self._n_moose = n_moose
            self.create_dirs(one_dir=self._one_dir,sub_dir=self._sub_dir)

        self._runner.set_para_opts(tasks_per_moose,threads_per_moose)

    def set_sweep_vars(self,in_vars):
        self._sweep_vars = in_vars

    def run_para(self,para_vars):
        """Run MOOSE in parallel using multiprocessing async.

        Args:
            para_vars (list of dict): List of len(n_threads) containing the parameters to use for each process.
        """
        with mp.Pool(self._n_moose) as pool:
            self._start_time = time.perf_counter()

            processes = []
            for ii,vv in enumerate(para_vars):
                processes.append(pool.apply_async(self._run_sim, args=(ii,vv)))

            self._para_res = [pp.get() for pp in processes]

            self._end_time = time.perf_counter()
            self._run_time = self._end_time - self._start_time

    def _run_sim(self,iter,run_vars):
        """Run a simulation. 

        Args:
            iter (int): Index of process number. 
            run_vars (dict): Parameters to be passed to update the input.
        """
        name = mp.current_process().name
        process_num = name.split('-',1)[1]
        #print(process_num)
            
        if self._one_dir:
            run_dir = self._run_dir+'-1/'
        else:
            #run_dir = self._run_dir+'-'+process_num+'/'
            run_dir = self._run_dir+'-'+str(iter+1)+'/'
        
        save_file = run_dir+self._input_tag +'-'+str(iter+1)+'.i'
        
        # Modify the file. Check if we're modifying the moose file or not. 
        if self._moose_mod:
            print('*****Updating Moose Input*****')
            self._modifier.update_vars(run_vars)
            self._modifier.write_file(save_file)
        else:
            print('*****Updating Mesh*****')
            mesh_file = run_dir+'/'+ os.path.split(self._modifier._input_file)[-1].split('.')[0] +'_{}.geo'.format(iter+1)
            self._modifier.update_vars(run_vars)
            self._modifier.write_file(mesh_file)
            RunGmsh(self._gmsh_path,mesh_file) # Generate the mesh
            #print(mesh_file)
            #copy in the moose file to run
            shutil.copyfile(self.input_file,save_file)


        # Run MOOSE input file
        self._runner.set_env_vars()
        print('Running file: {}'.format(save_file))
        self._runner.run(save_file)
          

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
