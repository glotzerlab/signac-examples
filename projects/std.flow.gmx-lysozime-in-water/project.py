import signac
from flow import FlowProject
from flow import staticlabel
# import flow.environments  # uncomment to use default environments

gmx_exec = "gmx_mpi"  # Assumes mpi build
mpi_exec = "mpirun"

"""Define file level constants"""
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


class Project(FlowProject):

    """Define labels"""
    @staticlabel()
    def converted_to_gmx(job):
        return job.isfile(gro_file)

    @staticlabel()
    def boxed(job):
        return job.isfile(boxed_file)

    @staticlabel()
    def solvated(job):
        return job.isfile(solvated_file)

    @staticlabel()
    def ionize_prepared(job):
        return job.isfile(ionization_config)

    @staticlabel()
    def ionized(job):
        return job.isfile(ionized_file)

    @staticlabel()
    def em_prepared(job):
        return job.isfile(em_op + '.tpr')

    @staticlabel()
    def minimized(job):
        return job.isfile(em_file)

    @staticlabel()
    def nvt_prepared(job):
        return job.isfile(nvt_op + '.tpr')

    @staticlabel()
    def nvt_equilibrated(job):
        return job.isfile(nvt_file)

    @staticlabel()
    def npt_prepared(job):
        return job.isfile(npt_op + '.tpr')

    @staticlabel()
    def npt_equilibrated(job):
        return job.isfile(npt_file)

    @staticlabel()
    def production_prepared(job):
        return job.isfile(production_op + '.tpr')

    @staticlabel()
    def finished(job):
        return job.isfile(production_file)

    """Definition of helper functions for defining operations"""

    def _grompp_str(self, op_name, gro_name, checkpoint_file=None):
        """Helper function, returns grompp command string for operation """
        mdp_file = signac.get_project().fn('mdp_files/{op}.mdp'.format(op=op_name))
        cmd = '{gmx} grompp -f {mdp_file} -c {gro_file} {checkpoint} -o {op}.tpr -p'.format(
            gmx=gmx_exec, mdp_file=mdp_file, op=op_name, gro_file=gro_name,
            checkpoint='' if checkpoint_file is None else ('-t ' + checkpoint_file))
        return cmd

    def _mdrun_str(self, op_name, np=1, nt=None, verbose=False):
        """Helper function, returns mdrun command string for operation """
        num_threads = 1 if nt is None else nt
        num_nodes = np // num_threads
        return 'OMP_NUM_THREADS={num_threads} {mpi_exec} -n {np} {gmx} mdrun -ntomp {num_threads} {verbose} -deffnm {op}'.format(
            np=num_nodes, mpi_exec=mpi_exec, gmx=gmx_exec, num_threads=num_threads, op=op_name, verbose='-v' if verbose else '')

    def add_workspace_operation(self, name, cmd, pre=[], post=[], np=1):
        """Simple extension of add operation to always go to the workspace directory"""
        command = ' && '.join([
            'cd {job.ws}',
            cmd if not isinstance(cmd, list) else ' && '.join(cmd),
            'cd ..',
        ])
        self.add_operation(
            name=name,
            cmd=command,
            pre=pre,
            post=post,
            np=np
        )

    def add_gromacs_run_op(self, name, structure_file, checkpoint_file=None,
                           pre_grompp=[], post_grompp=[], post_md=[], np=1, nt=1):
        """Helper function for any mdrun op requiring preprocessing with grompp"""
        self.add_workspace_operation(
            name='grompp_' + name,
            cmd=[self._grompp_str(name, structure_file, checkpoint_file)],
            pre=pre_grompp,
            post=post_grompp,
            np=1
        )
        self.add_workspace_operation(
            name=name,
            cmd=[self._mdrun_str(name, np=np, nt=nt)],
            pre=post_grompp,
            post=post_md,
            np=np
        )

    """Define the FlowProject"""

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)

        """Add operations required"""
        # First three steps are simple configuration
        self.add_workspace_operation(
            name='pdb2gmx',
            cmd='{gmx} pdb2gmx -f {pdb_file} -o {gro_file} -water {water_model} -ff {force_field} -ignh'.format(
                gmx=gmx_exec, pdb_file=pdb_file, gro_file=gro_file, water_model=water_model, force_field=force_field),
            post=[Project.converted_to_gmx],
        )

        self.add_workspace_operation(
            name='editconf',
            cmd='{gmx} editconf -f {gro_file} -o {boxed_file} -c -d {edge_spacing} -bt {box_type}'.format(
                gmx=gmx_exec, gro_file=gro_file, boxed_file=boxed_file, edge_spacing=edge_spacing, box_type=box_type),
            pre=[Project.converted_to_gmx],
            post=[Project.boxed],
        )

        self.add_workspace_operation(
            name='solvate',
            cmd='{gmx} solvate -cp {boxed_file} -cs {solvent_configuration} -o {solvated_file} -p'.format(
                gmx=gmx_exec, boxed_file=boxed_file, solvent_configuration=solvent_configuration, solvated_file=solvated_file),
            pre=[Project.boxed],
            post=[Project.solvated]
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
        self.add_workspace_operation(
            name='grompp_add_ions',
            cmd=self._grompp_str('ions', solvated_file),
            pre=[Project.solvated],
            post=[Project.ionize_prepared],
            np=1
        )
        self.add_operation(
            name='add_ions',
            cmd='python operations.py ionize {job._id}',
            pre=[Project.ionize_prepared],
            post=[Project.ionized],
            np=1
        )

        # Minimization
        self.add_gromacs_run_op(
            name=em_op,
            structure_file=ionized_file,
            pre_grompp=[Project.ionized],
            post_grompp=[Project.em_prepared],
            post_md=[Project.minimized]
        )

        # Equilibration: NVT then NPT
        self.add_gromacs_run_op(
            name=nvt_op,
            structure_file=em_file,
            pre_grompp=[Project.minimized],
            post_grompp=[Project.nvt_prepared],
            post_md=[Project.nvt_equilibrated],
            np=16
        )
        self.add_gromacs_run_op(
            name=npt_op,
            structure_file=nvt_file,
            checkpoint_file=nvt_checkpoint,
            pre_grompp=[Project.nvt_equilibrated],
            post_grompp=[Project.npt_prepared],
            post_md=[Project.npt_equilibrated],
            np=16
        )

        # Final run
        self.add_gromacs_run_op(
            name=production_op,
            structure_file=npt_file,
            checkpoint_file=npt_checkpoint,
            pre_grompp=[Project.npt_equilibrated],
            post_grompp=[Project.production_prepared],
            post_md=[Project.finished],
            np=16
        )


if __name__ == '__main__':
    Project().main()
