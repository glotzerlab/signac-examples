#!/bin/bash

set -euo pipefail

for PROJECT in `ls -d */`; do
    if [[ "$CI" ]]; then
        echo "::group::Testing ${PROJECT}"
    fi

    if [ -e "${PROJECT}/.skipci" ]; then
        echo "Skipping tests for project ${PROJECT}."
        if [[ "$CI" ]]; then
            echo "::endgroup::"
        fi
        continue
    fi
    REQUIREMENTS_FILE="${PROJECT}/requirements.txt"
    echo "Run test for ${PROJECT}."
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
