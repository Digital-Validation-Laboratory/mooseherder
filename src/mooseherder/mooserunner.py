'''
===============================================================================
MOOSE Runner Class

Author: Lloyd Fletcher
===============================================================================
'''
import os
import subprocess

class MooseRunner:
    """Used to run MOOSE models (*.i) from python.
    """    
    def __init__(self, moose_dir: str, app_dir: str, app_name: str):
        """Constructor for MOOSE runner taking all required paths to MOOSE app/
        Sets default parallelisation options to 1 MPI task and 1 thread. Sets 
        environment variables required for MPI setup.

        Args:
            moose_dir (str): Full path to main moose directory e.g. '/home/USER/moose'
            app_dir (str): Full path to moose app e.g. '/home/USER/moose-workdir/proteus'
            app_name (tsr): Name of the moose app to be used in the command line string e.g. 'proteus-opt'
        """        
        self._n_threads = 1
        self._n_tasks = 1
        self._redirect_stdout = False; 
        self._moose_dir = moose_dir
        self._app_dir = app_dir
        self._app_name = app_name
        self._run_str = ''
        self._input_file = ''
        self._input_dir = ''
        self._input_tag = ''

        self.set_env_vars()

    def set_env_vars(self) -> None:
        """Sets environment variables for calling MOOSE with MPI.
        """         
        # Find moose and set environment vars
        os.environ['CC'] = 'mpicc'
        os.environ['CXX'] = 'mpicxx'
        os.environ['F90'] = 'mpif90'
        os.environ['F77'] = 'mpif77'
        os.environ['FC'] = 'mpif90'
        os.environ['MOOSE_DIR'] = self._moose_dir
        os.environ["PATH"] = os.environ["PATH"] + ':' + self._app_dir

    def set_threads(self, n_threads: int) -> None:
        """Sets the number of threads asked of MOOSE on the command line.

        Args:
            n_threads (int): Number of threads. 
        """        
        # Need to make sure number is sensible based on cpu
        if n_threads <= 0:
            n_threads = 1
        if n_threads > os.cpu_count():
            n_threads = os.cpu_count()
        
        self._n_threads = int(n_threads)

    def set_tasks(self, n_tasks: int) -> None:
        """Sets the number of MPI tasks asked of MOOSE on the command line.

        Args:
            n_tasks (int): Number of mpi tasks. 
        """        
        # Need to make sure is sensible based on cpu
        if n_tasks <= 0:
            n_tasks = 1
        if n_tasks> os.cpu_count():
            n_tasks = os.cpu_count()
        
        self._n_tasks = int(n_tasks)

    def set_stdout(self, redirect_flag=True) -> None:
        """Sets MOOSE to redirect output (True) to file instead of console (False).

        Args:
            redirect_flag (bool, optional): True = output to stdout file, False
                 = output to console. Defaults to True.
        """        
        self._redirect_stdout = redirect_flag

    def set_opts(self, n_tasks=1, n_threads=1, redirect=False) -> None:
        """Sets all options for MOOSE run parallelisation and output.

        Args:
            n_tasks (int, optional): Number of mpi tasks for MOOSE run. 
                Defaults to 1.
            n_threads (int, optional): Number of threads for MOOSE run. 
                Defaults to 1.
            redirect (bool, optional): Redirect MOOSE output from console to 
                file (True). Defaults to False.
        """        
        self.set_threads(n_threads)
        self.set_tasks(n_tasks)
        self.set_stdout(redirect)

    def set_input_file(self, input_file):
        """Sets the path to the MOOSE input file and checks it exists.

        Args:
            input_file (str): full path and name of *.i MOOSE input script.

        Raises:
            FileNotFoundError: the MOOSE input script doesn't exist
        """        
        if not(os.path.isfile(input_file)):
            raise FileNotFoundError("Input file does not exist.")
        else:
            self._input_file = input_file
            self._input_dir = os.path.split(input_file)[0]+'/'
            self._input_tag = str(os.path.split(input_file)[1]).split('.')[0]
            self.assemble_run_str()

    def get_input_dir(self) -> str:
        """Gets the path to the directory for the specified input file.

        Returns:
            str: path to input file directory, if no input file is specified
                returns an empty string.
        """        
        return self._input_dir
    
    def get_input_tag(self) -> str:
        """Gets the input file name string without the path or the .i

        Returns:
            str: input file string, if no input file is specified returns an
                empty string.
        """        
        return self._input_tag

    def get_output_exodus_file(self) -> str:
        """Gets the file name (without path) for the output exodus file based 
        on the specified input file. Includes '_out.e'.

        Returns:
            str: output exodus file name without path, returns an empty string
                if no input file is specified.
        """        
        if self._input_tag != '':
            return self._input_tag + '_out.e' 
        else:
            return ''
        
    def get_output_exodus_path(self) -> str:
        """Gets the file and path for the output exodus file based 
        on the specified input file. Includes '_out.e'.

        Returns:
            str: output exodus file name with path, returns an empty string
                if no input file is specified.
        """     
        if self._input_tag != '':
            return self._input_dir + self._input_tag + '_out.e' 
        else:
            return ''
    
    def get_run_str(self) -> str:
        """Run string getter.

        Returns:
            str: command line string to run MOOSE.
        """        
        return self._run_str

    def assemble_run_str(self, input_file = '') -> str:  
        """Assmebles the command line string to run MOOSE based on current 
        options.

        Args:
            input_file (str, optional): Full path to MOOSE input file, if not 
                empty updates the input file. Defaults to "".

        Returns:
            str: command line string that will be used by the runner when run 
                is called.
        """
        if input_file != '':
            self.set_input_file(input_file)

        if self._input_file == '':
            raise RuntimeError('No input file specified, set one using set_input_file or by passing on into this function.')

        if self._redirect_stdout:
            redirect_str = ' --redirect-stdout'
        else:
            redirect_str = ''

        if self._n_tasks > 1:
            run_str = 'mpirun -np ' + str(self._n_tasks) + ' '\
                            + self._app_name \
                            + ' --n-threads=' + str(self._n_threads) + ' -i ' \
                            + self._input_file + redirect_str 
        else:
            run_str = self._app_name + \
                            ' --n-threads=' + str(self._n_threads) + ' -i ' \
                            + self._input_file + redirect_str 
        
        self._run_str = run_str
        
        return self._run_str


    def run(self, input_file = '',run_dir='') -> None:
        """Runs MOOSE based on current options by passing run string to 
        subprocess shell.

        Args:
            input_file (str, optional): Full path to MOOSE input file, if not 
                empty updates the input file. Defaults to "".
        """        
        if input_file != '':
            self.set_input_file(input_file)
        if run_dir == '':
            run_dir = os.getcwd()

        self.assemble_run_str()
        
        subprocess.run(self._run_str,shell=True,cwd=run_dir)
