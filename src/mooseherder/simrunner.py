"""
===============================================================================
Sim Runner Abstract Base Class

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
"""
from abc import ABC, abstractmethod
from pathlib import Path

class SimRunner(ABC):
    """SimRunner: Abstract Base Class for
    """
    @abstractmethod
    def get_input_path(self) -> Path | None:
        """get_input_path

        Returns:
            Path: _description_
        """
        pass

    @abstractmethod
    def run(self, input_file: Path | None = None) -> None:
        """run _summary_

        Args:
            input_file (Path or None, optional): _description_. Defaults to None.
        """
        pass
