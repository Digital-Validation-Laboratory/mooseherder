#_* Variables
n_elem_y = 120
e_modulus = 3300000000.0
p_ratio = 0.33
#**

[GlobalParams]
    displacements = 'disp_x disp_y'
[]

[Mesh]
    [generated]
        type = GeneratedMeshGenerator
        dim = 2
        nx = 100 # ${n_elem_x}
        ny = ${n_elem_y}
        xmax = 2
        ymax = 1
    []
[]

[Modules/TensorMechanics/Master]
    [all]
        add_variables = true
        generate_output = 'vonmises_stress strain_xx strain_yy strain_zz'
    []
[]

#
# Added boundary/loading conditions
# https://mooseframework.inl.gov/modules/tensor_mechanics/tutorials/introduction/step02.html
#
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

# consider all off-diagonal Jacobians for preconditioning
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
    end_time = 5
    dt = 1
[]

[Outputs]
    exodus = true
[]