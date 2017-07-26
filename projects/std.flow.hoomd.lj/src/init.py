#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories."""
import logging
import argparse
from hashlib import sha1

import signac
import numpy as np


def main(args, random_seed):
    project = signac.init_project('Ideal-Gas-Example-Project')
    for replication_index in range(args.num_replicas):
        for p in np.linspace(0.5, 5.0, 10):
            statepoint = dict(
                    # system size
                    N=512,

                    # Lennard-Jones potential parameters
                    sigma=1.0,
                    epsilon=1.0,
                    r_cut=2.5,

                    # random seed
                    seed=random_seed*(replication_index + 1),

                    # thermal energy
                    kT=1.0,
                    # presure
                    p=p,
                    # thermostat coupling constant
                    tau=1.0,
                    # barostat coupling constant
                    tauP=1.0)
            project.open_job(statepoint).init()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Initialize the data space.")
    parser.add_argument(
        'random',
        type=str,
        help="A string to generate a random seed.")
    parser.add_argument(
        '-n', '--num-replicas',
        type=int,
        default=1,
        help="Initialize multiple replications.")
    args = parser.parse_args()

    # Generate an integer from the random str.
    try:
        random_seed = int(args.random)
    except ValueError:
        random_seed = int(sha1(args.random.encode()).hexdigest(), 16) % (10 ** 8)

    logging.basicConfig(level=logging.INFO)
    main(args, random_seed)
