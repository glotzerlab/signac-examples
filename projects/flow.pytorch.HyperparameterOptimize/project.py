import numpy as np
import signac
import torch
from flow import FlowProject
from source import vae


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


def gpu_directives(walltime: float = 0.5, n_gpu: int = 1):
    return {"nranks": n_gpu, "ngpu": n_gpu, "walltime": walltime}


def cpu_directives(walltime: float = 0.5, n_cpu: int = 1):
    return {"nranks": n_cpu, "walltime": walltime}


def store_success_to_doc(operation_name, job):
    job.doc.update({f"{operation_name}_done": True})


training_group = Project.make_group(name="trainings")

TRAIN_WALLTIME = 1
EVAL_WALLTIME = 0.5


@training_group
@Project.operation_hooks.on_success(store_success_to_doc)
@Project.post.true("train_done")
@Project.operation(directives=gpu_directives(walltime=TRAIN_WALLTIME))
def train(job):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, val_loader = vae.load_data(job)
    vae.fit(job=job, train_loader=train_loader, val_loader=val_loader, device=device)


@training_group
@Project.operation_hooks.on_success(store_success_to_doc)
@Project.post.true("evaluation_done")
@Project.pre.after(train)
@Project.operation(directives=gpu_directives(walltime=EVAL_WALLTIME))
def evaluation(job):
    vae.plot_loss(job)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _, val_loader = vae.load_data(job)
    dataset = val_loader.dataset
    vae.plot_reconstruction(
        job=job, dataset=dataset, plot_arrangement=(3, 3), device=device
    )
    vae.plot_latent(job=job, dataset=dataset, device=device)


if __name__ == "__main__":
    Project().main()
