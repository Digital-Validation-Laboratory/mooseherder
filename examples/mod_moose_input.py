#==============================================================================
# MODIFY MOOSE INPUT FILE
#
# Author: Lloyd Fletcher
#==============================================================================

from mooseherder import InputModifier

# Read in an input file and extract all variables that are declared before
# the first MOOSE block []
input_file = 'examples/model-mech-test.i'
in_mod = InputModifier()
in_mod.read_vars(input_file)

# Show the dictionary of variables found in the MOOSE file
print('Variables at the top of the MOOSE input file:')
print(in_mod.get_vars())

#  
new_vars = {'n_elem_x':50,'n_elem_y':200,'e_modulus':2e9}
in_mod.mod_vars(new_vars)

save_file = 'examples/model-mod-vars1.i'
in_mod.write_input(save_file)

new_vars = {'n_elem_y':120,'e_modulus':3.3e9,'p_ratio':0.33}
save_file = 'examples/model-mod-vars2.i'
in_mod.write_mod_input(new_vars,save_file)

