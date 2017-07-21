# Examples

This is a collection of project examples, designed to demonstrate possible signac workflows and for the fast setup of new projects.

## Usage

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

## Namespaces

Project names are divided into namespaces to avoid name clashes.
These are namespaces used:

  * *std*: *Standard* examples that only require the **signac** core package.
  * *std.flow*: These *standard* examples require **signac-flow**.

*If you intend to create your own library of example projects, consider to place them in a namespace clearly related to your organization.*

## Project Overview

### [std.idg-minimal](std.idg-minimal/)

Minimal example for the calculation and storage of a phase diagram for an *ideal gas*.

### [std.flow.minimal](std.flow.minimal/)

The absolute bare minimum of scripts required to setup a **signac-flow** workflow.

### [std.flow.hello-world](std.flow.hello-world/)

A minimal example for a **signac-flow** workflow with one *hello-world* data space operation.

### [std.hoomd.lj-minimal](std.hoomd.lj-minimal)

Minimal example for the generation of a phase diagram for a Lennard-Jones fluid with **signac** and **HOOMD-blue**.

## Copyright Notice

**All code provided as part of this example collection (projects/*) is released into the public domain.**

The full copy right notice can be found in [LICENSE.txt](LICENSE.txt).

