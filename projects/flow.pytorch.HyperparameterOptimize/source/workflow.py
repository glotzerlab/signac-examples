import flow

from .labels import Project

training_group = Project.make_group(name="trainings")


def gpu_directives(walltime: float = 0.5, n_gpu: int = 1):
    return {"nranks": n_gpu, "ngpu": n_gpu, "walltime": walltime}


def cpu_directives(walltime: float = 0.5, n_cpu: int = 1):
    return {"nranks": n_cpu, "walltime": walltime}


def store_success_to_doc(operation_name, job):
    job.doc.update({f"{operation_name}_done": True})


def store_error_to_doc(operation_name, error, job):
    job.doc.update({f"{operation_name}_done": False})
