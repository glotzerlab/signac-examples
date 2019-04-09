from signac import init_project

project = init_project('hoomd-benchmarking-example-project')

for diameter in 0.5, :
    for lattice_a in 0.5, :
        for n in 10, 20:
            project.open_job({
                'random_seed': 0,
                'diameter': 1.0,
                'lattice': {'a': 1.05},
                'n': n,
            }).init()
