#!/bin/bash

for np in 1 2 4; do
  mpirun -np ${np} ./operations.py benchmark_mps --np 1
done
