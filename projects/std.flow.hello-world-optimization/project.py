#!/usr/bin/env python
from contextlib import contextmanager
from flow import FlowProject


# Set this variable to True to use a single space for all "simulations".
# By default, each simulation data space will be placed within the
# workspace of the corresponding optimization job.
USE_SHARED_SIMULATION_DATA_SPACE = False

# Use this variable to control the maximum number of generations that
# are generated for each optimization job.
MAX_NUM_GENERATIONS = 200


@contextmanager
def lock(job):
    job.doc.locked = True
    yield
    job.doc.locked = False


def locked(job):
    return job.doc.get('locked', False)


class SimulationProject(FlowProject):
    pass


@SimulationProject.label
def simulated(job):
    return job.doc.get('y') is not None


@SimulationProject.operation
@SimulationProject.pre(lambda job: not locked(job))
@SimulationProject.post(simulated)
def simulate(job):
    import math
    from time import sleep
    with lock(job):
        sleep(0.5)    # Artifical computational cost!!
        func = eval('lambda x: ' + job.sp.func, dict(sqrt=math.sqrt))
        job.doc.y = func(job.sp.x)


def calc_cost(job):
    return abs(job.doc.y)


if USE_SHARED_SIMULATION_DATA_SPACE:
    SIMULATION_SUB_PROJECT = SimulationProject.init_project(
        name='Simulate',
        root='simulations')


class OptimizationProject(FlowProject):
    pass


def get_simulation_sub_project(job):
    if USE_SHARED_SIMULATION_DATA_SPACE:
        return SIMULATION_SUB_PROJECT
    else:
        return SimulationProject.init_project(name='Simulate', root=job.fn('simulations'))


def get_simulation_sub_jobs(job, simulated=None):
    filter = {'func': job.sp.func} if USE_SHARED_SIMULATION_DATA_SPACE else None
    if simulated is None:
        doc_filter = None
    elif simulated is True or simulated is False:
        doc_filter = {'y': {'$exists': simulated}}
    else:
        raise ValueError(simulated)
    return get_simulation_sub_project(job).find_jobs(filter, doc_filter)


@OptimizationProject.label
def num_jobs(job):
    return '#jobs={}'.format(len(get_simulation_sub_jobs(job)))


@OptimizationProject.label
def cost_label(job):
    try:
        min_cost = min(map(calc_cost,
                           get_simulation_sub_jobs(job, simulated=True)))
        return "min-cost:{:0.3f}".format(min_cost)
    except ValueError:  # no jobs
        return "min-cost:n/a"


@OptimizationProject.label
def solution_label(job):
    sim_jobs_simulated = get_simulation_sub_jobs(job, simulated=True)
    for sim_job in sorted(sim_jobs_simulated, key=calc_cost):
        return 'solution:x={:0.5f}'.format(sim_job.sp.x)
    return 'solution:n/a'


@OptimizationProject.operation
@OptimizationProject.post.true('seeds')
def init_random_generator(job):
    import random
    random.seed(job.sp.seed)
    job.doc.seeds = [random.randint(1, 10000)]


@OptimizationProject.label
def exhausted(job):
    sim_jobs = get_simulation_sub_jobs(job)
    return len(sim_jobs) > MAX_NUM_GENERATIONS


@OptimizationProject.label
def converged(job):
    try:
        min_cost = min(map(calc_cost,
                           get_simulation_sub_jobs(job, simulated=True)))
        return min_cost < job.doc.max_cost
    except ValueError:  # no jobs
        return False


def all_simulated(job):
    return len(get_simulation_sub_jobs(job, simulated=False)) == 0


@OptimizationProject.operation
@OptimizationProject.pre.after(init_random_generator)
@OptimizationProject.pre(all_simulated)
@OptimizationProject.pre(lambda job: not exhausted(job))
@OptimizationProject.post(converged)
def spawn_new_simulations(job, n=4):
    import random
    random.seed(job.doc.seeds[-1])
    simulate_project = get_simulation_sub_project(job)
    for i in range(n):
        x = random.uniform(0, 4)
        simulate_project.open_job(dict(func=job.sp.func, x=x)).init()
    for i in range(5):
        next_seed = random.randint(0, 10000)
        if next_seed not in job.doc.seeds:
            job.doc.seeds = job.doc.seeds + [next_seed]
            break
    else:
        raise RuntimeError("Unable to determine next unique random seed.")


@OptimizationProject.operation
@OptimizationProject.post(all_simulated)
def run_simulations(job):
    get_simulation_sub_project(job).run(
        np=-1, progress=True)  # run on all available processors


if __name__ == '__main__':
    OptimizationProject().main()
