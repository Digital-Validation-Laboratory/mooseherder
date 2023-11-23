#
# Working version of a creep model with realistic-ish material model.
# This creep model isn't normalised so the power law causes big changes to A parameter.
#
[GlobalParams]
    displacements = 'disp_x disp_y disp_z'
  []
  
  [Mesh]
    type = FileMesh
    file = '/home/rspencer/mooseherder/data/test_mesh.msh'
  []
  
  [Modules/TensorMechanics/Master]
    [./all]
      strain = FINITE
      incremental = true
      add_variables = true
      generate_output = 'stress_yy elastic_strain_yy creep_strain_yy stress_xx plastic_strain_yy'
    [../]
  []
  
  [Functions]
    [./top_pull]
      type = PiecewiseLinear
      x = '  0   0.5  100   '
      y = '-0E6 -50E6  -50E6' 
    [../]
  
    [./dts]
      type = PiecewiseLinear
      x = '0        0.5    1.0 100'
      y = '0.02  0.02  1  1'
    [../]

    [./swift]
        type = ParsedFunction
        expression = '400E6*(1E-3 +x)^0.1'
    [../]
  []
  
  [BCs]
    [./u_top_pull]
      type = Pressure
      variable = disp_y
      boundary = Top-BC
      factor = 1.7
      function = top_pull
    [../]
    [./u_bottom_fix]
      type = DirichletBC
      variable = disp_y
      boundary = Btm-BC
      value = 0.0
    [../]
    [./u_yz_fix]
      type = DirichletBC
      variable = disp_x
      boundary = Mid-BC
      value = 0.0
    [../]
    [./u_xy_fix]
      type = DirichletBC
      variable = disp_z
      boundary = Bck-BC
      value = 0.0
    [../]
  []
  
  [Materials]
    [./elasticity_tensor]
      type = ComputeIsotropicElasticityTensor
      #block = 1
      youngs_modulus = 1e11
      poissons_ratio = 0.3
    [../]
    #[./compute_stress]
    #    type = ComputeFiniteStrainElasticStress 
    #[../]
    [./creep_plas]
      type = ComputeMultipleInelasticStress
      tangent_operator = elastic
      inelastic_models = 'creep plas'
      max_iterations = 50
      absolute_tolerance = 1e-06
      #combined_inelastic_strain_weights = '0.0 1.0'
    [../]
    [./creep]
      type = PowerLawCreepStressUpdate
      coefficient = 1e-45
      n_exponent = 5
      m_exponent = -0.5
      activation_energy = 0
    [../]
    [./plas]
      type = IsotropicPlasticityStressUpdate
      #hardening_constant = 100E6
      hardening_function = swift
      yield_stress = 200E6
    [../]
  []
  
  [Executioner]
    type = Transient
  
    #Preconditioned JFNK (default)
    solve_type = 'PJFNK'
  
    #petsc_options = '-snes_ksp'
    #petsc_options_iname = '-ksp_gmres_restart'
    #petsc_options_value = '101'
  
    line_search = 'none'
    automatic_scaling = True
    l_max_its = 20
    nl_max_its = 6
    nl_rel_tol = 1e-8
    nl_abs_tol = 1e-8
    l_tol = 1e-8
    l_abs_tol = 1E-8
    start_time = 0.0
    end_time = 100
    dtmin =1E-4
  
    [./TimeStepper]
      type = FunctionDT
      function = dts
    [../]
  []
  
  [Outputs]
    exodus = true
  []

  [Postprocessors]
    [./react_y]
      type = SidesetReaction
      direction = '0 1 0'
      stress_tensor = stress
      boundary = 'Btm-BC'
    [../]
  []
