#!/usr/bin/env python
import flow
import hoomd
import hoomd.hpmc


def _setup_integrator(job):
    tuning = job.document.get('integrator', dict())
    mc = hoomd.hpmc.integrate.sphere(seed=job.sp.random_seed, **tuning)
    mc.shape_param.set('A', diameter=job.sp.diameter)
    return mc


def setup(job):
    with job:
        with hoomd.context.SimulationContext():
            hoomd.init.create_lattice(
                unitcell=hoomd.lattice.sq(a=job.sp.lattice.a), n=job.sp.n)
            hoomd.dump.gsd('init.gsd', period=None, group=hoomd.group.all())


def tune(job):
    with job:
        with hoomd.context.SimulationContext():
            hoomd.init.read_gsd('init.gsd', restart='restart.gsd')
            mc = _setup_integrator(job)
            tuner = hoomd.hpmc.util.tune(mc, ['d'], target=0.2)
            for i in range(10):
                hoomd.run(100)
                tuner.update()
            job.document['integrator'] = dict(d=mc.get_d())


def benchmark_tps(job):
    with job:
        with hoomd.context.SimulationContext():
            hoomd.init.read_gsd('init.gsd', restart='restart.gsd')
            _setup_integrator(job)
            tps = hoomd.benchmark.series(warmup=1e4, repeat=10, steps=1e3)
            TPS = job.document.get('TPS', dict())
            TPS[hoomd.comm.get_num_ranks()] = tps
            job.document['TPS'] = TPS


def benchmark_mps(job):
    with job:
        with hoomd.context.SimulationContext():
            hoomd.init.read_gsd('init.gsd', restart='restart.gsd')
            mc = _setup_integrator(job)
            hoomd.run(1e4)     # warmup
            mps = []
            for i in range(10):
                hoomd.run(1e3)
                mps.append(mc.get_mps())
            MPS = job.document.get('MPS', dict())
            MPS[hoomd.comm.get_num_ranks()] = mps
            job.document['MPS'] = MPS


def sample(job):
    with job:
        with hoomd.context.SimulationContext():
            hoomd.init.read_gsd('init.gsd', restart='restart.gsd')
            _setup_integrator(job)
            restart = hoomd.dump.gsd('restart.gsd', period=100, truncate=True, group=hoomd.group.all())
            hoomd.dump.gsd('trajectory.gsd', period=100, group=hoomd.group.all())
            hoomd.run_upto(1000)
            restart.write_restart()


if __name__ == '__main__':
    hoomd.context.initialize('--mode=cpu')
    flow.run()
