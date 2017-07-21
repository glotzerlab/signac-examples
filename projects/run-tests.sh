#!/bin/bash

set -e

for project in `ls -d */`; do
    requirements=$project/requirements.txt
    if [ -e $requirements ]
    then
        conda install --yes --use-index-cache --file $requirements
    fi
    flow-test $project -vv
done
