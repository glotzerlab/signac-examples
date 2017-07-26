"""This module contains the operation functions for this project.

Functions defined in this module can be executed directly from the
command line with

    $ python src/operations.py {operation} [job_id [job_id ...]]

See also: $ python src/operations.py --help
"""


def initialize(job):
    "Initialize the simulation configuration."
    import hoomd
    from math import ceil
    if hoomd.context.exec_conf is None:
        hoomd.context.initialize('')
    with job:
        with hoomd.context.SimulationContext():
            n = int(ceil(pow(job.sp.N, 1.0/3)))
            assert n**3 == job.sp.N
            hoomd.init.create_lattice(unitcell=hoomd.lattice.sc(a=1.0), n=n)
            hoomd.dump.gsd('init.gsd', period=None, group=hoomd.group.all())


def estimate(job):
    "Ideal-gas estimate operation."
    sp = job.statepoint()
    # Calculate volume using ideal gas law
    V = sp['N'] * sp['kT'] / sp['p']
    job.document['volume_estimate'] = V


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
            md.integrate.npt(
                group=group, kT=job.sp.kT, tau=job.sp.tau,
                P=job.sp.p, tauP=job.sp.tauP)
            hoomd.analyze.log('dump.log', ['volume'], 100, phase=0)
            try:
                hoomd.run_upto(5000)
            except hoomd.WalltimeLimitReached:
                logging.warning("Reached walltime limit.")
            finally:
                gsd_restart.write_restart()
                job.document['sample_step'] = hoomd.get_step()


def auto(job):
    "This is a meta-operation to execute multiple operations."
    from project import MyProject
    import logging
    project = MyProject()
    logging.info("Running meta operation 'auto' for job '{}'.".format(job))
    for i in range(10):
        next_op = project.next_operation(job)
        if next_op is None:
            logging.info("No next operation, exiting.")
            break
        else:
            logging.info("Running next operation '{}'...".format(next_op))
            func = globals()[next_op.name]
            func(job)
    else:
        logging.warning("auto: Reached max # operations limit!")


if __name__ == '__main__':
    import flow
    flow.run()
