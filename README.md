[![Binder](http://mybinder.org/badge.svg)](http://www.mybinder.org:/repo/csadorf/signac-examples)

# signac - Tutorial and Examples

## Tutorial

The `notebooks` directory contains a collection of jupyter notebooks that serve as tutorial.
They demonstrate how to implement a basic computational workflow using the [signac framework](https://glotzerlab.engin.umich.edu/signac).
The framework assists users in managing simple to complext data spaces for example by simplifying provenance tracking and meta data management.

Use [nbviewer](http://nbviewer.jupyter.org) to view a [static version](http://nbviewer.jupyter.org/github/csadorf/signac-examples/blob/master/index.ipynb) of these notebooks.
Or start a [dynamic version](https://mybinder.org/v2/gh/csadorf/signac-examples/master?filepath=notebooks%2Findex.ipynb) with the service offered by [mybinder.org](http://www.mybinder.org).

To run the notebooks locally, clone the repository and then start jupyter:
```
#!bash
$ git clone https://bitbucket.org/glotzer/signac-examples.git
$ cd signac-examples/notebooks
$ jupyter
```

## Examples

The [projects directory](projects/) contains a collection of project examples.
They are designed as examples and for the fast setup of new projects.

Simply clone or download this repository and copy all scripts into your signac project root directory, *e.g.*:

```
#!bash
$ git clone https://bitbucket.org/glotzer/signac-examples.git
$ mkdir my_project
$ cd my_project
$ signac init MyProject
$ cp -r ../signac-examples/projects/flow.minimal/* ./
```

For more information, please see [projects/README.md](projects/README.md).

## Copyright Notice

All code as part of this repository is released under the **BSD 3-Clause** [license](LICENSE.txt), except for the examples found in the *projects/* directory which are released into the [public domain](projects/LICENSE.txt).
