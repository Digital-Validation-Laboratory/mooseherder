
'''
===============================================================================
MOOSE Config Class

Authors: Lloyd Fletcher
===============================================================================
'''
from typing import Self
import json
from pathlib import Path


class MooseConfig:
    """ _summary_
    """
    def __init__(self, config: dict[str,Path | str] | None = None) -> None:
        """__init__ _summary_

        Args:
            config (dict[str,Path  |  str] | None, optional): _description_. Defaults to None.
        """
        self._required_keys = ['main_path','app_path','app_name']

        if config is not None:
            self._check_config_valid(config)

        self._config = config


    def get_config(self) -> dict[str,Path | str]:
        """get_config _summary_

        Returns:
            dict[str,Path | str] | None: _description_
        """
        self._check_config_valid(self._config)
        return self._config # type: ignore


    def _check_config_valid(self, config: dict[str,Path | str] | None = None) -> None:
        """_check_config_valid _summary_

        Args:
            config (dict[str,Path  |  str] | None, optional): _description_. Defaults to None.

        Raises:
            MooseConfigError: _description_
        """
        if config is None:
            raise MooseConfigError(
                'Config dictionary must be initialised, load config file first.')

        for kk in self._required_keys:
            if kk not in config:
                raise MooseConfigError(
                    f'Config dictionary must contain all keys: {self._required_keys}')

        if not config['main_path'].is_dir(): # type: ignore
            raise MooseConfigError(
                "Main path to MOOSE does not exist. Check path at key 'main_path'.")

        if not config['app_path'].is_dir(): # type: ignore
            raise MooseConfigError(
                "MOOSE app path does not exist. Check path at key: 'app_path'.")


    def _convert_path_to_str(self, in_config: dict[str,Path | str] | None
                             ) -> dict[str,str] | None:
        """_convert_path_to_str _summary_

        Args:
            in_config (dict[str,Path  |  str] | None): _description_

        Returns:
            dict[str,str] | None: _description_
        """
        if in_config is None:
            return None

        conv_config = dict({})
        for kk in in_config:
            conv_config[kk] = str(in_config[kk])

        return conv_config


    def _convert_str_to_path(self, in_config: dict[str,str] | None = None
                             ) -> dict[str, Path | str] | None:
        """_convert_str_to_path _summary_

        Args:
            in_config (dict[str,str] | None, optional): _description_. Defaults to None.

        Returns:
            dict[str, Path | str] | None: _description_
        """
        if in_config is None:
            return None

        conv_config = dict({})
        for kk in in_config:
            if 'path' in kk:
                conv_config[kk] = Path(in_config[kk])
            else:
                conv_config[kk] = in_config[kk]

        return conv_config


    def read_config(self, config_path: Path) -> Self:
        """read_config _summary_

        Args:
            config_path (Path): _description_

        Raises:
            FileNotFoundError: _description_

        Returns:
            Self: _description_
        """
        if not config_path.is_file():
            raise FileNotFoundError(
                f'MOOSE config file at {str(config_path)} does not exist.')

        with open(config_path, 'r', encoding='utf-8') as cf:
            config_strs = json.load(cf)
            config_paths = self._convert_str_to_path(config_strs)

        self._check_config_valid(config_paths)

        self._config = config_paths
        return self


    def save_config(self,config_path: Path) -> None:
        """save_config _summary_

        Args:
            config_path (Path): _description_

        Raises:
            FileNotFoundError: _description_
        """
        if not config_path.parent.is_dir():
            raise FileNotFoundError('Parent path to save config file does not exist.')

        with open(config_path, 'w', encoding='utf-8') as cf:
            config_strs = self._convert_path_to_str(self._config)
            json.dump(config_strs, cf, indent=4)


class MooseConfigError(Exception):
    """MooseConfigError _summary_

    Args:
        Exception (_type_): _description_
    """
