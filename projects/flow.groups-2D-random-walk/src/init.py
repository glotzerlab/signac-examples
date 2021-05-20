#!/usr/bin/env python3
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories."""
import logging

import numpy as np
import signac

logger = logging.getLogger()
# Lower level to prevent output
logger.setLevel(logging.WARN)

# The different standard deviations to use for generating moves in the random
# walk
STANDARD_DEVIATIONS = np.linspace(start=0.1, stop=1, num=20)
NUMBER_REPLICAS = 100
RUN_STEPS = 5_000


def main():
    project = signac.init_project("2D Gaussian Random Walk")
    project.doc.run_steps = RUN_STEPS
    for replica in range(NUMBER_REPLICAS):
        for std in STANDARD_DEVIATIONS:
            statepoint = {"mean": 0, "std": std, "replica": replica + 1}

            job = project.open_job(statepoint)

            logger.warn(f"Initializing job with state point: {statepoint}.")
            job.init()


if __name__ == "__main__":
    main()
