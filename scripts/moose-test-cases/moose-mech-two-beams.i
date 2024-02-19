#
# Multiple submesh setup with two cantilevers side by side
# https://mooseframework.inl.gov/modules/tensor_mechanics/tutorials/introduction/step04.html
#

[GlobalParams]
  displacements = 'disp_x disp_y'
[]

[Mesh]
  [generated1]
    type = GeneratedMeshGenerator
    dim = 2
    nx = 10
    ny = 100
    xmin = -0.6
    xmax = -0.1
    ymax = 5
    #bias_y = 0.9
    boundary_name_prefix = pillar1
  []
  [generated2]
    type = GeneratedMeshGenerator
    dim = 2
    nx = 10
    ny = 100
    xmin = 0.1
    xmax = 0.6
    ymax = 5
    #bias_y = 0.9
    boundary_name_prefix = pillar2
    boundary_id_offset = 4
  []
  [collect_meshes]
    type = MeshCollectionGenerator
    inputs = 'generated1 generated2'
  []
[]

[Modules/TensorMechanics/Master]
  [all]
    add_variables = true
    strain = FINITE
    generate_output = 'vonmises_stress strain_xx strain_yy strain_zz strain_xy'
  []
[]

[BCs]
  [bottom_x]
    type = DirichletBC
    variable = disp_x
    boundary = 'pillar1_bottom pillar2_bottom'
    value = 0
  []
  [bottom_y]
    type = DirichletBC
    variable = disp_y
    boundary = 'pillar1_bottom pillar2_bottom'
    value = 0
  []
  [Pressure]
    [sides]
      boundary = 'pillar1_left pillar2_right'
      function = 1e4*t
    []
  []
[]

[Materials]
  [elasticity]
    type = ComputeIsotropicElasticityTensor
    youngs_modulus = 1e9
    poissons_ratio = 0.3
  []
  # we anticipate large deformation
  [stress]
    type = ComputeFiniteStrainElasticStress
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  line_search = none
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
  end_time = 5
  dt = 0.5
  [Predictor]
    type = SimplePredictor
    scale = 1
  []
[]

[Postprocessors]
  [max]
    type = NodalExtremeValue
    variable = disp_x
    value_type = max
  []
[]

[Outputs]
  exodus = true
  csv = true
  perf_graph = false
[]