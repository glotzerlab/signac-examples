An Example of Using signac with [Pytorch] to train [Variational Autoencoder] (VAE).

This example project demonstrate how to use signac to optimize the hyperparameters of VAE trained on the popular [MNIST] datasets.

[Variational Autoencoder]: https://arxiv.org/pdf/1312.6114.pdf
[Pytorch]: https://pytorch.org/
[MNIST]: https://pytorch.org/vision/main/generated/torchvision.datasets.MNIST.html

## Prerequisites

This example use the following python packages:

```conda create --name pytorch python=3.10 matplotlib numpy signac-flow signac-dashboard h5py```
* [Numpy](https://github.com/numpy/numpy)
* [matplotlib](https://github.com/matplotlib/matplotlib)
* [signac](https://github.com/glotzerlab/signac)
* [signac-flow](https://github.com/glotzerlab/signac-flow)
* [signac-dashboard](https://github.com/glotzerlab/signac-dashboard)

```conda activate pytorch```
```conda install pytorch torchvision==0.13.0 -c pytorch```
* [Pytorch](https://github.com/pytorch/pytorch)
* [torchvision](https://github.com/pytorch/vision)


Conda users can install these from [conda-forge](https://conda-forge.org/):

# Usage

1. Initialize the project with

    ```
    python init.py
    ```
    
    In `init.py`, you can define VAE's hyperparameters you would like to try.

- This checks if MNIST dataset has been downloaded yet. If it's not, it will automatically download it and store in `/source/data/MNIST`.
- This creates the `workspace/`, which holds all of our `jobs`. Each `job` has its own directory, named by the job's unique `id` (something like `87c7fccdea3531da704bbae95e95e914`).\
- If you look in these directories, you'll see `signac_statepoint.json`. This is a json file that contains the statepoint parameters (hyperparameters of VAE) for that job.
- NOTE: The job's `id` is generated specifically for the dict containing the statepoint parameters, so do not edit the directory name or `signac_statepoint.json`.

2. All of the operations we will be performing on [MNIST] dataset are defined in `project.py`. An operation is a function with `job` as its only argument that signac-flow recognizes as a part of your workflow.
    - You can tell which methods are operations because they will have the `@Project.operation` decorator, which tells signac-flow that this method is to be treated as an operation associated with `Project`.
    - `operation`s typically have pre- and post-conditions. This is how signac-flow knows when the operation should be run. For example, the `train()` function has no pre-condition because it must be run first, but has `@Project.post(labels.check_train_complete)` as a post-condition.
   
3. All of the functions used in `project.py` are defined in three python scripts: `source/labels.py`, `source/workflow.py`, and `source/vae.py`.
    - `source/labels.py` defines the functions that are used to identify whether an signac project level operation is done or not in `project.py`.
    - `source/workflow.py` defines the functions that used to manage the workflow of training protocols including post-evaluation on the training.
    - `source/vae.py` defines any functions that relate to the training and post-evaluation of VAE using pytorch, which includes functions for, e.g. download [MNIST] dataset, and plot learning curve, etc.

4. Now let's run the operations:

- First run a status check:

    ```
    python project.py status -d
    ```

- Now run eligible jobs:

    ```
    python project.py run -o train
    ```

- After the training is done, you can run post-evaluation:

    ```
    python project.py run -o evaluation
    ```

5. For visualizing the post-evaluation, you can launch the [signac-dashbboard](https://github.com/glotzerlab/signac-dashboard):

    ```
    python dashborad.py run
    ```
    
    And open `http://localhost:8888/` in your web browser. 

**NOTE**: If you want to run this tutorial from scratch, just run `rm -rf workspace/` to delete the workspace.
