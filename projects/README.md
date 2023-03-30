# Examples

This is a collection of project examples, designed to demonstrate possible signac workflows and for the fast setup of new projects.

## Usage

Simply clone or download this repository and copy the scripts related to a specific example into your project path.
Example:

```bash
git clone https://github.com/glotzerlab/signac-examples.git
cp -r signac-examples/projects/flow.minimal/ my_project
cd my_project
signac init
```

## Namespaces

Project names are divided into namespaces to avoid name clashes.
These are namespaces used:

  * *flow*: These examples require **signac-flow**.
  * *hoomd*: These examples require **HOOMD-blue**.
  * *qe*: These examples require **Quantum-Espresso**.
  * *gmx*: The examples requires **GROMACS**.

*If you intend to create your own library of example projects, consider placing them in a namespace clearly related to your organization.*

## Project Overview

### [idg-minimal](idg-minimal/)

Minimal example for the calculation and storage of a phase diagram for an *ideal gas* with **signac**.

### [flow.2D-random-walk](flow.2D-random-walk/)

A study on 2D Gaussian random walks using **groups** and **aggregation**.

### [flow.aggregation-mpi](flow.aggregation-mpi/)

This is an example of a signac-flow project using aggregation to split MPI communicators.

### [flow.aggregation-plotting](flow.aggregation-plotting/)

An example of plotting data using **aggregation**.

### [flow.gmx-lysozyme-in-water](flow.gmx-lysozyme-in-water/)

This project provides a demonstration of a complete GROMACS workflow using signac and signac-flow.
The simulation flow follows Justin Lemkul's
[Lysozyme in Water Tutorial](http://www.bevanlab.biochem.vt.edu/Pages/Personal/justin/gmx-tutorials/lysozyme/),
illustrating how all key steps can be automated and simplified using signac and signac-flow.
If you plan to use this to simulate a different system, note that the physics encoded by these
parameter files may not be appropriate; you should modify the mdp files to model the
appropriate physics correctly.

### [flow.gmx-mtools](flow.gmx-mtools/)

Template for MoSDeF- and GROMACS-centric project managed with signac

### [flow.hello-world-optimization](flow.hello-world-optimization/)

This is a "hello world" example for an optimization flow project.
It features the optimization of three mathematical functions, which are stand-ins for more expensive simulations.

### [flow.hello-world](flow.hello-world/)

This is a hello world example flow project.
It features a *hello* operation, which prints `Hello {job._id}` to screen and writes the same string to a file.

### [flow.minimal](flow.minimal/)

This is a minimal example for a signac-flow project.

### [flow.qe-minimal](flow.qe-minimal/)

This is a simple example on how to setup a **signac-flow** project for Density-functional theory (DFT) calculations with [Quantum Espresso](http://www.quantum-espresso.org/).
Quantum Espresso can be installed with:

### [flow.hoomd.lj](flow.hoomd.lj/)

An Introductory Walk-through Using signac with HOOMD-blue

### [flow.sklearn.init-ParameterGrid](flow.sklearn.init-ParameterGrid/)

This example projects shows how to use signac-flow in combination with scikit-learn.
The scripts perform a grid search over model hyperparameters for a simple classifier, saving the results of each evaluated parameter set into a signac data space.
Then, a confusion matrix is plotted for each set of model hyperparameters.
The script `dashboard.py` can be used with signac-dashboard to visualize these plots.

## Copyright Notice

**UNLESS OTHERWISE STATED, ALL CODE PROVIDED AS PART OF THIS EXAMPLE COLLECTION (projects/*) IS RELEASED INTO THE PUBLIC DOMAIN!**

The full copyright notice can be found in [LICENSE.txt](LICENSE.txt).
