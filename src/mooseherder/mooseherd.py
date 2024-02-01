'''
===============================================================================
MOOSE Herd Class

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
'''
import os
import time
import multiprocessing as mp
from pathlib import Path
from multiprocessing.pool import Pool

from mooseherder.directorymanager import DirectoryManager
from mooseherder.simrunner import SimRunner
from mooseherder.inputmodifier import InputModifier


class MooseHerd:
    """ _summary_
    """
    def __init__(self, sim_runners: list[SimRunner],
                 input_mods: list[InputModifier],
                 dir_manager: DirectoryManager) -> None:
        """__init__ _summary_

        Args:
            sim_runners (list[SimRunner]): _description_
            input_mods (list[InputModifier]): _description_
            dir_manager (DirectoryManager): _description_
        """
        self._runners = sim_runners
        self._modifiers = input_mods
        self._dir_manager = dir_manager

        self._n_para_sims = 2

        self._input_name = 'sim'

        self._keep_all = True

        self._var_sweep = list([])

        self._sweep_iter = 0
        self._sweep_run_time = -1.0

        self._sim_iter = 0
        self._iter_run_time = -1.0


    def set_input_copy_name(self, input_name: str = 'sim') -> None:
        """set_input_copy_name _summary_

        Args:
            input_name (str, optional): _description_. Defaults to 'sim'.
        """
        self._input_name = input_name


    def set_keep_flag(self, keep_all: bool = True) -> None:
        """set_keep_flag _summary_

        Args:
            keep_all (bool, optional): _description_. Defaults to True.
        """
        self._keep_all = keep_all


    def set_num_para_sims(self, n_para: int = 1) -> None:
        """set_num_para_sims _summary_

        Args:
            n_para (int, optional): _description_. Defaults to 1.
        """
        n_para = int(n_para)
        if n_para <= 0:
            n_para = 1
        elif n_para > os.cpu_count(): # type: ignore
            n_para = os.cpu_count() # type: ignore

        if self._n_para_sims != n_para:
            self._n_para_sims = n_para


    def get_sim_iter(self) -> int:
        """get_sim_iter _summary_

        Returns:
            int: _description_
        """
        return self._sim_iter


    def get_sweep_iter(self) -> int:
        """get_sweep_iter _summary_

        Returns:
            int: _description_
        """
        return self._sweep_iter


    def reset_iter_counts(self) -> None:
        """reset_iter_counts _summary_
        """
        self._sim_iter = 0
        self._sweep_iter = 0


    def _get_process_name(self) -> str:
        # Only here for monkey patching
        return mp.current_process().name


    def _get_worker_num(self) -> str:
        """_get_worker_num _summary_

        Returns:
            str: _description_
        """
        name = self._get_process_name()

        # If we are calling this from main we need to set the process number
        if name == 'MainProcess':
            worker_num = '1'
        else:
            worker_num = name.split('-',1)[1]

        # Process number increase keeps increasing so need to update with
        # multiple calls to run_para/seq
        if int(worker_num) > self._n_para_sims:
            worker_num = str((int(worker_num) % self._n_para_sims)+1)

        return worker_num


    def _get_run_num(self, sim_iter: int, worker_num: str) -> str:
        """_get_run_num _summary_

        Args:
            sim_iter (int): _description_
            worker_num (str): _description_

        Returns:
            str: _description_
        """
        if self._keep_all:
            run_num = str(sim_iter+1)
        else: # Set to overwrite based on working directory
            run_num = worker_num

        return run_num


    def _mod_input(self,
                   modifier: InputModifier,
                   mod_vars: dict | None,
                   save_file: Path) -> None:
        """_mod_input _summary_

        Args:
            modifier (InputModifier): _description_
            mod_vars (dict | None): _description_
            save_file (Path): _description_
        """
        if mod_vars is not None:
            modifier.update_vars(mod_vars)
        modifier.write_file(save_file)


    def _run(self, runner: SimRunner, run_file: Path) -> Path | None:
        """_run _summary_

        Args:
            runner (SimRunner): _description_
            run_file (Path): _description_

        Returns:
            Path | None: _description_
        """
        runner.run(run_file)
        return runner.get_output_path()


    def run_once(self, sim_iter: int, var_list: list[dict | None]) -> list[Path | None]:
        """run_once _summary_

        Args:
            sim_iter (int): _description_
            var_list (list[dict  |  None]): _description_

        Returns:
            list[Path | None]: _description_
        """
        iter_start_time = time.perf_counter()

        worker_num = self._get_worker_num()
        run_dir = self._dir_manager.get_run_dir(int(worker_num)-1)
        run_num = self._get_run_num(sim_iter,worker_num)

        # Run all input modifiers and create scripts to run
        run_files = list([])
        for ii,mm in enumerate(self._modifiers):
            ext = mm.get_input_file().suffix
            run_files.append(run_dir / (self._input_name +'-'+run_num+ext))
            self._mod_input(mm,var_list[ii],run_files[ii])

        # Run all runners in order
        output_list = list([])
        for ii,rr in enumerate(self._runners):
            output_list.append(self._run(rr,run_files[ii]))

        self._iter_run_time = time.perf_counter() - iter_start_time

        return output_list


    def _start_sweep(self, var_sweep: list[list[dict | None]]) -> float:
        """_start_sweep _summary_

        Args:
            var_sweep (list[list[dict  |  None]]): _description_

        Returns:
            float: _description_
        """
        self._var_sweep = var_sweep

        if not self._keep_all:
            self.reset_iter_counts()
            self._dir_manager.clear_dirs()
            self._dir_manager.create_dirs()

        return time.perf_counter()


    def _end_sweep(self, start_sweep_time: float,
                   output_files: list[list[Path]]) -> None:
        """_end_sweep _summary_

        Args:
            start_sweep_time (float): _description_
        """
        self._sweep_run_time = time.perf_counter() - start_sweep_time

        self._sweep_iter += 1
        self._sim_iter += len(self._var_sweep)

        self._dir_manager.set_output_paths(output_files)
        self._dir_manager.write_output_key(self._sweep_iter)


    def run_sequential(self, var_sweep: list[list[dict | None]]) -> list[list[Path | None]]:
        """run_sequential _summary_

        Args:
            var_sweep (list[list[dict  |  None]]): _description_

        Returns:
            list[list[Path | None]]: _description_
        """
        start_sweep_time = self._start_sweep(var_sweep)

        output_files = list([])

        ii = self._sim_iter
        for vv in var_sweep:
            output_files.append(self.run_once(ii,vv))
            ii += 1


        self._end_sweep(start_sweep_time,output_files)

        return output_files


    def run_para(self, var_sweep: list[list[dict | None]]) -> list[list[Path | None]]:
        """run_para _summary_

        Args:
            var_sweep (list[list[dict  |  None]]): _description_

        Returns:
            list[list[Path | None]]: _description_
        """
        sweep_start_time = self._start_sweep(var_sweep)

        with Pool(self._n_para_sims) as pool:
            processes = list([])

            ii = self._sim_iter
            for vv in var_sweep:
                processes.append(pool.apply_async(self.run_once, args=(ii,vv)))
                ii += 1

            output_files = [pp.get() for pp in processes]

        self._end_sweep(sweep_start_time, output_files)

        return output_files


    def get_sweep_time(self) -> float:
        """get_sweep_time _summary_

        Returns:
            float: _description_
        """
        return self._sweep_run_time


    def get_iter_time(self) -> float:
        """get_iter_time _summary_

        Returns:
            float: _description_
        """
        return self._iter_run_time

