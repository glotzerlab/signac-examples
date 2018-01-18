"""Define the project's workflow logic.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
from flow import FlowProject
from flow import staticlabel
# import flow.environments  # uncomment to use default environments

# import environments # uncomment to use custom environments


class MyProject(FlowProject):

    # Definition of project-related labels (classification)

    @staticlabel()
    def initialized(job):
        return job.isfile('init.gsd')

    @staticlabel()
    def estimated(job):
        return 'volume_estimate' in job.document

    @staticlabel()
    def started(job):
        return job.document.get('sample_step', 0) > 0

    @staticlabel()
    def sampled(job):
        return job.document.get('sample_step', 0) >= 5000

    # Adding of project-related operations to the constructor (workflow)

    def __init__(self, *args, **kwargs):
        super(MyProject, self).__init__(*args, **kwargs)

        self.add_operation(
            name='initialize',
            cmd='python src/operations.py initialize {job._id}',
            post=[self.initialized])

        self.add_operation(
            name='estimate-volume',
            cmd='python src/operations.py estimate {job._id}',
            post=[self.estimated])

        self.add_operation(
            name='sample',
            cmd='python src/operations.py sample {job._id}',
            pre=[self.initialized],
            post=[self.sampled])

    # Overload functions for execution script generation (optional)

    def write_script_header(self, script, walltime=None, **kwargs):
        super(MyProject, self).write_script_header(script, walltime=walltime, **kwargs)

        # We want to use HOOMD-blue's walltime stop command in case
        # there is a walltime provided.
        if walltime is not None:
            walltime_seconds = 24 * 3600 * walltime.days + walltime.seconds
            script.writeline("# Ensure to stop hoomd in time...")
            script.writeline(
                'export HOOMD_WALLTIME_STOP=$((`date +%s` + {}))'.format(
                    int(0.9 * walltime_seconds)))


if __name__ == '__main__':
    MyProject().main()
