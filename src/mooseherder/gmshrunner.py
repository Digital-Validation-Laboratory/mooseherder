'''
===============================================================================
Gmsh Runner Class

Authors: Rory Spencer, Lloyd Fletcher
===============================================================================
'''
import os
from pathlib import Path
from mooseherder.simrunner import SimRunner

class GmshRunner(SimRunner):
    """Used to call gmsh to create a mesh file to be used to run a finite
    element simulation. Implements the SimRunner abstract interface so that it
    can be used by the herd.
    """
    def __init__(self, gmsh_app: Path | None = None):
        """Create a gmsh runner with path to the gmsh app.

        Args:
            gmsh_app (Path, optional): full path to the gmsh app. Defaults to None.
        """
        if gmsh_app is None:
            self._gmsh_app = None
        else:
            self.set_gmsh_app(gmsh_app)

        self._input_path = None
        self._run_str = ""

    def set_gmsh_app(self, gmsh_app: Path) -> None: # type: ignore
        """Sets path to the gmsh app.

        Args:
            gmsh_app (str): full path to the gmsh app.

        Raises:
            FileNotFoundError: gmsh app does not exist at the specified path.
        """
        if not gmsh_app.exists():
            raise FileNotFoundError('Gmsh app not found at given path.')

        self._gmsh_app = gmsh_app


    def get_input_file(self) -> Path | None:
        """get_input_path: the path to the input file to run gmsh with.

        Returns:
            Path | None: path to the gmsh *.geo file.
        """
        return self._input_path


    def set_input_file(self, input_path: Path) -> None:
        """Sets the input geo file for gmsh.

        Args:
            input_file (str): Full path

        Raises:
            FileNotFoundError: Not a .geo file
            FileNotFoundError: Geo file does not exist
        """
        if input_path.suffix != '.geo':
            raise FileNotFoundError('Incorrect file type. Must be *.geo.')

        if not input_path.exists():
            raise FileNotFoundError('Specified gmsh geo file does not exist.')

        self._input_path = input_path


    def run(self, input_file: Path | None = None) -> None:
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
        if input_file is not None:
            self.set_input_file(input_file)

        if self._gmsh_app is None:
            raise RuntimeError("Specify the full path to the gmsh app before calling run.")

        if self._input_path is None:
            raise RuntimeError("Specify input *.geo file before running gmsh.")

        self._run_str = f'{self._gmsh_app} {self._input_path}'
        os.system(self._run_str)


    def get_output_path(self) -> Path | None:
        """get_output_path: default return None for gmsh as there is no output
        to be read after the simulation has run. This information is stored in
        the exodus.

        Returns:
            Path | None: Default returns None.
        """
        return None

