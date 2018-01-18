#!/usr/bin/env python
"""Initialize the project's data space."""
import argparse
import signac
import subprocess

def main(args):
    try:
        project = signac.get_project()
    except LookupError:
        project = signac.init_project('GROMACSExample')

    statepoints_init = []

    pdb_url = "https://files.rcsb.org/download/"

    proteins = ["1K8H"]
    for protein in proteins:
        sp = dict(protein=protein)
        job = project.open_job(sp)
        job.init()
        with job:
            subprocess.check_output(["curl", pdb_url + protein + '.pdb', "-o", "protein.pdb"])
        statepoints_init.append(sp)

        # Writing statepoints to hash table as backup
    project.write_statepoints(statepoints_init)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Initialize the data space.")
    args = parser.parse_args()

    main(args)
