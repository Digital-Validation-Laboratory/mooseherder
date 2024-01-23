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
    def get_input_file(self) -> Path | None:
        """get_input_path
        """


    @abstractmethod
    def set_input_file(self, input_path: Path) -> None:
        """set_input_file
        """


    @abstractmethod
    def run(self, input_file: Path | None = None) -> None:
        """run _summary_
        """

    @abstractmethod
    def get_output_path(self) -> Path | None:
        """get_output_path _summary_
        """

