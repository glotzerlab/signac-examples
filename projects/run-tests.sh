#!/bin/bash

set -euo pipefail

for PROJECT in `ls -d */`; do
    if [ -e "${PROJECT}/.skipci" ]; then
        echo "Skipping ${PROJECT}"
        continue
    fi
    if [[ "$CI" ]]; then
        echo "::group::Executing ${PROJECT}"
    else
        echo "Executing ${PROJECT}"
    fi
    REQUIREMENTS_FILE="${PROJECT}/requirements.txt"
    if [ -e ${REQUIREMENTS_FILE} ]; then
        echo "Installing requirements:"
        cat ${REQUIREMENTS_FILE}
        mamba install --yes --file ${REQUIREMENTS_FILE} --quiet
    fi
    python flow-test.py ${PROJECT} -vv --timeout=600 $@
    if [[ "$CI" ]]; then
        echo "::endgroup::"
    fi
done
