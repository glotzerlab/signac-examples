# About

The example project features the generation of a p-V phase diagram of a simulated Lennard-Jones (LJ) fluid and an ideal gas estimate.
The LJ fluid is sampled via molecular dynamics using the [HOOMD-blue particle simulation toolkit](https://glotzerlab.engin.umich.edu/hoomd-blue/).

# Usage

To execute the example workflow, follow these steps:

We start by initializing the project and a few state points with the `init.py` module.

```
python src/init.py 42
```

The number 42 is the random seed used for initialization, feel free to replace it with a different number or a text string, which will be converted into a numeric random seed.

The project's workflow and data space operations are defined within the `src/project.py` module.
We can check the project's status, e.g., with:

```
python src/project.py status --detailed --parameters p
```

We use the `--detailed` flag to show the labels explicitly for each job.
The `--parameters` (`-p`) argument specifies state point parameters that should be shown in the status overview.
In this case we specify to show the `p` variable, which stands for pressure.

The status will also show all pending operations (initialize/estimate-volume/sample).
The command

```
python src/project.py run
```

will execute the immediately pending operations for the complete data space.
You may need to execute this command multiple times to cycle through all pending operations.

Finally, we can analyze the data using a jupyter notebook, simply execute `jupyter notebook` within the project's root directory and open the `src/analysis.ipynb` notebook.

# Modules

The following list is a brief overview of the modules and scripts to be found within the project template.

Modules, that are usually modified by the user:

 * `src/init.py` - **Init**ialize the project and parameter space.
 * `src/operations.py` - Definition and execution of python-based data space **operations**.
 * `src/project.py` - Configuration, execution, and submission of the **project** workflow.

Other modules:

  * `src/environment.py` - Custom **environment** definitions
