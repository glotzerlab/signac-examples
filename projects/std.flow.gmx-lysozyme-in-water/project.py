import signac
import flow
from flow import FlowProject
# import flow.environments  # uncomment to use default environments

import pexpect  # Used to automate interaction with GROMCAS interface.

gmx_exec = "gmx_mpi"  # Assumes mpi build
mpi_exec = "mpirun"

"""Define file level constants."""

# Configuration file names
pdb_file = 'protein.pdb'
fn_base = pdb_file.split('.')[0]
gro_file = fn_base + '.gro'
boxed_file = fn_base + '_newbox.gro'
solvated_file = fn_base + '_solv.gro'
ionized_file = fn_base + '_solv_ions.gro'
ionization_config = 'ions.tpr'

# Run file prefixes and names
em_op = 'minim'
nvt_op = 'nvt'
npt_op = 'npt'
production_op = 'md'

em_file = em_op + '.gro'
nvt_file = nvt_op + '.gro'
npt_file = npt_op + '.gro'
production_file = production_op + '.gro'

nvt_checkpoint = nvt_op + '.cpt'
npt_checkpoint = npt_op + '.cpt'

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


def workspace_command(cmd):
    """Simple command to always go to the workspace directory"""
    return ' && '.join([
        'cd {job.ws}',
        cmd if not isinstance(cmd, list) else ' && '.join(cmd),
        'cd ..',
    ])


def _grompp_str(op_name, gro_name, checkpoint_file=None):
    """Helper function, returns grompp command string for operation."""
    mdp_file = signac.get_project().fn('mdp_files/{op}.mdp'.format(op=op_name))
    cmd = '{gmx} grompp -f {mdp_file} -c {gro_file} {checkpoint} -o {op}.tpr -p'.format(
        gmx=gmx_exec, mdp_file=mdp_file, op=op_name, gro_file=gro_name,
        checkpoint='' if checkpoint_file is None else ('-t ' + checkpoint_file))
    return workspace_command(cmd)


def _mdrun_str(op_name, np=1, nt=None, verbose=False):
    """Helper function, returns mdrun command string for operation."""
    num_threads = 1 if nt is None else nt
    num_nodes = np // num_threads
    cmd = 'OMP_NUM_THREADS={num_threads} {mpi_exec} -n {np} {gmx} mdrun -ntomp {num_threads} {verbose} -deffnm {op}'.format(
          np=num_nodes, mpi_exec=mpi_exec, gmx=gmx_exec, num_threads=num_threads, op=op_name, verbose='-v' if verbose else '')
    return workspace_command(cmd)

# First three steps are simple configuration
@MyProject.operation
@MyProject.post.isfile(gro_file)
@flow.cmd
def pdb2gmx(job):
    return workspace_command(
        '{gmx} pdb2gmx -f {pdb_file} -o {gro_file} -water {water_model} '
        '-ff {force_field} -ignh'.format(
            gmx=gmx_exec, pdb_file=pdb_file, gro_file=gro_file,
            water_model=water_model, force_field=force_field))


@MyProject.operation
@MyProject.pre.after(pdb2gmx)
@MyProject.post.isfile(boxed_file)
@flow.cmd
def editconf(job):
    return workspace_command(
        '{gmx} editconf -f {gro_file} -o {boxed_file} -c -d {edge_spacing} '
        '-bt {box_type}'.format(
            gmx=gmx_exec, gro_file=gro_file, boxed_file=boxed_file,
            edge_spacing=edge_spacing, box_type=box_type))


@MyProject.operation
@MyProject.pre.isfile(boxed_file)
@MyProject.post.isfile(solvated_file)
@flow.cmd
def solvate(job):
    return workspace_command(
        '{gmx} solvate -cp {boxed_file} -cs {solvent_configuration} '
        '-o {solvated_file} -p'.format(
            gmx=gmx_exec, boxed_file=boxed_file,
            solvent_configuration=solvent_configuration,
            solvated_file=solvated_file))


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

@MyProject.operation
@MyProject.pre.isfile(solvated_file)
@MyProject.post.isfile(ionization_config)
@flow.cmd
def grompp_add_ions(job):
    return _grompp_str('ions', solvated_file)


@MyProject.operation
@MyProject.pre.after(grompp_add_ions)
@MyProject.post(prepared_for_simulation)
def ionize(job):
    """Exploit the pexpect module to run."""
    with job:
        cmd = "{gmx} genion -s {io_config} -o {ionized_gro} " \
            "-p -pname {pname} -nname {nname} -neutral".format(
                gmx=gmx_exec,
                io_config=ionization_config, ionized_gro=ionized_file,
                pname=pname, nname=nname)
        child = pexpect.spawn(cmd)
        child.expect('Select a group:*')
        child.send('13\n')
        print(child.before.decode('ascii'))
        print(child.after.decode('ascii'))
        child.expect(pexpect.EOF)
        print(child.before.decode('ascii'))


# Minimization
@MyProject.operation
@MyProject.pre(prepared_for_simulation)
@MyProject.post.isfile(em_op + '.tpr')
@flow.cmd
def grompp_minim(job):
    return _grompp_str('minim', ionized_file)


@MyProject.operation
@MyProject.pre.after(grompp_minim)
@MyProject.post.isfile(em_file)
@flow.cmd
def minim(job):
    return _mdrun_str('minim')


# Equilibration: NVT then NPT
@MyProject.operation
@MyProject.pre.after(minim)
@MyProject.post.isfile(nvt_op + '.tpr')
@flow.cmd
def grompp_nvt(job):
    return _grompp_str('nvt', em_file)


@MyProject.operation
@MyProject.pre.after(grompp_nvt)
@MyProject.post.isfile(nvt_file)
@flow.cmd
@flow.directives(np=16)
def nvt(job):
    return _mdrun_str('nvt')


@MyProject.operation
@MyProject.pre.after(nvt)
@MyProject.post.isfile(npt_op + '.tpr')
@flow.cmd
def grompp_npt(job):
    return _grompp_str('npt', nvt_file)


@MyProject.operation
@MyProject.pre.isfile(npt_op + '.tpr')
@MyProject.post.isfile(npt_file)
@flow.cmd
@flow.directives(np=16)
def npt(job):
    return _mdrun_str('npt')


# Final run
@MyProject.operation
@MyProject.pre.isfile(npt_file)
@MyProject.post.isfile(production_op + '.tpr')
@flow.cmd
def grompp_md(job):
    return _grompp_str('md', npt_file)


@MyProject.operation
@MyProject.pre.after(grompp_md)
@MyProject.post(finished)
@flow.cmd
@flow.directives(np=16)
def md(job):
    return _mdrun_str('md')


if __name__ == '__main__':
    MyProject().main()
