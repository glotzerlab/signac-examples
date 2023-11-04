#!/bin/bash

set -euo pipefail

export USE_INDEX_CACHE=""
for PROJECT in `ls -d */`; do
    if [[ "$CI" ]]; then
        echo "Testing ::group::${PROJECT}"
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

        # Re-use the conda index cache after the first time.
        conda install --yes ${USE_INDEX_CACHE} --file ${REQUIREMENTS_FILE} --quiet
        export USE_INDEX_CACHE="--use-index-cache"
    fi
    python flow-test.py ${PROJECT} -vv --timeout=600 $@
    if [[ "$CI" ]]; then
        echo "::endgroup::"
    fi
done
