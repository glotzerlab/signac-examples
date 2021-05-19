A study on 2D Gaussian random walks using __groups__ and __aggregates__

Here we use simulations of a 2D random walk to demonstrate the __groups__ and __aggregation__ features of __signac-flow__.

# Usage

1. Initialize the project with

    ```
    python3 src/init.py
    ```

2. Now let's simulate the random walks:

    ```
    python3 src/project.py run -o simulate
    ```

3. From here we can use the `post-processing` group to run all the aggregate operations computing the mean squared displacement, and creating multiple plots.

    ```
    python3 src/project.py run -o post-processing
    ```

4. Now we can run the final operation, `plot_mean_squared_distance` with
    ```
    python3 src/project.py run
    ```

The current status of the project can be viewed using

```
python src/project.py status -d
```

**NOTE**: If you want to run this tutorial from scratch, just run `rm -rf workspace/` to delete the workspace.

# Modules

The following list is a brief overview of the modules and scripts to be found within the project template.

Modules, that are usually modified by the user:

 * `init.py` - **Init**ialize the project and parameter space.
 * `project.py` - Configuration, execution, and submission of the **project** workflow. Definition and execution of python-based data space **operations**.
