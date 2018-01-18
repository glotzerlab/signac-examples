#!/usr/bin/env python
"""Initialize the project's data space."""
import signac

PDB_URL = "https://files.rcsb.org/download/"

project = signac.init_project('std.flow.gromacs-example-project')

for protein in ["1K8H"]:
    job = project.open_job(dict(protein=protein))
    with job:
        subprocess.check_output(["curl", PDB_URL + protein + '.pdb', "-o", "protein.pdb"])
