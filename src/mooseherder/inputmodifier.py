"""
===============================================================================
Generic Input Modifier Class

Used to modify variables in generic text-based input files.

Once variables have been modified by the user by passing in a dictionary of 
new variables the MOOSE input can be written to file.

Variable definition blocks should begin #comment character#* and end 
#comment character#**, i.e. //_* and //**

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
"""

import os

class InputModifier:
    """
    Class to store all information related to an input file.
    """
    def __init__(self,input_file,comment_char='#',end_char=''):
        """ Initialise the class reading in the input file.

        Args:
            input_file (string): Path to the input text file.
            comment_char (string): character(s) describing what a comment looks like in the file. 
            end_char (string): character (if any) that ends a line, i.e. ; 
        """
        self._vars = dict()
        self._input_file = input_file
        with open(self._input_file,'r') as in_file:
            self._input_lines = in_file.readlines()
        self.comment_char = comment_char
        self.end_char = end_char
        self.find_vars()
        self.read_vars()
        
    def read_vars(self):
        """ Reads the variables in the file 
        """
        for ii,ss in enumerate(self._input_lines[self.var_start+1:self.var_end]):
            ss = ss.strip()
            ss = ss.replace(' ','') 
            ss = ss.replace(self.end_char,'') 
            ss = ss.split(self.comment_char)[0]  # Remove trailing comments should they exist
            if ss:
                # Anything left with an equals sign is a variable
                if ss.find('=') >= 0:
                    self._vars[ss.split('=', 1)[0]] = float(ss.split('=', 1)[1])


    def find_vars(self):
        """ Find what lines the variables are defined on.
        """
        self.var_start = 0
        self.var_end = -1
        start_string = self.comment_char+'_*'
        end_string = self.comment_char+'**'
        with open(self._input_file,'r') as in_file:
            for index,line in enumerate(in_file):
                if start_string in line:
                    self.var_start = index
                if end_string in line:
                    self.var_end = index
                    break

    def update_vars(self,new_vars):
        """Updates the dict of varaibles

        Args:
            new_vars (dict): New values for the variables. Must have the same keys!

        Raises:
            KeyError: Keys don't match between existing and updated dicts.
        """
        # Check keys
        if self._vars.keys() == new_vars.keys():
            # Update away
            self._vars = new_vars
        else:
            raise KeyError('Dictionary Key Mismatch')


    def write_file(self,wfile):
        """Write the input file.

        Args:
            wfile (str): Path to where the file should be written.
        """
        
        #Prep the values to write
        keys = list(self._vars.keys())
        values = list(self._vars.values())

        #Write file
        with open(wfile,'w') as out_file:
            for index,line in enumerate(self._input_lines):
                #If it's in the variables block, overwrite
                if index > self.var_start and index < self.var_end:
                    current_var = index-self.var_start-1
                    try:
                        write_string = '{} = {}{}\n'.format(keys[current_var],values[current_var],self.end_char)
                        out_file.write(write_string)
                    except(IndexError):
                        # TODO: Probably should avoid printing to console inside a class
                        print('All available parameters written. Check for commented out parameters in the input.')
                    continue
                else:
                    out_file.write(line)

    def get_vars(self):
        '''
        TODO
        '''
        return self._vars
    
    def get_var_keys(self):
        """Return the keys of the variable dict
        """

        return list(self._vars.keys())

        

