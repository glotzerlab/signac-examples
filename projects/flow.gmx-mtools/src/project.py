"""Define the project's workflow logic."""
import mbuild as mb
import signac
from flow import FlowProject

project_path = signac.get_project().path


def _grompp_str(path, op_name, gro_name, sys_name):
    """Helper function, returns grompp command string for operation"""
    cmd = (
        "gmx grompp -f {path}/mdp_files/{op}.mdp -c {gro}.gro "
        "-p {sys}.top -o {op}.tpr"
    )
    return cmd.format(path=path, op=op_name, gro=gro_name, sys=sys_name)


def _mdrun_str(op_name):
    """Helper function, returns mdrun command string for operation"""
    return "gmx mdrun -v -deffnm {0} -nt 12 -cpi {0}.cpt".format(op_name)


def gromacs_command(name, gro, sys):
    """Simplify GROMACS operations"""
    return "{} && {}".format(
        _grompp_str(project_path, name, gro, sys),
        _mdrun_str(name),
    )


class MyProject(FlowProject):
    pass


@MyProject.label
def initialized(job):
    return job.isfile("init.top")


@MyProject.label
def minimized(job):
    return job.isfile("em.gro")


@MyProject.label
def equilibrated(job):
    return job.isfile("equil.gro")


@MyProject.label
def sampled(job):
    return job.isfile("sample.gro")


@MyProject.post(initialized)
@MyProject.operation(with_job=True)
def initialize(job):
    """Initialize the simulation."""
    alkane = mb.recipes.Alkane(job.statepoint()["C_n"])
    n_alkane = 200
    # A cleaner packing approach would involve pull #372
    system_box = mb.Box([4, 4, 4])
    system = mb.fill_box(compound=alkane, n_compounds=n_alkane, box=system_box)
    system.save("init.gro", overwrite=True)
    system.save("init.top", forcefield_name="oplsaa", overwrite=True)


@MyProject.pre(initialized)
@MyProject.post(minimized)
@MyProject.operation(cmd=True, with_job=True)
def em(job):
    return gromacs_command(name="em", gro="init", sys="init").format(job)


@MyProject.pre(minimized)
@MyProject.post(equilibrated)
@MyProject.operation(cmd=True, with_job=True)
def equil(job):
    return gromacs_command(name="equil", gro="em", sys="init").format(job)


@MyProject.pre(equilibrated)
@MyProject.post(sampled)
@MyProject.operation(cmd=True, with_job=True)
def sample(job):
    return gromacs_command(name="sample", gro="equil", sys="init").format(job)


if __name__ == "__main__":
    MyProject.get_project(project_path).main()
