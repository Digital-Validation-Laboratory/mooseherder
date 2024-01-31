# This is a simple MOOSE tensor mechanics input script for testing the herder
dimension = 2 # Putting this variable outside the block to test

#_* Variables Block
n_elem_x = 20
n_elem_y = 20 # Testing comments in the variables block
e_modulus = 1e9
# Comment line to test
p_ratio = 0.3 # Another comment to test with
e_type = QUAD4
time_end = 3
#**

[GlobalParams]
    displacements = 'disp_x disp_y'
[]

[Mesh]
    [generated]
        type = GeneratedMeshGenerator
        dim = ${dimension}
        nx = ${n_elem_x}
        ny = ${n_elem_y}
        xmax = 2
        ymax = 1
        elem_type = ${e_type}
    []
[]

[Modules/TensorMechanics/Master]
    [all]
        add_variables = true
        generate_output = 'vonmises_stress stress_yy stress_xx stress_xy strain_xx strain_yy strain_xy strain_zz'
    []
[]

[BCs]
    [bottom_x]
        type = DirichletBC
        variable = disp_x
        boundary = bottom
        value = 0
    []
    [bottom_y]
        type = DirichletBC
        variable = disp_y
        boundary = bottom
        value = 0
    []
    [Pressure]
        [top]
        boundary = top
        function = 1e7*t
        []
    []
[]

[Materials]
    [elasticity]
        type = ComputeIsotropicElasticityTensor
        youngs_modulus = ${e_modulus}
        poissons_ratio = ${p_ratio}
    []
    [stress]
        type = ComputeLinearElasticStress
    []
[]

[Preconditioning]
    [SMP]
        type = SMP
        full = true
    []
[]

[Executioner]
    type = Transient
    # we chose a direct solver here
    petsc_options_iname = '-pc_type'
    petsc_options_value = 'lu'
    end_time = ${time_end}
    dt = 1
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
        boundary = 'bottom'
    [../]
    [./max_y_disp]
        type = NodalExtremeValue
        variable = disp_y
    [../]
    [./max_yy_stress]
        type = ElementExtremeValue
        variable = stress_yy
    [../]
    [./avg_yy_stress]
        type = ElementAverageValue
        variable = stress_yy
    [../]
[]


