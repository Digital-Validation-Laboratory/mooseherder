'''
===============================================================================
SweepReader Class

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
'''

import os
import json
import multiprocessing as mp
from pathlib import Path
from multiprocessing.pool import Pool
from mooseherder.directorymanager import DirectoryManager
from mooseherder.exodusreader import ExodusReader


class SweepReader:

    def __init__(self, dir_manager: DirectoryManager) -> None:

        self._dir_manager = dir_manager


    def get_output_key_file(self, sweep_iter = None) -> Path:

        if sweep_iter is None:
            sweep_iter = self._sweep_iter

        return self._dir_manager.get_run_dir(0) / f'output-key-{sweep_iter:d}.json'




    def _write_output_key(self) -> None:

        str_output = self._output_paths_to_str()

        with open(self.get_output_key_file(), 'w', encoding='utf-8') as okf:
            json.dump(str_output, okf, indent=4)


    def _output_paths_to_str(self) -> list[list[str]]:

        str_output = list([])
        for sim_iter in self._output_files:
            iter_output = list([])
            for output_path in sim_iter:
                iter_output.append(str(output_path))

            str_output.append(iter_output)

        return str_output


    def read_output_key(self, sweep_iter = None) -> list[list[str]]:

        with open(self.get_output_key_file(sweep_iter), 'r', encoding='utf-8') as okf:
            output_files = json.load(okf)

        return output_files


    def read_all_output_keys(self) -> list[list[Path]]:

        work_dir_files = os.listdir(self._run_dirs[0])

        key_count = 0
        for ff in work_dir_files:
            if 'output-key' in ff:
                key_count += 1

        if key_count == 0:
            raise FileNotFoundError("No output key files found.")

        output_files = list()
        for kk in range(key_count):
            output_files = output_files + self.read_output_key(kk+1)

        self._output_files = output_files
        self._sweep_iter = len(self._output_files)

        return self._output_files

    def get_output_files(self) -> list[list[Path]]:


        return self._output_files


    def read_results_once(self, output_file: Path, var_keys: list, elem_var_blocks = None) -> dict:

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
            elif (elem_var_blocks != None) and (kk in reader.get_elem_var_names()):
                read_vars[kk] = reader.get_elem_data(kk,elem_var_blocks[ii])
            elif kk in reader.get_all_var_names():
                read_vars[kk] = reader.get_var(kk)
            else:
                read_vars[kk] = None

        return read_vars


    def read_results_sequential(self, var_keys: list, sweep_iter = None, elem_var_blocks=None) -> list:

        self._start_read(sweep_iter)

        self._sweep_results = list()
        for ff in self._output_files:
            self._sweep_results.append(
                self.read_results_once(ff,var_keys,elem_var_blocks))

        return self._sweep_results


    def read_results_para(self, var_keys: list, sweep_iter = None, elem_var_blocks = None) -> list:

        self._start_read(sweep_iter)

        with Pool(self._n_moose) as pool:
            processes = list()
            for ff in self._output_files:
                processes.append(pool.apply_async(
                    self.read_results_once, args=(ff,var_keys,elem_var_blocks)))

            self._sweep_results = [pp.get() for pp in processes]

        return self._sweep_results


    def read_results_para_generic(self, reader) -> list:

        #self._start_read(sweep_iter)

        with Pool(self._n_moose) as pool:
            processes = list()
            for ff in self._output_files:
                processes.append(pool.apply_async(reader.read, args=(ff,)))

            self._sweep_results = [pp.get() for pp in processes]

        return self._sweep_results


    def _start_read(self,sweep_iter):

        if self._output_files == '':
            self._output_files = self.read_output_key(sweep_iter=1)

        if sweep_iter == None:
            self.read_all_output_keys()


