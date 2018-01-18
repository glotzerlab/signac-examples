#!/usr/bin/env python
"""Initialize the project's data space."""
import os
import subprocess

import signac

PDB_URL = "https://files.rcsb.org/download/"
MDP_URL = "http://www.bevanlab.biochem.vt.edu/Pages/Personal/justin/gmx-tutorials/lysozyme/Files/"


# Initialize signac project
project = signac.init_project('std.flow.gromacs-example-project')

# Download MDP files from tutorial website
os.makedirs('mdp_files', exist_ok=True)
for fn in ('em.mdp', 'ions.mdp', 'md.mdp', 'npt.mdp', 'nvt.mdp'):
    subprocess.check_output(["curl", URL + fn, "-o", project.fn("mdp_files/" + fn)])

# Initialize data space for one protein
for protein in ["1AKI"]:
    job = project.open_job(dict(protein=protein))
    with job:
        subprocess.check_output(["curl", PDB_URL + protein + '.pdb', "-o", "protein.pdb"])
