#_* Variables
n_elem_x = 40
n_elem_y = 20
e_modulus = 1e9
p_ratio = 0.3

#**

[GlobalParams]
    displacements = 'disp_x disp_y'
[]

[Mesh]
    [generated]
        type = GeneratedMeshGenerator
        dim = 2
        nx = ${n_elem_x}
        ny = ${n_elem_y}
        xmax = 2
        ymax = 1
        elem_type = QUAD4
        # EDGE, EDGE2, EDGE3, EDGE4, QUAD, QUAD4, QUAD8, QUAD9, TRI, TRI3, TRI6, TRI7, HEX, HEX8, HEX20, HEX27, TET, TET4, TET10, TET14, PRISM, PRISM6, PRISM15, PRISM18, PYRAMID, PYRAMID5, PYRAMID13, PYRAMID14
    []
[]

[Modules/TensorMechanics/Master]
    [all]
        add_variables = true
        generate_output = 'vonmises_stress strain_xx strain_yy strain_zz'
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
    solve_type = 'PJFNK'
    petsc_options_iname = '-pc_type -pc_hypre_type'
    petsc_options_value = 'hypre boomeramg'
    end_time = 5
    dt = 1
[]

[Outputs]
    exodus = true
[]