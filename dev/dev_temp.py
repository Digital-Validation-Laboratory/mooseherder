'''
==============================================================================
EXAMPLE 1: MODIFY INPUT SCRIPTS, MOOSE AND GMSH 

Author: Lloyd Fletcher
==============================================================================
'''
from mooseherder import InputModifier

moose_input = 'tests/moose/moose-vartest.i'
moose_mod = InputModifier(moose_input,comment_char='#',end_char='')

print('Variables found the top of the MOOSE input file:')
print(moose_mod.get_vars())
print()

new_vars = {'n_elem_y':120,'e_modulus':3.3e9,'p_ratio':0.33}
moose_mod.update_vars(new_vars)

print('New variables inserted:')
print(moose_mod.get_vars())
print()

moose_save = 'scripts/moose-mech_mod-vars.i'
moose_mod.write_file(moose_save)

print('Modified input script written to:')
print(moose_save)
print()
