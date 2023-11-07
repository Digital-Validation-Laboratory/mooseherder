#==============================================================================
# MODIFY MOOSE INPUT FILE
#
# Author: Lloyd Fletcher
#==============================================================================

import os

class InputModifier:
    def __init__(self):
        self._vars = dict()
        self._input_file = ''
        self._input_lines = list()

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

    def mod_vars(self):
        '''
        TODO
        '''
        # Need to update the variables dictionary and the strings in the file
        for kk in self._vars.keys():
            print(kk)

    def write_input(self,write_file):
        '''
        TODO
        '''
        with open(write_file,'w') as in_file:
            in_file.writelines(self.input_lines)



input_file = 'examples/model-mech-test.i'
in_mod = InputModifier()
in_mod.read_vars(input_file)
print('Variables at the top of the MOOSE input file:')
print(in_mod._vars)
print()

in_mod.mod_vars()

print(in_mod._vars['n_elem_x'])
