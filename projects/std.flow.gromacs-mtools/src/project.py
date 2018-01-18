"""Define the project's workflow logic."""
from flow import FlowProject
from flow import staticlabel
import environment  # Custom environment definition


def _grompp_str(root, op_name, gro_name, sys_name):
    """Helper function, returns grompp command string for operation """
    cmd = ('gmx grompp -f {root}/src/util/mdp_files/{op}.mdp -c {gro}.gro '
           '-p {sys}.top -o {op}.tpr')
    return cmd.format(root=root, op=op_name, gro=gro_name, sys=sys_name)


def _mdrun_str(op_name):
    """Helper function, returns mdrun command string for operation """
    return 'gmx mdrun -v -deffnm {0} -nt 12 -cpi {0}.cpt'.format(op_name)


class MyProject(FlowProject):

    @staticlabel()
    def initialized(job):
        return job.isfile('init.top')

    @staticlabel()
    def minimized(job):
        return job.isfile('em.gro')

    @staticlabel()
    def equilibrated(job):
        return job.isfile('equil.gro')

    @staticlabel()
    def sampled(job):
        return job.isfile('sample.gro')

    def __init__(self, *args, **kwargs):
        super(MyProject, self).__init__(*args, **kwargs)

        def add_gromacs_op(name, gro, sys, **kwargs):
            self.add_operation(
                name=name,
                cmd="cd {{job.ws}} ; {} && {}".format(
                    _grompp_str(self.root_directory(), name, gro, sys),
                    _mdrun_str(name)),
                **kwargs)

        self.add_operation(
            name='initialize',
            cmd='python src/operations.py initialize {job._id}',
            post=[self.initialized])

        add_gromacs_op(
            name='em', gro='init', sys='init',
            pre=[self.initialized],
            post=[self.minimized])

        add_gromacs_op(
            name='equil', gro='em', sys='init',
            pre=[self.minimized],
            post=[self.equilibrated])

        add_gromacs_op(
            name='sample', gro='equil', sys='init',
            pre=[self.equilibrated],
            post=[self.sampled])

    def write_script_header(self, script, **kwargs):
        super().write_script_header(script, **kwargs)
        script.writeline('module load gromacs/5.1.4')


if __name__ == '__main__':
    MyProject().main()
