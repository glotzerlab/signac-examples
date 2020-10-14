import signac
import hoomd
import hoomd.md

project = signac.init_project("hoomd-lennard-jones")

for kT in (0.1, 1.0, 2.0):
    with project.open_job({"kT": kT, "seed": 42}) as job:
        hoomd.context.initialize()
        hoomd.init.create_lattice(unitcell=hoomd.lattice.sc(a=2.0), n=5)
        nl = hoomd.md.nlist.cell()
        lj = hoomd.md.pair.lj(r_cut=2.5, nlist=nl)
        lj.pair_coeff.set("A", "A", epsilon=1.0, sigma=1.0)
        hoomd.md.integrate.mode_standard(dt=0.005)
        all = hoomd.group.all()
        hoomd.md.integrate.langevin(group=all, kT=job.sp.kT, seed=job.sp.seed)
        hoomd.analyze.log(
            filename="log-output.log",
            quantities=["potential_energy", "temperature", "pressure"],
            period=100,
            overwrite=True,
        )
        hoomd.dump.gsd("trajectory.gsd", period=2e3, group=all, overwrite=True)
        hoomd.run(1e4)
