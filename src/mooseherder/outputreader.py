#
# Read the csv outputs from Moose.
#

# Can use pandas to read in csvs. But won't know what the headers are necessarily, may be different for each problem .

import pandas as pd
import os

class OutputCSVReader():
    """Class to support reading in of csv files in parallels
    An instance of this class will be passed to the mooseherder 
    which will call read() in paralle;.
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
            output =None
        return output


