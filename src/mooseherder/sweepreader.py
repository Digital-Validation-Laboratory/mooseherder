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
        self._sweep_results = list([])
        self._n_para_read = num_para_read


    def read_output_key(self, sweep_iter: int) -> list[list[Path]]:
        """read_output_key _summary_

        Args:
            sweep_iter (int): _description_

        Returns:
            list[list[Path]]: _description_
        """
        output_key = self._dir_manager.get_output_key_file(sweep_iter)

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
                          var_keys: list,
                          elem_var_blocks: list[int] | None = None) -> dict:
        """read_results_once _summary_

        Args:
            output_file (Path): _description_
            var_keys (list): _description_
            elem_var_blocks (list[int] | None, optional): _description_. Defaults to None.

        Returns:
            dict: _description_
        """
        # Create the
        reader = ExodusReader(output_file)
        read_vars = dict({})

        # Always get the nodal coords and the time vector
        read_vars['coords'] = reader.get_coords()
        read_vars['time'] = reader.get_time()

        # Three cases:
        # 1) nodal data (no block)
        # 2) element data (with block)
        # 3) standard variable string to access anything in exodus
        for ii,kk in enumerate(var_keys):
            if kk in reader.get_node_var_names():
                read_vars[kk] = reader.get_node_data(kk)
            elif (elem_var_blocks is not None) and (kk in reader.get_elem_var_names()):
                read_vars[kk] = reader.get_elem_data(kk,elem_var_blocks[ii])
            elif kk in reader.get_all_var_names():
                read_vars[kk] = reader.get_var(kk)
            else:
                read_vars[kk] = None

        return read_vars


    def read_results_sequential(self, var_keys: list,
                                sweep_iter: int | None = None,
                                elem_var_blocks: list[int] | None = None) -> list[dict]:
        """read_results_sequential _summary_

        Args:
            var_keys (list): _description_
            sweep_iter (int | None, optional): _description_. Defaults to None.
            elem_var_blocks (int | None, optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        self._start_read(sweep_iter)

        self._sweep_results = list([])
        for ll in self._output_files:
            for ff in ll:
                if ff is not None:
                    self._sweep_results.append(
                        self.read_results_once(ff,var_keys,elem_var_blocks))

        return self._sweep_results


    def read_results_para(self,
                          var_keys: list,
                          sweep_iter: int | None = None,
                          elem_var_blocks: list[int] | None = None) -> list[dict]:
        """read_results_para _summary_

        Args:
            var_keys (list): _description_
            sweep_iter (int | None, optional): _description_. Defaults to None.
            elem_var_blocks (int | None, optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """
        self._start_read(sweep_iter)

        with Pool(self._n_para_read) as pool:
            processes = list([])
            for ll in self._output_files:
                for ff in ll:
                    if ff is not None:
                        processes.append(pool.apply_async(
                            self.read_results_once, args=(ff,var_keys,elem_var_blocks)))

            self._sweep_results = [pp.get() for pp in processes]

        return self._sweep_results


    def read_results_para_generic(self,
                                  reader,
                                  sweep_iter: int | None = None) -> list:
        """read_results_para_generic _summary_

        Args:
            reader (_type_): _description_
            sweep_iter (int | None, optional): _description_. Defaults to None.

        Returns:
            list: _description_
        """
        self._start_read(sweep_iter)

        with Pool(self._n_para_read) as pool:
            processes = list([])
            for ff in self._output_files:
                processes.append(pool.apply_async(reader.read, args=(ff,)))

            self._sweep_results = [pp.get() for pp in processes]

        return self._sweep_results


    def _start_read(self,sweep_iter):
        """_start_read _summary_

        Args:
            sweep_iter (_type_): _description_
        """
        if self._output_files == '':
            self._output_files = self.read_output_key(sweep_iter=1)

        if sweep_iter is None:
            self.read_all_output_keys()


