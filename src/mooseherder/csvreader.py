'''
==============================================================================
CSVReader Class

Author: Rory Spencer, Lloyd Fletcher
==============================================================================
'''
import pandas as pd
import os

class CSVReader():
    """Class to support reading in of csv files in parallel.
    An instance of this class will be passed to the mooseherder 
    which will call read() in parallel. 
    """

    def __init__(self):
        self._data_type = 'csv'
        self._extension = 'csv'
    
    def read(self,filename):
        """Read file

        Args:
            filename (str): Read file at path filename

        Returns:
            dict : Dict of the moose csv outputs at the last timestep.
        """
            
        try:
            data = pd.read_csv(filename,
                        delimiter=',',
                        header= 0)

            output = data.iloc[-1].to_dict()
        except(FileNotFoundError):
            print('Likely model did not run, setting data as none.')
            output = None
        return output


