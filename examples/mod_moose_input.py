#==============================================================================
# MODIFY MOOSE INPUT FILE
#
# Author: Lloyd Fletcher
#==============================================================================

import os

class MooseModifier:
    def __init__(self):
        self.input_file = ''

    def read_vars(self,input_file):
        self.input_file = input_file
        with open(input_file,'r') as data_file:
            all_lines = data_file.readlines()

            self.vars = dict()
            for ss in all_lines:
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
                        self.vars[ss.split('=', 1)[0]] = float(ss.split('=', 1)[1])

input_file = 'examples/model-mech-test.i'
mmod = MooseModifier()
mmod.read_vars(input_file)

print(mmod.vars)


