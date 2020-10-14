#!/usr/bin/env python
import signac

project = signac.init_project("Optimization")

for seed in (0,):
    for func in (
        "(x - 1.0)**2",  # solution: x = 1.0
        "(x - 2.0)**3",  # solution: x = 2.0
        "sqrt(x) - sqrt(3.0)",  # solution: x = 3.0
    ):
        job = project.open_job({"func": func, "x0": 0, "seed": seed, "master": True})
        job.document.setdefault("max_cost", 1e-2)  # convergence criterion
