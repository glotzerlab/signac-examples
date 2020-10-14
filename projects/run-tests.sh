#!/bin/bash

set -e

python --version
for PROJECT in `ls -d */`; do
    if [ -e "${PROJECT}/.skipci" ]; then
        echo "Skipping tests for project ${PROJECT}."
        continue
    fi
    REQUIREMENTS_FILE="${PROJECT}/requirements.txt"
    echo "Run test for ${PROJECT}."
    if [ -e ${REQUIREMENTS_FILE} ]; then
        echo "Installing requirements:"
        cat ${REQUIREMENTS_FILE}
        conda install --yes --use-index-cache --file ${REQUIREMENTS_FILE}
    fi
    python flow-test.py ${PROJECT} -vv --timeout=600 $@
done
