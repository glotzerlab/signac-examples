import pexpect  # Used to automate interaction with GROMACS interface.
import signac
from flow import FlowProject

gmx_exec = "gmx"  # or use gmx_mpi if available

"""Define file level constants."""

# Configuration file names
pdb_file = "protein.pdb"
fn_base = pdb_file.split(".")[0]
gro_file = fn_base + ".gro"
boxed_file = fn_base + "_newbox.gro"
solvated_file = fn_base + "_solv.gro"
ionized_file = fn_base + "_solv_ions.gro"
ionization_config = "ions.tpr"

# Run file prefixes and names
em_op = "minim"
nvt_op = "nvt"
npt_op = "npt"
production_op = "md"

em_file = em_op + ".gro"
nvt_file = nvt_op + ".gro"
npt_file = npt_op + ".gro"
production_file = production_op + ".gro"

nvt_checkpoint = nvt_op + ".cpt"
npt_checkpoint = npt_op + ".cpt"

# pdb2gmx parameters
force_field = "oplsaa"
water_model = "spce"

# editconf parameters
box_type = "cubic"
edge_spacing = "1.0"

# solvate parameters
solvent_configuration = "spc216.gro"

# genion options
pname = "NA"
nname = "CL"


class MyProject(FlowProject):
    pass


"""Define labels, which in this case we use to indicate major checkpoints in the workflow."""


@MyProject.label
def prepared_for_simulation(job):
    """Indicates when the various preparation steps
    have been completed and the actual MD simulation
    steps can begin."""
    return job.isfile(ionized_file)


@MyProject.label
def finished(job):
    """Indicates that the entire workflow has completed
    for this operation."""
    return job.isfile(production_file)


"""Definition of helper functions for defining operations."""


def _grompp_str(op_name, gro_name, checkpoint_file=None):
    """Helper function, returns grompp command string for operation."""
    mdp_file = signac.get_project().fn(f"mdp_files/{op_name}.mdp")
    cmd = "{gmx} grompp -f {mdp_file} -c {gro_file} {checkpoint} -o {op}.tpr -p".format(
        gmx=gmx_exec,
        mdp_file=mdp_file,
        op=op_name,
        gro_file=gro_name,
        checkpoint="" if checkpoint_file is None else ("-t " + checkpoint_file),
    )
    return cmd


def _mdrun_str(op_name, nt=None, verbose=False):
    """Helper function, returns mdrun command string for operation."""
    num_threads = 1 if nt is None else nt
    cmd = ("{gmx} mdrun -ntomp {num_threads} {verbose} -deffnm {op}").format(
        gmx=gmx_exec,
        num_threads=num_threads,
        op=op_name,
        verbose="-v" if verbose else "",
    )
    return cmd


# First three steps are simple configuration
@MyProject.post.isfile(gro_file)
@MyProject.operation(cmd=True, with_job=True)
def pdb2gmx(job):
    return (
        "{gmx} pdb2gmx -f {pdb_file} -o {gro_file} -water {water_model} "
        "-ff {force_field} -ignh".format(
            gmx=gmx_exec,
            pdb_file=pdb_file,
            gro_file=gro_file,
            water_model=water_model,
            force_field=force_field,
        )
    )


@MyProject.pre.after(pdb2gmx)
@MyProject.post.isfile(boxed_file)
@MyProject.operation(cmd=True, with_job=True)
def editconf(job):
    return (
        "{gmx} editconf -f {gro_file} -o {boxed_file} -c -d {edge_spacing} "
        "-bt {box_type}".format(
            gmx=gmx_exec,
            gro_file=gro_file,
            boxed_file=boxed_file,
            edge_spacing=edge_spacing,
            box_type=box_type,
        )
    )


@MyProject.pre.isfile(boxed_file)
@MyProject.post.isfile(solvated_file)
@MyProject.operation(cmd=True, with_job=True)
def solvate(job):
    return (
        "{gmx} solvate -cp {boxed_file} -cs {solvent_configuration} "
        "-o {solvated_file} -p".format(
            gmx=gmx_exec,
            boxed_file=boxed_file,
            solvent_configuration=solvent_configuration,
            solvated_file=solvated_file,
        )
    )


# genion requires a binary topology file (the tpr file)
# In order to provide one, we use grompp to generate it.
# Most of the run parameters here are unimportant, since
# we are not actually going to run a simulation, we just
# have to make sure that the topology has the correct
# interaction parameters so that the resulting topology
# will accurately model water molecules
# The grompp here is split because the ionization uses a
# python operation to leverage the pexpect class to
# automate responding to requested std input


@MyProject.pre.isfile(solvated_file)
@MyProject.post.isfile(ionization_config)
@MyProject.operation(cmd=True, with_job=True)
def grompp_add_ions(job):
    return _grompp_str("ions", solvated_file).format(job)


@MyProject.pre.after(grompp_add_ions)
@MyProject.post(prepared_for_simulation)
@MyProject.operation(with_job=True)
def ionize(job):
    """Exploit the pexpect module to run."""
    cmd = (
        "{gmx} genion -s {io_config} -o {ionized_gro} "
        "-p -pname {pname} -nname {nname} -neutral".format(
            gmx=gmx_exec,
            io_config=ionization_config,
            ionized_gro=ionized_file,
            pname=pname,
            nname=nname,
        )
    )
    child = pexpect.spawn(cmd)
    child.expect("Select a group:*")
    child.send("13\n")
    print(child.before.decode("ascii"))
    print(child.after.decode("ascii"))
    child.expect(pexpect.EOF)
    print(child.before.decode("ascii"))


# Minimization
@MyProject.pre(prepared_for_simulation)
@MyProject.post.isfile(em_op + ".tpr")
@MyProject.operation(cmd=True, with_job=True)
def grompp_minim(job):
    return _grompp_str("minim", ionized_file).format(job)


@MyProject.pre.after(grompp_minim)
@MyProject.post.isfile(em_file)
@MyProject.operation(cmd=True, with_job=True)
def minim(job):
    return _mdrun_str("minim").format(job)


# Equilibration: NVT then NPT
@MyProject.pre.after(minim)
@MyProject.post.isfile(nvt_op + ".tpr")
@MyProject.operation(cmd=True, with_job=True)
def grompp_nvt(job):
    return _grompp_str("nvt", em_file).format(job)


@MyProject.pre.after(grompp_nvt)
@MyProject.post.isfile(nvt_file)
@MyProject.operation(cmd=True, directives={"np": 16}, with_job=True)
def nvt(job):
    return _mdrun_str("nvt").format(job)


@MyProject.pre.after(nvt)
@MyProject.post.isfile(npt_op + ".tpr")
@MyProject.operation(cmd=True, with_job=True)
def grompp_npt(job):
    return _grompp_str("npt", nvt_file).format(job)


@MyProject.pre.isfile(npt_op + ".tpr")
@MyProject.post.isfile(npt_file)
@MyProject.operation(cmd=True, directives={"np": 16}, with_job=True)
def npt(job):
    return _mdrun_str("npt").format(job)


# Final run
@MyProject.pre.isfile(npt_file)
@MyProject.post.isfile(production_op + ".tpr")
@MyProject.operation(cmd=True, with_job=True)
def grompp_md(job):
    return _grompp_str("md", npt_file).format(job)


@MyProject.pre.after(grompp_md)
@MyProject.post(finished)
@MyProject.operation(cmd=True, directives={"nranks": 4, "omp_num_threads": 4}, with_job=True)
def md(job):
    return _mdrun_str("md", nt=4).format(job)


if __name__ == "__main__":
    MyProject().main()
