"""
===============================================================================
OutputReader Abstract Base Class

Authors: Lloyd Fletcher
===============================================================================
"""
from abc import ABC, abstractmethod
from pathlib import Path

class OutputReader(ABC):
    """OutputReader: Abstract Base Class
    """
    @abstractmethod
    def read_output(self) -> None:
        pass

