'''
==============================================================================
EXAMPLE 1: MODIFY INPUT SCRIPTS, MOOSE AND GMSH 

Author: Lloyd Fletcher
==============================================================================
'''
from mooseherder import InputModifier

print('------------------------------------------')
print('EXAMPLE 1a: Modify MOOSE input script')
print('------------------------------------------')
moose_input = 'scripts/moose-mech.i'
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

print('------------------------------------------')
print('EXAMPLE 1b: Modify gmsh input script')
print('------------------------------------------')
gmsh_input = 'scripts/gmsh_3d.geo'
gmsh_mod = InputModifier(gmsh_input,'//',';')

print('Variables found the top of the gmsh input file:')
print(gmsh_mod.get_vars())
print()

new_vars = {'p0':0.0018,'p1':0.0012,'p2':0.001}
gmsh_mod.update_vars(new_vars)

print('New variables inserted:')
print(gmsh_mod.get_vars())
print()

gmsh_save = 'scripts/gmsh_3d-mod_vars.geo'
gmsh_mod.write_file(gmsh_save)

print('Modified input script written to:')
print(gmsh_save)
print()

print('EXAMPLES COMPLETE')
print('------------------------------------------')
print()