'''
===============================================================================
SweepReader Class

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
'''

import os
import json
from pathlib import Path
from multiprocessing.pool import Pool
from mooseherder.directorymanager import DirectoryManager
import mooseherder.directorymanager as dm
from mooseherder.exodusreader import ExodusReader
from mooseherder.simdata import SimData, SimReadConfig


class SweepReader:
    """ _summary_
    """
    def __init__(self,
                 dir_manager: DirectoryManager,
                 num_para_read: int = 1) -> None:
        """__init__ _summary_

        Args:
            dir_manager (DirectoryManager): _description_
            num_para_read (int, optional): _description_. Defaults to 1.
        """
        self._dir_manager = dir_manager
        self._output_files = list([])
        self._n_para_read = num_para_read


    def read_output_key(self, sweep_iter: int) -> list[list[Path]]:
        """read_output_key _summary_

        Args:
            sweep_iter (int): _description_

        Returns:
            list[list[Path]]: _description_
        """
        output_key = self._dir_manager.get_output_key_file(sweep_iter)
        if not output_key.is_file():
            raise FileNotFoundError(f'Output key file for sweep iteration {sweep_iter} not found at path: {output_key}')

        with open(output_key, 'r', encoding='utf-8') as okf:
            output_files = json.load(okf)

        return dm.output_str_to_paths(output_files)


    def read_all_output_keys(self) -> list[list[Path]]:
        """read_all_output_keys _summary_

        Raises:
            FileNotFoundError: _description_

        Returns:
            list[list[Path]]: _description_
        """
        output_paths = self._find_files_by_str(self._dir_manager.get_output_key_tag(),
                                               self._dir_manager.get_run_dir(0))

        if len(output_paths) == 0:
            raise FileNotFoundError("No output key json files found.")

        output_files = list([])
        for ii,_ in enumerate(output_paths):
            output_files = output_files + self.read_output_key(ii+1)

        self._output_files = output_files
        return self._output_files


    def read_sweep_var_file(self, sweep_iter: int = 1) -> list[list[dict | None]]:
        """read_sweep_var_file _summary_

        Args:
            sweep_iter (int, optional): _description_. Defaults to 1.

        Raises:
            FileNotFoundError: _description_

        Returns:
            list[list[dict | None]]: _description_
        """
        sweep_var_file = self._dir_manager.get_sweep_var_file(sweep_iter)
        if not sweep_var_file.is_file():
            raise FileNotFoundError(f'Sweep variable file for sweep iteration {sweep_iter} not found at path: {sweep_var_file}')

        with open(sweep_var_file, 'r', encoding='utf-8') as svf:
            sweep_vars = json.load(svf)

        return sweep_vars


    def read_all_sweep_var_files(self) -> list[list[dict | None]]:
        """read_all_sweep_var_files _summary_

        Raises:
            FileNotFoundError: _description_

        Returns:
            list[list[dict | None]]: _description_
        """
        sweep_var_paths = self._find_files_by_str(self._dir_manager.get_sweep_var_tag(),
                                                  self._dir_manager.get_run_dir(0))

        if len(sweep_var_paths) == 0:
            raise FileNotFoundError("No sweep variable json files found.")

        sweep_vars = list([])
        for ii,_ in enumerate(sweep_var_paths):
            sweep_vars = sweep_vars  + self.read_sweep_var_file(ii+1)

        return sweep_vars


    def _find_files_by_str(self, search_str: str, search_path: Path) -> list[Path]:
        """_find_files_by_str _summary_

        Args:
            search_str (str): _description_
            search_path (Path): _description_

        Returns:
            list[Path]: _description_
        """
        found_files = list([])

        all_files = os.listdir(search_path)

        for ff in all_files:
            if search_str in ff:
                found_files.append(Path(ff))

        return found_files


    def get_output_files(self) -> list[list[Path]]:
        """get_output_files _summary_

        Returns:
            list[list[Path]]: _description_
        """
        return self._output_files


    def read_results_once(self,
                          output_file: Path,
                          read_config: SimReadConfig | None = None) -> SimData:
        """read_results_once _summary_

        Args:
            output_file (Path): _description_
            read_config (SimReadConfig | None): _description_

        Returns:
            SimData: _description_
        """
        reader = ExodusReader(output_file)

        if read_config is None:
            return reader.read_all_sim_data()

        return reader.read_sim_data(read_config)


    def read_results_sequential(self,
                                sweep_iter: int | None = None,
                                read_config: SimReadConfig | None = None) -> list[SimData]:
        """read_results_sequential _summary_

        Args:
            sweep_iter (int | None, optional): _description_. Defaults to None.
            read_config (SimReadConfig | None, optional): _description_. Defaults to None.

        Returns:
            list[SimData]: _description_
        """
        self._start_read_output_keys(sweep_iter)

        sweep_results = list([])
        for ll in self._output_files:
            for ff in ll:
                if ff is not None:
                    sweep_results.append(self.read_results_once(ff,read_config))

        return sweep_results


    def read_results_para(self,
                          sweep_iter: int | None = None,
                          read_config: SimReadConfig | None = None) -> list[SimData]:
        """read_results_para _summary_

        Args:
            sweep_iter (int | None, optional): _description_. Defaults to None.
            read_config (SimReadConfig | None, optional): _description_. Defaults to None.

        Returns:
            list[SimData]: _description_
        """
        self._start_read_output_keys(sweep_iter)

        with Pool(self._n_para_read) as pool:
            processes = list([])
            for ll in self._output_files:
                for ff in ll:
                    if ff is not None:
                        processes.append(pool.apply_async(
                            self.read_results_once, args=(ff,read_config)))

            sweep_results = [pp.get() for pp in processes]

        return sweep_results


    def _start_read_output_keys(self, sweep_iter: int | None):
        """_start_read _summary_

        Args:
            sweep_iter (_type_): _description_
        """
        if self._output_files == '':
            self._output_files = self.read_output_key(sweep_iter=1)

        if sweep_iter is None:
            self.read_all_output_keys()


