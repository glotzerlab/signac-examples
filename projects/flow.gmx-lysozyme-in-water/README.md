# About

This project provides a demonstration of a complete GROMACS workflow using signac and signac-flow.
The simulation flow follows Justin Lemkul's
[Lysozyme in Water Tutorial](http://www.bevanlab.biochem.vt.edu/Pages/Personal/justin/gmx-tutorials/lysozyme/),
illustrating how all key steps can be automated and simplified using signac and signac-flow.
If you plan to use this to simulate a different system, note that the physics encoded by these
parameter files may not be appropriate; you should modify the mdp files to model the
appropriate physics correctly.

# Tested with

  * signac 0.9.2
  * signac-flow 0.5.5
  * GROMACS: version 5.1.4

# Usage

```
python init.py
python project.py status -d
python project.py run
# And repeat
```
