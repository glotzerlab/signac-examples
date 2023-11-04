#!/bin/bash

# Requires many dependencies specified in environment.yml

# Remove existing signac workspaces used by notebooks
rm -rf notebooks/projects

# Render all notebooks by executing them and overwriting contents
jupyter nbconvert --execute --inplace notebooks/*.ipynb

# Clean up the notebooks using pre-commit hooks (formatters)
# Importantly, this removes extra metadata and strips user paths
pre-commit run --files notebooks/*.ipynb
