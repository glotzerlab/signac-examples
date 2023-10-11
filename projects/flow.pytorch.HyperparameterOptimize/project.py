import numpy as np
import signac
from flow import FlowProject


class Project(FlowProject):
    pass


@Project.label
def status_label(job):
    return ", ".join(
        [
            f"{check_point}_completed"
            for check_point in ("train", "evaluation")
            if job.doc.get(check_point + "_done", False)
        ]
    )


def check_train_complete(job):
    return job.doc.get("train_done", False)


def check_eval_complete(job):
    return job.doc.get("evaluation_done", False)


def gpu_directives(walltime: float = 0.5, n_gpu: int = 1):
    return {"nranks": n_gpu, "ngpu": n_gpu, "walltime": walltime}


def cpu_directives(walltime: float = 0.5, n_cpu: int = 1):
    return {"nranks": n_cpu, "walltime": walltime}


def store_success_to_doc(operation_name, job):
    job.doc.update({f"{operation_name}_done": True})


training_group = Project.make_group(name="trainings")

PR = signac.get_project()
TRAIN_WALLTIME = 1
EVAL_WALLTIME = 0.5


@training_group
@Project.operation(directives=cpu_directives(walltime=TRAIN_WALLTIME))
@Project.operation_hooks.on_success(store_success_to_doc)
@Project.post(check_train_complete)
def train(job):
    """ """
    import torch
    from source import vae

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, val_loader = vae.load_data(job)
    vae.fit(job=job, train_loader=train_loader, val_loader=val_loader, device=device)


@training_group
@Project.operation(directives=cpu_directives(walltime=EVAL_WALLTIME))
@Project.pre.after(train)
@Project.operation_hooks.on_success(store_success_to_doc)
@Project.post(check_eval_complete)
def evaluation(job):
    import torch
    from source import vae

    np.random.seed(job.sp["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, val_loader = vae.load_data(job)
    vae.plot_loss(job)

    random_idx = np.random.randint(0, len(val_loader.dataset) - 1, 9).tolist()
    vae.plot_reconstruction(
        job=job,
        data_loader=val_loader,
        demo_idxs=random_idx,
        plot_arrangement=(3, 3),
        device=device,
    )
    vae.plot_latent(
        job=job,
        data_loader=val_loader,
        device=device,
        # If False, only plot first 2 dimensions of latent space. If True, use UMAP to
        # reduce the latent space dimensions to 2.
        reduce_dim=True,
    )


if __name__ == "__main__":
    Project().main()
