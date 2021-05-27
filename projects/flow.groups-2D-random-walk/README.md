A study on 2D Gaussian random walks using **groups** and **aggregates**

Here we use simulations of a 2D random walk to demonstrate the **groups** and **aggregation** features of **signac-flow**.
In addition, this example tries to showcase a robust workflow similar to those of real research projects while keeping the actual computation at a low level.

# Usage

1. Initialize the project with

    ```
    python3 src/init.py
    ```

2. Now let's simulate the random walks:

    ```
    python3 src/project.py run -o simulate
    ```

    Alternatively, we can use the base group to do some analysis as well with

    ```
    python3 src/project.py run -o base
    ```

    To see all the operations this previous command runs look at the `project.py` file.


3. From here we can use the `post-processing` group to run all the aggregate operations (besides one) computing the mean squared displacement, and creating multiple plots.

    ```
    python3 src/project.py run -o post-processing
    ```

4. Now we can run the final two operations, `plot_mean_squared_distance` and `plot_walks` with
    ```
    python3 src/project.py run -o plot_mean_squared_distance plot_walks
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
