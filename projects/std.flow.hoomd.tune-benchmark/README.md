# README #

## About

Brief examples on how to use **signac-flow** for tuning and benchmarking of **HOOMD-blue (HPMC)** simulations.

Author: Carl Simon Adorf <csadorf@umich.edu>

## Usage

Make sure to install [HOOMD-blue](http://hoomd-blue.readthedocs.io) and [signac-flow](http://signac-flow.readthedocs.io), then execute:
```bash
$ python init.py
$ ./operations.py setup
$ ./tune.sh
$ ./benchmark.sh
$ python project.py status --detailed -p n
```

You should see output similar to
```bash
$ python project.py status --detailed -p n
Generate output...

Status project 'hoomd-benchmarking-example-project':
Total # of jobs: 2

label                                 progress
------------------------------------  --------------------------------------------------
tuned                                 |########################################| 100.00%
MPS/np:1=4.2e+06|2=2.5e+06|4=1.9e+06  |####################--------------------| 50.00%
MPS/np:1=3.5e+06|2=2.2e+06|4=1.1e+06  |####################--------------------| 50.00%

Detailed view:
job_id                            S      next_op    n  labels
--------------------------------  ---  ---------  ---  -------------------------------------------
ad82cca43a115d09a74e476d4d0978c3  U                10  MPS/np:1=3.5e+06|2=2.2e+06|4=1.1e+06, tuned
42eae87faa3b2f6e941339a06bc21822  U                20  MPS/np:1=4.2e+06|2=2.5e+06|4=1.9e+06, tuned

Abbreviations used:
S: status
U: unknown
```
