import numpy
import signac

project = signac.get_project()

for job in project:
    log = numpy.genfromtxt(job.fn("log-output.log"), names=True)
    pressure = log["pressure"]
    start_step = len(log) // 2
    print(job.sp.kT, pressure[start_step:].mean())
