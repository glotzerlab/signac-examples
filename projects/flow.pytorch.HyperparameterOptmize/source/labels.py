from flow import FlowProject
import signac
import numpy as np


class Project(FlowProject):
    pass


@Project.label
def status_label(job):
    check_list = ["train", "evaluation"]
    check_results = ""
    for check_point in check_list:
        if job.doc.get(f"{check_point}_done") is not None:
            check_results += f"{check_point}_completed, "
        return check_results


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
