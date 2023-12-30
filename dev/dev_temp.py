'''
==============================================================================
EXAMPLE 1b: MODIFY INPUT SCRIPT FOR GMSH 

Author: Lloyd Fletcher
==============================================================================
'''
from mooseherder import InputModifier

print('------------------------------------------')
print('EXAMPLE 1b: Modify gmsh input script')
print('------------------------------------------')
gmsh_input = 'tests/gmsh/gmsh_vartest.geo'
gmsh_mod = InputModifier(gmsh_input,'//',';')

print('Variables found the top of the gmsh input file:')
print(gmsh_mod.get_vars())
print()

new_vars = {'p0':0.0018,'p1':0.0012,'p2':0.001}
gmsh_mod.update_vars(new_vars)

print('New variables inserted:')
print(gmsh_mod.get_vars())
print()

gmsh_save = 'tests/gmsh/gmsh_vartest-mod.geo'
gmsh_mod.write_file(gmsh_save)

print('Modified input script written to:')
print(gmsh_save)
print()

print('EXAMPLE COMPLETE')
print('------------------------------------------')
print()