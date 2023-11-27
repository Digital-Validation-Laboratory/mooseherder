#
# Read the csv outputs from Moose.
#

# Can use pandas to read in csvs. But won't know what the headers are necessarily, may be different for each problem .

import pandas as pd

#filename = '/home/rspencer/mooseherder/examples/creep_mesh_test_dev_out.csv'

def output_csv_reader(filename):
    """Outputs a dict of the last row of the csv output. 

    Args:   
        filename (str): Path to the file to be read.
    """
    data = pd.read_csv(filename,
                   delimiter=',',
                   header= 0)
    
    return data.iloc[-1].to_dict()

#print(output_csv_reader(filename))