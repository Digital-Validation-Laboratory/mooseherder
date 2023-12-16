'''
===============================================================================
Gmsh Runner Class

Used to call gmsh to create a mesh file to use to run a finite element sim.

Author: Rory Spencer, Lloyd Fletcher
===============================================================================
'''
import os

class GmshRunner:
    """_summary_
    """    
    def __init__(self,gmsh_path=""):
        """Constructor for gmsh runner.

        Args:
            gmsh_path (str): Full path to gmsh app.
        """        
        self._gmsh_path = gmsh_path
        self._input_file = ""

    def set_input_file(self,input_file):
        """Sets the input geo file for gmsh.

        Args:
            input_file (str): Full path 

        Raises:
            FileNotFoundError: Not a .geo file
            FileNotFoundError: Geo file does not exist
        """        
        if os.path.splitext(input_file)[1] != '.geo':
            raise FileNotFoundError('Incorrect file type. Must be .geo.')
        
        if not os.path.exists(input_file):
            raise FileNotFoundError('Gmsh geo file not found.')
        
        self._input_file = input_file

    def run(self,input_file=""):
        """Run the geo file given

        Args:
            input_file (string): Path to the .geo file containing the input.
        """
        if input_file != "":
            self.set_input_file(input_file)
        
        self._run_str = '{} {}'.format(self._gmsh_path,self._input_file)
        os.system(self._run_str)

