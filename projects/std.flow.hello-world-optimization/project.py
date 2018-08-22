#!/usr/bin/env python
from functools import wraps

from flow import FlowProject


# Use this variable to control the maximum number of generations that
# are generated for each optimization job.
MAX_NUM_GENERATIONS = 200


class SimulationProject(FlowProject):
    pass


@SimulationProject.label
def simulated(job):
    return job.doc.get('y') is not None


@SimulationProject.operation
@SimulationProject.pre(lambda job: 'max_cost' not in job.doc)
@SimulationProject.post(simulated)
def simulate(job):
    import math
    from time import sleep
    sleep(0.5)    # Artifical computational cost!!
    func = eval('lambda x: ' + job.sp.func, dict(sqrt=math.sqrt))
    job.doc.y = func(job.sp.x)


def calc_cost(job):
    return abs(job.doc.y)


class OptimizationProject(SimulationProject):
    pass

    @staticmethod
    def is_master(job):
        return 'max_cost' in job.doc

    @classmethod
    def label(cls, func, *args, **kwargs):

        @wraps(func)
        def _inner_label_func(job):
            if cls.is_master(job):
                return func(job)
        return FlowProject.label(_inner_label_func, *args, **kwargs)

    @classmethod
    def operation(cls, func, *args, **kwargs):
        return cls.pre(lambda job: cls.is_master(job))(FlowProject.operation(func, *args, **kwargs))


def get_simulation_sub_jobs(job, simulated=None):
    "Determine all simulation jobs, belonging to this master-job."
    filter = {'func': job.sp.func}
    doc_filter = {'max_cost': {'$exists': False}}
    if simulated is True or simulated is False:
        doc_filter['y'] = {'$exists': simulated}
    elif simulated is not None:
        raise ValueError(simulated)
    return job._project.find_jobs(filter, doc_filter)


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
    if 'max_cost' in job.doc:
        try:
            min_cost = min(map(calc_cost,
                               get_simulation_sub_jobs(job, simulated=True)))
            return min_cost < job.doc.max_cost
        except ValueError:  # no jobs
            return False


@OptimizationProject.label
def all_simulated(job):
    if 'max_cost' in job.doc:
        return len(get_simulation_sub_jobs(job, simulated=False)) == 0


@OptimizationProject.operation
@OptimizationProject.pre.after(init_random_generator)
@OptimizationProject.pre(all_simulated)
@OptimizationProject.pre(lambda job: not exhausted(job))
@OptimizationProject.post(converged)
def spawn_new_simulations(job, n=4):
    import random
    random.seed(job.doc.seeds[-1])
    project = job._project
    for i in range(n):
        x = random.uniform(0, 4)
        project.open_job(dict(func=job.sp.func, x=x)).init()
    for i in range(5):
        next_seed = random.randint(0, 10000)
        if next_seed not in job.doc.seeds:
            job.doc.seeds = job.doc.seeds + [next_seed]
            break
    else:
        raise RuntimeError("Unable to determine next unique random seed.")


if __name__ == '__main__':
    OptimizationProject().main()
