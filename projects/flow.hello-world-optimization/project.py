#!/usr/bin/env python
import math
import random

from flow import FlowProject


# Use this variable to control the maximum number of generations that
# are generated for each optimization job.
MAX_NUM_GENERATIONS = 200


def _convert_to_tuple(l):
    return tuple(tuple(_) if isinstance(_, list) else _ for _ in l)


def calc_cost(job):
    "Calculate the current 'cost' function of this job."
    return abs(job.doc.y)


def is_primary(job):
    return job.sp.primary


class OptimizationProject(FlowProject):
    pass


def get_simulation_sub_jobs(primary_job, simulated=None):
    "Retrieve all simulation jobs belonging to this primary-job."
    filter = {"func": primary_job.sp.func, "primary": False}
    if simulated is True or simulated is False:
        doc_filter = {"y": {"$exists": simulated}}
    elif simulated is None:
        doc_filter = None
    else:
        raise ValueError(simulated)
    return primary_job._project.find_jobs(filter, doc_filter)


@OptimizationProject.label
def simulated(job):
    if job.sp.primary:
        return len(get_simulation_sub_jobs(job, simulated=False)) == 0
    else:
        return "y" in job.doc


@OptimizationProject.operation
@OptimizationProject.pre(lambda job: not is_primary(job))
@OptimizationProject.post(simulated)
def simulate(job):
    from time import sleep

    sleep(0.5)  # Artificial computational cost!!
    func = eval("lambda x: " + job.sp.func, dict(sqrt=math.sqrt))
    job.doc.y = func(job.sp.x)


@OptimizationProject.label
def num_jobs(job):
    if job.sp.primary:
        return "#jobs={}".format(len(get_simulation_sub_jobs(job)))


@OptimizationProject.label
def cost_label(job):
    if job.sp.primary:
        try:
            min_cost = min(map(calc_cost, get_simulation_sub_jobs(job, simulated=True)))
            return "min-cost:{:0.3f}".format(min_cost)
        except ValueError:  # no jobs
            return "min-cost:n/a"


@OptimizationProject.label
def solution_label(job):
    if job.sp.primary:
        sim_jobs_simulated = get_simulation_sub_jobs(job, simulated=True)
        for sim_job in sorted(sim_jobs_simulated, key=calc_cost):
            return "solution:x={:0.5f}".format(sim_job.sp.x)
        return "solution:n/a"


@OptimizationProject.label
def exhausted(job):
    "True when we have exhausted the maximum number of generations."
    if job.sp.primary:
        sim_jobs = get_simulation_sub_jobs(job)
        return len(sim_jobs) > MAX_NUM_GENERATIONS


@OptimizationProject.label
def converged(job):
    "True when we have converged to a solution."
    if job.sp.primary:
        try:
            min_cost = min(map(calc_cost, get_simulation_sub_jobs(job, simulated=True)))
            return min_cost < job.doc.max_cost
        except ValueError:  # no jobs
            return False


@OptimizationProject.operation
@OptimizationProject.pre(
    is_primary
)  # execute this operation only on the "primary" job.
@OptimizationProject.pre(simulated)
@OptimizationProject.pre(lambda job: not exhausted(job))
@OptimizationProject.post(converged)
def spawn_new_simulations(job, n=4):
    try:
        # Load the stored random generator state...
        random.setstate(_convert_to_tuple(job.doc.rng))
    except AttributeError:
        # ... or initialize if no state was previously stored.
        random.seed(job.sp.seed)

    project = job._project
    for i in range(n):
        x = random.uniform(0, 4)
        project.open_job(dict(func=job.sp.func, x=x, primary=False)).init()

    # Store state of random generator.
    job.doc.rng = random.getstate()


if __name__ == "__main__":
    OptimizationProject().main()
