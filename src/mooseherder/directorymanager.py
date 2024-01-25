'''
===============================================================================
Directory Manager Class

Authors: Lloyd Fletcher
===============================================================================
'''

import os
import shutil
import json
from pathlib import Path

class DirectoryManager:
    """ _summary_
    """
    def __init__(self, n_dirs: int = 1) -> None:
        """__init__ _summary_

        Args:
            n_dirs (int, optional): _description_. Defaults to 1.
        """
        self._n_dirs = n_dirs
        self._sub_dir = 'sim-workdir'
        self._base_dir = Path().cwd()
        self._run_dirs = list([])


    def set_sub_dir_name(self, sub_dir_name: str) -> None:
        """set_sub_dir_name _summary_

        Args:
            sub_dir_name (str): _description_
        """
        self._sub_dir = sub_dir_name


    def set_base_dir(self, base_dir: Path, clear_old_dirs = False) -> None:
        """set_base_dir _summary_

        Args:
            base_dir (Path): _description_
            clear_old_dirs (bool, optional): _description_. Defaults to False.

        Raises:
            FileExistsError: _description_
        """
        if not base_dir.is_dir():
            raise FileExistsError("Specified base directory does not exist.")

        if clear_old_dirs:
            self.clear_dirs()

        self._base_dir = base_dir


    def create_dirs(self) -> list[Path]:
        """create_dirs _summary_

        Returns:
            list[Path]: _description_
        """
        self._run_dirs = list([])

        for nn in range(self._n_dirs): # type: ignore
            run_sub_dir = self._base_dir / (self._sub_dir + '-' + str(nn+1))

            if not run_sub_dir.is_dir():
                run_sub_dir.mkdir()

            self._run_dirs.append(run_sub_dir)

        return self._run_dirs


    def clear_dirs(self) -> None:
        """clear_dirs _summary_
        """
        all_dirs = os.listdir(self._base_dir)
        for dd in all_dirs:
            if os.path.isdir(self._base_dir / dd):
                if self._sub_dir in dd:
                    shutil.rmtree(self._base_dir / dd)


    def get_all_run_dirs(self) -> list[Path]:
        """get_all_run_dirs _summary_

        Returns:
            list[Path]: _description_
        """
        return self._run_dirs


    def get_run_dir(self, dir_num: int) -> Path:
        """get_run_dir _summary_

        Args:
            dir_num (int): _description_

        Returns:
            Path: _description_
        """
        if dir_num >= self._n_dirs:
            dir_num = dir_num % 2

        return self._run_dirs[dir_num]


    def get_output_key_file(self, sweep_iter: int) -> Path:
        return self._run_dirs[0] / f'output-key-{sweep_iter:d}.json'


    def write_output_key(self) -> None:

        str_output = self.output_paths_to_str()

        with open(self.get_output_key_file(), 'w', encoding='utf-8') as okf:
            json.dump(str_output, okf, indent=4)


    def output_paths_to_str(self, output_files: list[list[Path]]) -> list[list[str]]:

        str_output = list([])
        for sim_iter in output_files:
            iter_output = list([])
            for output_path in sim_iter:
                iter_output.append(str(output_path))

            str_output.append(iter_output)

        return str_output
