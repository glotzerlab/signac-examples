# Examples

This is a collection of project examples, designed to demonstrate possible signac workflows and for the fast setup of new projects.

## Usage

### Manual download

Simply clone or download this repository and copy the scripts related to a specific example into your project root directory.
Example:

```
#!bash
$ git clone https://bitbucket.org/glotzer/signac-examples.git
$ mkdir my_project
$ cd my_project
$ signac init MyProject
$ cp -r ../signac-examples/projects/flow.minimal/* ./
```

### Download with flow-clone

If you have the [signac-utils package](https://bitbucket.org/glotzer/signac-utils) installed, you can download any of these templates with the following command:

```flow-clone https://bitbucket.org/glotzer/signac-examples.git#projects/[NAME_OF_THE_TEMPLATE]```

## Namespaces

Project names are divided into namespaces to avoid name clashes.
These are namespaces used:

  * *std*: *Standard* examples that only require the **signac** core package.
  * *flow*: These examples require **signac-flow**.
  * *hoomd*: These examples require **HOOMD-blue**.
  * *qe*: These examples require **Quantum-Espresso**.

*If you intend to create your own library of example projects, consider to place them in a namespace clearly related to your organization.*

## Project Overview

### [std.idg-minimal](std.idg-minimal/)

Minimal example for the calculation and storage of a phase diagram for an *ideal gas* with **signac**.

    flow-clone https://bitbucket.org/glotzer/signac-examples.git#projects/std.idg-minimal

### [std.flow.hello-world](std.flow.hello-world/)

This is a hello world example flow project.
It features a *hello* operation, which prints `Hello {job._id}` to screen and writes the same string to a file.

    flow-clone https://bitbucket.org/glotzer/signac-examples.git#projects/std.flow.hello-world

### [std.flow.minimal](std.flow.minimal/)

This is a minimal example for a signac-flow project.

    flow-clone https://bitbucket.org/glotzer/signac-examples.git#projects/std.flow.minimal

### [std.hoomd.lj-minimal](std.hoomd.lj-minimal/)

Minimal example for the generation of a phase diagram for a Lennard-Jones fluid with **signac** and **HOOMD-blue**.

    flow-clone https://bitbucket.org/glotzer/signac-examples.git#projects/std.hoomd.lj-minimal

### [std.flow.hoomd.lj](std.flow.hoomd.lj/)

The example project features the generation of a p-V phase diagram of a simulated Lennard-Jones (LJ) fluid and an ideal gas estimate.
The LJ fluid is sampled via molecular dynamics using the [HOOMD-blue particle simulation toolkit](https://glotzerlab.engin.umich.edu/hoomd-blue/).

    flow-clone https://bitbucket.org/glotzer/signac-examples.git#projects/std.flow.hoomd.lj

### [std.flow.qe-minimal](std.flow.qe-minimal/)

The example project shows how to setup and execute a DFT calaculation with Quantum-Espresso and signac.

## Copyright Notice

**All code provided as part of this example collection (projects/*) is released into the public domain.**

The full copy right notice can be found in [LICENSE.txt](LICENSE.txt).

