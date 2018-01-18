import signac

project = signac.get_project()

# For this example, we only initialize a single job.
project.open_job({
    'potential':            'Si.pw-mt_fhi.upf',
    'lattice_parameter':    10.2625545471,
    'number_of_bands':      20,
    }).init()
