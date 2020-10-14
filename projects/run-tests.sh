#!/bin/bash

set -e

for project in `ls -d */`; do
    REQUIREMENTS_FILE=$project/requirements.txt
    echo "Run test for $project."
    if [ -e ${REQUIREMENTS_FILE} ]; then
        echo "Installing requirements:"
        cat ${REQUIREMENTS_FILE}
        conda install --yes --use-index-cache --file ${REQUIREMENTS_FILE}
    fi
    ./flow-test $project -vv --timeout=600 $@
done