#!/bin/bash

for project in `ls -d */`; do
    requirements=$project/requirements.txt
    if [ -e $requirements ]
    then
        conda install --yes --dry-run --use-index-cache --file $requirements
    fi
    flow-test $project $@
done
