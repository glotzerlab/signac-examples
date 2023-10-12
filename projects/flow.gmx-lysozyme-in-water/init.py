#!/usr/bin/env python
"""Initialize the project's data space."""
import os
import subprocess

import signac

PDB_URL = "https://files.rcsb.org/download/"
MDP_URL = "http://www.mdtutorials.com/gmx/lysozyme/Files/"


# Initialize signac project
project = signac.init_project()


def download_file(source, destination):
    if not os.path.exists(destination):
        subprocess.check_output(["curl", source, "-o", destination])


# Download MDP files from tutorial website
os.makedirs("mdp_files", exist_ok=True)
for fn in ("minim.mdp", "ions.mdp", "md.mdp", "npt.mdp", "nvt.mdp"):
    output_fn = os.path.join(project.fn("mdp_files"), fn)
    download_file(MDP_URL + fn, os.path.join(project.fn("mdp_files"), fn))

# Initialize data space for one protein
for protein in ["1AKI"]:
    job = project.open_job(dict(protein=protein)).init()
    download_file(PDB_URL + protein + ".pdb", job.fn("protein.pdb"))
