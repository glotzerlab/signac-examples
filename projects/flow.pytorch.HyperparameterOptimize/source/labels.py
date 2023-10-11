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
    if job.doc.get("train_done", None) is None:
        return False
    else:
        if job.doc["train_done"]:
            return True
        else:
            return False


def check_eval_complete(job):
    if job.doc.get("evaluation_done", None) is None:
        return False
    else:
        if job.doc["evaluation_done"]:
            return True
        else:
            return False
