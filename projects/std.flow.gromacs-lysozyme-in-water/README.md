# About

This project provides an example of how signac and signac-flow can be used with GROMACS.
Please note that the provided mdp files are NOT a good representation of a proper run
(e.g. all run times are far too short) and should be modified to model the appropriate
physics correctly.

# Requirements
* signac 0.9.1
* signac-flow 0.5.5
* GROMACS: version 5.1.4

# Usage

````
python init.py
python project.py status -d
python project.py run
# And repeat
````
