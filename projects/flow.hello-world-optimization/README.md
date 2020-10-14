# About

This is a "hello world" example for an optimization flow project.
It features the optimization of three mathematical functions, which are stand-ins for more expensive simulations.

# Implementation

The optimization project is implemented with one *primary* job for each optimization, and a bunch of *simulation* jobs that actually execute the simulation.
The two kinds of jobs are distinguished by the **primary** state point parameter.

# Usage

## Local execution

```
python init.py
python project.py run --num-passes=100
```

You can also set `--num-passes=-1` for an unlimited number of execution passes.


## Submit to scheduler

The project comes with a special template that resubmits operations before and after the execution of each operation.
To submit the workflow to a scheduler, execute:

```
python init.py
python project.py submit
```

## Status

If you want to check the status of the optimization, use the following command:

```
python project.py status --detailed -p func -f primary true
```

To check the status of each simulation, use:

```
python project.py status --detailed -p func -f primary false
```
