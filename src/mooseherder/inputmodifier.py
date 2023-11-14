'''
===============================================================================
MOOSE Input Modifier Class

Used to modify variables in MOOSE files for parametric sweeps. Assumes that 
variables are declared before the first MOOSE block starting with []. Will 
ignore any characters occuring after a '#' is found as a comment. Looks for the
'=' to determine if a variable is found. 

Once variables have been modified by the user by passing in a dictionary of 
new variables the MOOSE input can be written to file.

Author: Lloyd Fletcher
===============================================================================
'''

import os

class InputModifier:
    def __init__(self,input_file):
        '''
        TODO
        '''
        self._vars = dict()
        self._input_file = ''
        self._input_lines = list()
        self.read_vars(input_file)

    def read_vars(self,input_file):
        '''
        TODO
        '''
        self._input_file = input_file
        with open(input_file,'r') as in_file:
            self._input_lines = in_file.readlines()

            for ii,ss in enumerate(self._input_lines):
                ss = ss.strip()
                ss = ss.replace(' ','') 
                if ss:
                    # If we find a MOOSE block stop looking for variables
                    if ss[0] == '[':
                        break
                    
                    # Remove anything that is a comment
                    if ss.find('#') >= 0:
                        ss = ss.split('#', 1)[0]

                    # Anything left with an equals sign is a variable
                    if ss.find('=') >= 0:
                        self._vars[ss.split('=', 1)[0]] = [float(ss.split('=', 1)[1]), ii]

    def mod_vars(self,in_vars):
        '''
        TODO
        '''
        # Need to update the variables dictionary and the strings in the file
        for kk in in_vars.keys():
            try:
                self._vars[kk] = [in_vars[kk],self._vars[kk][1]]
                edit_line = self._input_lines[self._vars[kk][1]]

                # Check for comments and the equals sign
                edit_line = edit_line[:edit_line.find('=')+1] + ' ' + \
                            str(in_vars[kk]) + ' ' + \
                            edit_line[edit_line.find('#'):]
                self._input_lines[self._vars[kk][1]] = edit_line

            except KeyError as e:
                print("Variable not found for: ", e)
        
    def get_vars(self):
        '''
        TODO
        '''
        return self._vars

    def write_input(self,write_file):
        '''
        TODO
        '''
        with open(write_file,'w') as in_file:
            in_file.writelines(self._input_lines)

    def write_mod_input(self,in_vars,in_file):
        '''
        TODO
        '''
        self.mod_vars(in_vars)
        self.write_input(in_file)
