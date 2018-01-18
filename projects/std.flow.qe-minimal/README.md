# About

This is a simple example on how to setup a **signac-flow** project for Density-functional theory (DFT) calculations with [Quantum Espresso](http://www.quantum-espresso.org/).


## Tested for:

    * signac 0.9.2
    * signac-flow 0.5.5
    * QuantumEspresso 6.1


## Before you start:

    1. Update the path to your local pw.x binary in the operations.py module.

## Usage

```
python init.py
python project.py status -d
python project.py run vc_relax
python project.py run scf
```

