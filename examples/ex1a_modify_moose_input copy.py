'''
==============================================================================
EXAMPLE 1a: MODIFY INPUT SCRIPT FOR MOOSE 

Author: Lloyd Fletcher
==============================================================================
'''
from mooseherder import InputModifier

print('------------------------------------------')
print('EXAMPLE 1a: Modify MOOSE input script')
print('------------------------------------------')
moose_input = 'scripts/moose/moose-mech-simple.i'
moose_mod = InputModifier(moose_input,comment_char='#',end_char='')

print('Variables found the top of the MOOSE input file:')
print(moose_mod.get_vars())
print()

new_vars = {'n_elem_y':40,'e_modulus':3.3e9}
moose_mod.update_vars(new_vars)

print('New variables inserted:')
print(moose_mod.get_vars())
print()

moose_save = 'scripts/moose-mech_mod-vars.i'
moose_mod.write_file(moose_save)

print('Modified input script written to:')
print(moose_save)
print()

print('EXAMPLE COMPLETE')
print('------------------------------------------')
print()