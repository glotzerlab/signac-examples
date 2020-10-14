# About

This example projects shows how to use signac-flow in combination with scikit-learn.
The scripts perform a grid search over model hyperparameters for a simple classifier, saving the results of each evaluated parameter set into a signac data space.
Then, a confusion matrix is plotted for each set of model hyperparameters.
The script `dashboard.py` can be used with signac-dashboard to visualize these plots.

# Usage

To execute the example workflow, follow these steps:

```
python init.py
python project.py status --detailed
python project.py run
```
