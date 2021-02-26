#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories."""
import numpy as np
import signac


def main():
    project = signac.init_project("Ideal-Gas-Example-Project")
    # sweep over 10 pressures evenly spaced between 0.5 and 5.0
    for p in np.linspace(0.5, 5.0, 10):
        statepoint = dict(
            # system size
            N=512,
            # Lennard-Jones potential parameters
            sigma=1.0,
            epsilon=1.0,
            r_cut=2.5,
            # thermal energy
            kT=1.0,
            # pressure
            p=p,
            # thermostat coupling constant
            tau=1.0,
            # barostat coupling constant
            tauP=1.0,
        )

        # open the job and initialize
        job = project.open_job(statepoint)

        # define run steps in the job document so that run_steps
        # can be changed without modifying the statepoint
        job.doc["run_steps"] = 5000
        print(f"initializing state point with id {job.get_id()} and p = {job.sp.p}")
        job.init()


if __name__ == "__main__":
    main()
