from flow import FlowProject
# import flow.environments  # uncomment to use default environments


class Project(FlowProject):

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    Project().main()
