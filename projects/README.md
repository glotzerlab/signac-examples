# Examples

This is a collection of project examples, designed to demonstrate possible signac workflows and for the fast setup of new projects.

## Usage

Simply clone or download this repository and copy the scripts related to a specific example into your project root directory.
Example:

```
#!bash
$ git clone https://github.com/glotzerlab/signac-examples.git
$ mkdir my_project
$ cd my_project
$ signac init MyProject
$ cp -r ../signac-examples/projects/flow.minimal/* ./
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

### [flow.hello-world](flow.hello-world/)

This is a hello world example flow project.
It features a *hello* operation, which prints `Hello {job._id}` to screen and writes the same string to a file.

### [flow.hello-world-optimization](stf.flow.hello-world-optimization/)

This is a minimal example for how to implement an iterative optimization project with signac-flow.
This project dynamically spawns new jobs as a result of previous results.

### [flow.minimal](flow.minimal/)

This is a minimal example for a signac-flow project.

### [hoomd.lj-minimal](hoomd.lj-minimal/)

Minimal example for the generation of a phase diagram for a Lennard-Jones fluid with **signac** and **HOOMD-blue**.

### [flow.hoomd.lj](flow.hoomd.lj/)

The example project features the generation of a p-V phase diagram of a simulated Lennard-Jones (LJ) fluid and an ideal gas estimate.
The LJ fluid is sampled via molecular dynamics using the [HOOMD-blue particle simulation toolkit](https://glotzerlab.engin.umich.edu/hoomd-blue/).

### [flow.qe-minimal](flow.qe-minimal/)

The example project shows how to setup and execute a DFT calaculation with Quantum-Espresso and signac.

### [flow.gmx-lysozyme-in-water](flow.gmx-lysozyme-in-water/)

An example on how to integrate signac with GROMACS, following the tutorial by Justin A. Lmekul.

### [flow.gmx-mtools](flow.gmx-mtools/)

An example on how to integrate signac with GROMACS and mtools.
**This example is licensed under the MIT-License!**

## Copyright Notice

**UNLESS OTHERWISE STATED, ALL CODE PROVIDED AS PART OF THIS EXAMPLE COLLECTION (projects/*) IS RELEASED INTO THE PUBLIC DOMAIN!**

The full copyright notice can be found in [LICENSE.txt](LICENSE.txt).
