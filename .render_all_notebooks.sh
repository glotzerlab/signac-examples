#!/bin/bash

# Requires many dependencies specified in pixi.toml

# Remove existing signac workspaces used by notebooks
rm -rf notebooks/projects

# Render all notebooks by executing them and overwriting contents
jupyter nbconvert --execute --inplace notebooks/*.ipynb

# Clean up the notebooks using prek hooks (formatters)
# Importantly, this removes extra metadata and strips user paths
prek run --files notebooks/*.ipynb
