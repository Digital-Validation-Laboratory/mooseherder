#Here's the force reaction
# If you're using the AD kernels it should be ADSidesetReaction
# Direction gives your x, y, z
# Boundary is your BC
# Stress tensor should match the ones set up with tensor mechanics master (either stress or cauchy_stress generally )

[Postprocessors]
  [./react_y]
    type = SidesetReaction
    direction = '0 1 0'
    stress_tensor = stress
    boundary = 'Btm-BC'
  [../]
[]
