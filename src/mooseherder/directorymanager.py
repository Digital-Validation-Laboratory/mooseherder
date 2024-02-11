'''
===============================================================================
Directory Manager Class

Authors: Lloyd Fletcher
===============================================================================
'''

import os
import shutil
import json
from typing import Any
from pathlib import Path

class DirectoryManager:
    """ Manages directories for running simulations in parallel.
    """
    def __init__(self, n_dirs: int = 1) -> None:
        """__init__

        Args:
            n_dirs (int, optional): number of directories to be created.
            Defaults to 1.
        """
        self._n_dirs = n_dirs
        self._sub_dir = 'sim-workdir'
        self._base_dir = Path().cwd()
        self._run_dirs = self._set_run_dirs()
        self._output_paths = list([])

    def _set_run_dirs(self) -> list[Path]:

        run_dirs = list([])
        for nn in range(self._n_dirs): # type: ignore
            run_dirs.append(self._base_dir / (self._sub_dir + '-' + str(nn+1)))

        return run_dirs


    def set_sub_dir_name(self, sub_dir_name: str) -> None:
        """set_sub_dir_name:

        Args:
            sub_dir_name (str): string to be used to name the created
            directories
        """
        self._sub_dir = sub_dir_name
        self._run_dirs = self._set_run_dirs()


    def set_base_dir(self, base_dir: Path, clear_old_dirs = False) -> None:
        """set_base_dir:

        Args:
            base_dir (Path): directory in which the new working directories will
                be created.
            clear_old_dirs (bool, optional): deletes previous directories in
                the base directory and their contents if they exist. Defaults
                to False.

        Raises:
            FileExistsError: the selected base directory does no exist.
        """
        if not base_dir.is_dir():
            raise FileExistsError("Specified base directory does not exist.")

        if clear_old_dirs:
            self.clear_dirs()

        self._base_dir = base_dir
        self._run_dirs = self._set_run_dirs()


    def create_dirs(self) -> list[Path]:
        """create_dirs: Creates the specified number of directories based on the sub_dir name.

        Returns:
            list[Path]: list of paths to the created directories
        """
        for rr in self._run_dirs:
            if not rr.is_dir():
                rr.mkdir()

        return self._run_dirs


    def clear_dirs(self) -> None:
        """clear_dirs: deletes all working directories in the base directory
        that have the corresponding sub-directory name and their contents.
        """
        all_dirs = os.listdir(self._base_dir)
        for dd in all_dirs:
            if os.path.isdir(self._base_dir / dd):
                if self._sub_dir in dd:
                    shutil.rmtree(self._base_dir / dd)


    def get_all_run_dirs(self) -> list[Path]:
        """get_all_run_dirs:

        Returns:
            list[Path]: paths to all created directories.
        """
        return self._run_dirs


    def get_run_dir(self, dir_num: int) -> Path:
        """get_run_dir:

        Args:
            dir_num (int): number of the directory path to be retrieved. Can be
                greater than the specified number of directories and will wrap
                appropriately

        Returns:
            Path: path to the directory
        """
        if dir_num >= self._n_dirs:
            dir_num = dir_num % self._n_dirs

        return self._run_dirs[dir_num]


    def set_output_paths(self, output_paths: list[list[Path]]) -> None:
        """set_output_paths:

        Args:
            output_paths (list[list[Path]]): paths to all outputs from the
                variable sweep. Outer list is the variable combination run
                inner list is based on the order the simulations were called.
        """
        self._output_paths = output_paths


    def get_output_paths(self) -> list[list[Path]]:
        """get_output_paths:

        Returns:
            list[list[Path]]: paths to all outputs from the variable sweep.
                Outer list is the variable combination run inner list is based
                on the order the simulations were called.
        """
        return self._output_paths


    def get_output_key_file(self, sweep_iter: int = 1) -> Path:
        """get_output_key_file: gets the path to the output key file created
        during the variable sweep mapping directories to given combinations
        of variables that were run.

        Args:
            sweep_iter (int): number corresponding to the sweep iteration to
                retrieve. Defaults to 1.

        Returns:
            Path: path to the output key file that maps output paths to the
                combinations of variables in the sweep.
        """
        return self._run_dirs[0] / f'output-key-{sweep_iter:d}.json'


    def write_output_key(self, sweep_iter: int) -> None:
        """write_output_key: converts the output paths to strings and saves
        them in json format.

        Args:
            sweep_iter (int): number corresponing to the sweep iteration to
                write. The sweep iteration is used to number the output key
                files.
        """
        str_output = output_paths_to_str(self._output_paths)

        with open(self.get_output_key_file(sweep_iter), "w", encoding='utf-8') as okf:
            json.dump(str_output, okf, indent=4)


    def get_sweep_var_file(self, sweep_iter: int = 1) -> Path:
        """get_sweep_var_file _summary_

        Args:
            sweep_iter (int, optional): _description_. Defaults to 1.

        Returns:
            Path: _description_
        """
        return self._run_dirs[0] / f'sweep-vars-{sweep_iter:d}.json'


    def write_sweep_vars(self,
                         sweep_vars: list[list[dict | None]],
                         sweep_iter: int = 1) -> None:
        """write_sweep_vars _summary_

        Args:
            sweep_vars (list[list[dict[str, Any]]]): _description_
            sweep_iter (int, optional): _description_. Defaults to 1.
        """
        with open(self.get_sweep_var_file(sweep_iter), "w", encoding='utf-8') as okf:
            json.dump(sweep_vars, okf, indent=4)



def output_paths_to_str(output_files: list[list[Path]]) -> list[list[str]]:
    """output_paths_to_str: helper functions for converting the output paths
    to strings to allow them to be saved as json.

    Args:
        output_files (list[list[Path]]):

    Returns:
        list[list[str]]:
    """
    str_output = list([])
    for sim_iter in output_files:
        iter_output = list([])
        for output_path in sim_iter:
            iter_output.append(str(output_path))

        str_output.append(iter_output)

    return str_output


def output_str_to_paths(output_files: list[list[str]]) -> list[list[Path]]:
    """output_str_to_paths _summary_

    Args:
        output_files (list[list[str]]): _description_

    Returns:
        list[list[Path]]: _description_
    """
    str_output = list([])
    for sim_iter in output_files:
        iter_output = list([])
        for output_path in sim_iter:
            iter_output.append(Path(output_path))

        str_output.append(iter_output)

    return str_output
