from flow import FlowProject
from flow import staticlabel
# import flow.environments  # uncomment to use default environments


class Project(FlowProject):

    @staticlabel()
    def greeted(job):
        return job.isfile('hello.txt')

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)

        # Add hello world operation
        self.add_operation(

            # The name of the operation (may be freely choosen)
            name='hello',

            # The command/script to be executed for this operation; any attribute of
            # job may be used as field:
            cmd='python operations.py hello {job._id}',

            # Alternatively, you can construct commands/scripts dynamically by providing a callable:
            # cmd=lambda job: "python operations.py hello {}".format(job),

            # A list of functions that represent requirements for the execution of this operation
            # for a specific job. The requirement is met when all functions return True.
            # An empty list means: 'No requirements.'
            pre=[],

            # A list of functions that represent whether this operation is 'completed' for a
            # specific job.
            # An empty list means that the operation is never considered 'completed'.
            post=[Project.greeted]

            # The number of processors required for this operation (may be a callable)
            # np = 1,
            )

if __name__ == '__main__':
    Project().main()
