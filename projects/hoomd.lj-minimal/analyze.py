import numpy
import signac

project = signac.get_project()

for job in project:
    log = numpy.genfromtxt(job.fn("log-output.log"), names=True)
    pressure = log["pressure"]
    print(job.sp.kT, pressure[len(log) // 2 :].mean())
