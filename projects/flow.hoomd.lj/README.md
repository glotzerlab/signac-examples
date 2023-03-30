An Introductory Walk-through Using signac with HOOMD-blue

This example project features the generation of a p-V phase diagram of a simulated Lennard-Jones (LJ) fluid and an ideal gas estimate.
The LJ fluid is sampled via molecular dynamics using the [HOOMD-blue particle simulation toolkit](https://glotzerlab.engin.umich.edu/hoomd-blue/).


# Usage

1. Initialize the project with

    ```
    python src/init.py
    ```

- This creates the `workspace/`, which holds all of our `jobs`. Each `job` has its own directory, named by the job's unique `id` (something like `87c7fccdea3531da704bbae95e95e914`).
- If you look in these directories, you'll see `signac_statepoint.json`. This is a json file that contains the statepoint parameters for that job.
- NOTE: The job's `id` is generated specifically for the dict containing the statepoint parameters, so do not edit the directory name or `signac_statepoint.json`.

2. All of the operations we will be performing on our data are defined in `project.py`. An operation is a function with `job` as its only argument that signac-flow recognizes as a part of your workflow.
    - You can tell which methods are operations because they will have the `@MyProject.operation` decorator, which tells signac-flow that this method is to be treated as an operation associated with `MyProject`.
    - `operation`s typically have pre- and post-conditions. This is how signac-flow knows when the operation should be run. For example, the `initialize()` function has no pre-condition because it must be run first, but has `@MyProject.post.isfile('init.gsd')` as a post-condition. This post-condition means that the operation will *not* be run if `init.gsd` exists in the job directory.

3. Now let's run the operations:

- First run a status check:

    ```
    python src/project.py status -d
    ```

    `-d` specifies a "detailed view". You will see a list of jobs and that `estimate` and `initialize` are eligible operations, as determined by those operations' pre- and post-conditions.

- Now initialize eligible jobs:

    ```
    python src/project.py run -o initialize
    ```

    This will run just the `initialize()` operation for *all* eligible jobs (which in this case is all of the jobs).
    - Run `python project.py status -d` again, and you'll see that now all the jobs are eligible for the operations `estimate` and `sample`. You can also run `python project.py status -d -p p`. The `-p` argument specifies which parameters should be shown in the status view, and we pass in `p` to see which statepoint corresponds to which pressure.

- Now we can run the simulations:

    ```
    python src/project.py run
    ```

    which will now run all eligible operations, and you'll see HOOMD be called. When you call `python project.py status -d` now, you'll see that no operations are eligible, and that the labels `estimated`, `sampled`, and `started` are now visible. These labels are defined in `project.py` with the `@MyProject.label` decorator.

4. For more examples of how you can analyze this data, execute `jupyter notebook` within the project's path and open the `src/notebook.ipynb` notebook.

**NOTE**: If you want to run this tutorial from scratch, just run `rm -rf workspace/` to delete the workspace.


# Modules

The following list is a brief overview of the modules and scripts to be found within the project template.

Modules, that are usually modified by the user:

 * `init.py` - **Init**ialize the project and parameter space.
 * `project.py` - Configuration, execution, and submission of the **project** workflow. Definition and execution of python-based data space **operations**.
