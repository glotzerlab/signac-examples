# About

This is a simple example on how to setup a **signac-flow** project for Density-functional theory (DFT) calculations with [Quantum Espresso](http://www.quantum-espresso.org/).
Quantum Espresso can be installed with:

```
conda install -c conda-forge qe
```

## Tested for:

    * signac 0.9.2
    * signac-flow 0.5.5
    * QuantumEspresso 6.1


## Before you start:

    1. Update the path to your local pw.x binary in the project.py module.

## Usage

```
python init.py
python project.py status --detailed
python project.py run -o vc_relax
python project.py run -o scf
```

