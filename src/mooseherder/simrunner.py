"""
===============================================================================
Sim Runner Abstract Base Class

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
"""
from abc import ABC, abstractmethod

"""
TODO: Runner has
- An app path - must exist!
- An input file and path - must exist!
- A funcion to assemble the command string
- A run function
"""


class SimRunner(ABC):
    @property
    def input_file(self):
        return self._input_file

    @abstractmethod
    def run(self, input_file=None) -> None:
        pass
