"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
from flow import FlowProject
# import flow.environments # uncomment to use default environments


class MyProject(FlowProject):
    pass

# Definition of project-related labels (classification)
@MyProject.label
def estimated(job):
    return 'volume_estimate' in job.document

@MyProject.label
def started(job):
    return job.document.get('sample_step', 0) > 0

@MyProject.label
def sampled(job):
    return job.document.get('sample_step', 0) >= job.sp.run_steps


# Adding project operations
@MyProject.operation
@MyProject.post.isfile('init.gsd')
def initialize(job):
    "Initialize the simulation configuration."
    import hoomd
    from math import ceil
    if hoomd.context.exec_conf is None:
        hoomd.context.initialize('')
    with job:
        with hoomd.context.SimulationContext():
            # create a simple cubic lattice
            n = int(ceil(pow(job.sp.N, 1.0/3)))
            assert n**3 == job.sp.N
            hoomd.init.create_lattice(unitcell=hoomd.lattice.sc(a=1.0), n=n)
            hoomd.dump.gsd('init.gsd', period=None, group=hoomd.group.all())


@MyProject.operation
@MyProject.pre.isfile('init.gsd')
@MyProject.post(sampled)
def sample(job):
    "Sample operation."
    import logging
    import hoomd
    from hoomd import md
    if hoomd.context.exec_conf is None:
        hoomd.context.initialize('')
    with job:
        with hoomd.context.SimulationContext():
            hoomd.init.read_gsd('init.gsd', restart='restart.gsd')
            group = hoomd.group.all()
            gsd_restart = hoomd.dump.gsd(
                'restart.gsd', truncate=True, period=100, phase=0, group=group)
            lj = md.pair.lj(r_cut=job.sp.r_cut, nlist=md.nlist.cell())
            lj.pair_coeff.set('A', 'A', epsilon=job.sp.epsilon, sigma=job.sp.sigma)
            md.integrate.mode_standard(dt=0.005)
            md.integrate.npt(group=group, kT=job.sp.kT, tau=job.sp.tau,
                             P=job.sp.p, tauP=job.sp.tauP)
            hoomd.analyze.log('dump.log', ['volume'], 100, phase=0)
            try:
                hoomd.run_upto(job.sp.run_steps)
            except hoomd.WalltimeLimitReached:
                logging.warning("Reached walltime limit.")
            finally:
                gsd_restart.write_restart()
                job.document['sample_step'] = hoomd.get_step()


@MyProject.operation
@MyProject.post(estimated)
def estimate(job):
    "Ideal-gas estimate operation."
    sp = job.statepoint()
    # Calculate volume using ideal gas law
    V = sp['N'] * sp['kT'] / sp['p']
    job.document['volume_estimate'] = V

if __name__ == '__main__':
    MyProject().main()
