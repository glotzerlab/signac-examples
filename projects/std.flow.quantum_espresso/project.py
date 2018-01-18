from flow import FlowProject
# import flow.environments  # uncomment to use default environments
from flow import staticlabel


class Project(FlowProject):

    @staticlabel()
    def converged(job):
        return 'ecut' in job.document

    @staticlabel()
    def calculated(job):
        return 'final_energy' in job.document

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self.add_operation(
             name='vc-relax',
             cmd='python operations.py vc_relax {job._id}',
             post=[self.converged])
        self.add_operation(
             name='scf',
             cmd='python operations.py scf {job._id}',
             pre=[self.converged],
             post=[self.calculated])


if __name__ == '__main__':
    Project().main()
