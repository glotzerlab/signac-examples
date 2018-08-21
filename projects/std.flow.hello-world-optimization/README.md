# About

This is a hello world example for an optimization flow project.
It features the optimization of three mathematical functions, which are
stand-ins for more expensive operations.

# Implementation

The optimization problem is implemented as a meta-project, which has the
optimization function itself, the random seed and the initial guess variable
as state point parameters.

The actual optimization data is stored in a separate project, which is either
a sub-space within each optimization job, or a shared space between all
optimization jobs (controlled by the `USE_SHARED_SIMULATION_DATA_SPACE` variable).

# Usage

```
python init.py
python project.py status --detailed -p func
python project.py run --num-passes=100
```
You can also set `--num-passes=-1` for unlimited number of executions.
