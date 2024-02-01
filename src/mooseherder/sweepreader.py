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
        work_dir_files = os.listdir(self._dir_manager.get_run_dir(0))

        key_count = 0
        output_files = list([])
        for ff in work_dir_files:
            if 'output-key' in ff:
                key_count += 1
                output_files = output_files + self.read_output_key(key_count)

        if key_count == 0:
            raise FileNotFoundError("No output key files found.")

        self._output_files = output_files
        return self._output_files


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


