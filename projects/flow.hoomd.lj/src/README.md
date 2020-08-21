## An Introductory Walk-through Using signac with HOOMD-blue

1. Initialize the project with `python init.py`.
    - This creates the `workspace/`, which holds all of our `jobs`. Each `job` has its own directory, named by the job's unique `id` (something like `87c7fccdea3531da704bbae95e95e914`).
    - If you look in these directories, you'll see `signac_statepoint.json`. This is a json file that contains the statepoint parameters for that job.
    - NOTE: The job's `id` is generated specifically for the dict containing the statepoint parameters, so do not directly change the directory name or `signac_statepoint.json` directly.

2. All of the operations we will be performing on our data is stored in `project.py`. An operation is a function with `job` as its only argument that signac-flow recognizes as a part of your workflow.
    - You can tell which methods are operations because they will have the `@MyProject.operation` decorator, which tells signac that this method is to be treated as an operation.
    - `operation`s typically have pre- and post- conditions. This is how signac knows when the operation should be run. For example, the `initialize()` function has no pre-condition because it must be run first, but has `@MyProject.post.isfile('init.gsd')` as a post-condition. This post-condition means that the operation will *not* be run if `init.gsd` exists.

3. Now run let's run the operations:
    - Run `python project.py status -d` (`-d` specifies a "detailed view"). You will see a list of jobs and that `estimate` and `initialize` are eligible operations, as determined by those operations' pre- and post- conditions.
    - Now run `python project.py run -o initialize`. This will run just the `initialize()` operations for *all* eligible jobs (which in this case is all of the jobs).
    - Run `python project.py status -d` again, and you'll see that now all the jobs are eligible for `estimate` and `sample`.
    - Run `python project.py run`, which will now run all eligible operations, and you'll see HOOMD be called. When you call `python project.py status -d` now, you'll see that no operations are eligible, and that the labels `estimated`, `sampled`, and `started` are now visible. These labels are defined in `project.py` with the `@MyProject.label` decorator.

4. For more information on how you can analyze this data, take a look at the `visualize_data.ipynb` jupyter notebook in this directory.

NOTE: If you want to run this tutorial from scratch, just run `rm -rf workspace/` to delete the workspace.
