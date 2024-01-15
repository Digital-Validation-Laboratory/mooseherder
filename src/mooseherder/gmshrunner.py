'''
===============================================================================
Gmsh Runner Class

Authors: Rory Spencer, Lloyd Fletcher
===============================================================================
'''
import os
from mooseherder.simrunner import SimRunner

class GmshRunner(SimRunner):
    """Used to call gmsh to create a mesh file to be used to run a finite 
    element simulation.
    """    
    def __init__(self, gmsh_app = ""):
        """Create a gmsh runner with path to gmsh app.

        Args:
            gmsh_app (str, optional): full path to the gmsh app. Defaults to "".
        """        
        if gmsh_app != "":      
            self.set_gmsh_app(gmsh_app)
        else:
            self._gmsh_app = gmsh_app

        self._input_file = ""

    def set_gmsh_app(self, gmsh_app: str) -> None:
        """Sets path to the gmsh app.

        Args:
            gmsh_app (str): full path to the gmsh app.

        Raises:
            FileNotFoundError: gmsh app does not exist at the specified path.
        """        
        if os.path.exists(gmsh_app):
            self._gmsh_app = gmsh_app
        else:
            raise FileNotFoundError('Gmsh app not found at given path.')

    def set_input_file(self, input_file: str) -> None:
        """Sets the input geo file for gmsh.

        Args:
            input_file (str): Full path 

        Raises:
            FileNotFoundError: Not a .geo file
            FileNotFoundError: Geo file does not exist
        """        
        if os.path.splitext(input_file)[1] != '.geo':
            raise FileNotFoundError('Incorrect file type. Must be *.geo.')
        
        if not os.path.exists(input_file):
            raise FileNotFoundError('Specified gmsh geo file does not exist.')
        
        self._input_file = input_file

    def run(self, input_file="") -> None:
        """Run the geo file to create the mesh.

        Args:
            input_file (str, optional): Path to the .geo file containing the input. 
                Can also be preset using set_input_file. Defaults to "" and ises 
                the input file specified using set_input_file.

        Raises:
            RuntimeError: the path to the gmsh app is empty and must be 
                specified first.
            RuntimeError: the input file string is empty and must be specified
                first.
        """        
        if input_file != "":
            self.set_input_file(input_file)
        
        if self._gmsh_app == "":
            raise RuntimeError("Specify the full path to the gmsh app before calling run.")

        if self._input_file == "":
            raise RuntimeError("Specify input *.geo file before running gmsh.")
        
        self._run_str = '{} {}'.format(self._gmsh_app,self._input_file)
        os.system(self._run_str)

