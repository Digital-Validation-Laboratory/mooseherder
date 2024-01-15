'''
===============================================================================
Sim Runner Abstract Base Class

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
'''
from abc import ABC, abstractmethod

'''
TODO:
- Runner has an input file property that must exist
- Runner keeps the file name and the path to the file
'''

class SimRunner(ABC):


    @abstractmethod
    def run(self, input_file = '') -> None:
        pass
