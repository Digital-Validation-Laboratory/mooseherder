#
# Working version of a creep model with realistic-ish material model.
# This creep model isn't normalised so the power law causes big changes to A parameter.
#
[GlobalParams]
    displacements = 'disp_x disp_y disp_z'
  []
  
  [Mesh]
    type = FileMesh
    file = 'test_mesh.msh'
  []
  
  [Modules/TensorMechanics/Master]
    [./all]
      strain = FINITE
      incremental = true
      add_variables = true
      generate_output = 'stress_yy elastic_strain_yy creep_strain_yy stress_xx plastic_strain_yy mechanical_strain_xx mechanical_strain_yy'
    [../]
  []
  
  [Functions]
    [./top_pull]
      type = PiecewiseLinear
      x = '  0   0.5  100   '
      y = '-0 -0.1  -0.1' 
    [../]
  
    [./dts]
      type = PiecewiseLinear
      x = '0  0.5E3    1.0E3 2.16E7'
      y = '20  20  5E5  5E5'
    [../]

    [./swift]
        type = ParsedFunction
        expression = '0.4*(1E-3 +x)^0.1'
    [../]
  []
  
  [BCs]
    [./u_top_pull]
      type = Pressure
      variable = disp_y
      boundary = Top-BC
      factor = 0.65
      function = top_pull
    [../]
    [./u_bottom_fix]
      type = DirichletBC
      variable = disp_y
      boundary = Btm-BC
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
      youngs_modulus = 100
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
      absolute_tolerance = 1E3#1e-06
      #combined_inelastic_strain_weights = '0.0 1.0'
    [../]
    [./creep]
      type = PowerLawCreepStressUpdate
      coefficient = 2.1119#10.559
      n_exponent = 6.832
      m_exponent = -0.8
      activation_energy = 0
    [../]
    [./plas]
      type = IsotropicPlasticityStressUpdate
      #hardening_constant = 100E6
      hardening_function = swift
      yield_stress = 0.2#200E6
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
    nl_rel_tol = 1e-5
    nl_abs_tol = 1e-5
    l_tol = 1e-5
    l_abs_tol = 1E-5
    start_time = 0.0
    end_time = 2.16E7
    dtmin =1
  
    [./TimeStepper]
      type = FunctionDT
      function = dts
    [../]
  []
  
  [Outputs]
    #exodus = true
    [./out]
      type = Exodus
      elemental_as_nodal = true
    [../]
    csv = true
  []

  [Postprocessors]
    [./react_y]
      type = SidesetReaction
      direction = '0 1 0'
      stress_tensor = stress
      boundary = 'Btm-BC'
    [../]
    [./max_y_disp]
      type = NodalExtremeValue
      variable = disp_y 
    [../]       
    [./max_creep_strain]
      type = ElementExtremeValue
      variable = creep_strain_yy
    [../]  
    [./min_creep_strain]
      type = ElementExtremeValue
      variable = creep_strain_yy
      value_type = min
    [../]  
    [./max_plas_strain]
      type = ElementExtremeValue
      variable = plastic_strain_yy
    [../]  
    [./min_plas_strain]
      type = ElementExtremeValue
      variable = plastic_strain_yy
      value_type = min
    [../] 
    [./max_stress]
      type = ElementExtremeValue
      variable = stress_yy
    [../]
    [./avg_creep]
      type = ElementAverageValue
      variable = creep_strain_yy
    [../]

  []
