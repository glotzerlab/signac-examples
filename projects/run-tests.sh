#!/bin/bash

set -e

for project in `ls -d */`; do
    requirements=$project/requirements.txt
    echo "Run test for $project."
    if [ -e $requirements ]
    then
        cat $requirements
        conda install --yes --use-index-cache --file $requirements
    fi
    flow-test $project -vv --timeout=600
done
