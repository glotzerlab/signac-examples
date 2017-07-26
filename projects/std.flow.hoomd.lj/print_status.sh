#!/bin/bash

python src/project.py status --detailed --parameters p $@ | tee status.txt
