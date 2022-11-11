import flow
from source import workflow, labels
from source.workflow import Project
import signac
import numpy as np

PR = signac.get_project()
TRAIN_WALLTIME = 1
EVAL_WALLTIME = 0.5

@workflow.training_group
@Project.operation
# .with_directives(
#     workflow.cpu_directives(walltime=TRAIN_WALLTIME))
@Project.operation_hooks.on_success(workflow.store_success_to_doc)
@Project.operation_hooks.on_exception(workflow.store_error_to_doc)
@Project.post(labels.check_train_complete)
def train(job):
    """

    """
    from source import vae
    import torch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    train_loader, val_loader = vae.load_data(job)
    vae.fit(
        job=job,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device
    )
    return

@workflow.training_group
@Project.operation
# with_directives(
#     workflow.cpu_directives(walltime=EVAL_WALLTIME))
@Project.pre.after(train)
@Project.operation_hooks.on_success(workflow.store_success_to_doc)
@Project.operation_hooks.on_exception(workflow.store_error_to_doc)
@Project.post(labels.check_eval_complete)
def evaluation(job):

    from source import vae
    import torch

    np.random.seed(job.sp['seed'])
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    train_loader, val_loader = vae.load_data(job)
    vae.plot_loss(job)

    random_idx = np.random.randint(0, len(val_loader.dataset)-1, 9).tolist()
    vae.plot_reconstruction(
        job=job,
        data_loader=val_loader,
        demo_idxs=random_idx,
        plot_arrangement=(3, 3),
        device=device
    )
    vae.plot_latent(
        job=job,
        data_loader=val_loader,
        device=device,
        reduce_dim=True  # If False, only plot first 2 dimensions of latent space. If True, use UMAP to reduce the latent space dimensions to 2.
    )
    return

if __name__ == "__main__":
    Project().main()
