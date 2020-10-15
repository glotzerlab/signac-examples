from flow import FlowProject

# import flow.environments  # uncomment to use default environments


class Project(FlowProject):
    pass


@Project.label
def greeted(job):
    return job.isfile("hello.txt")


# Add hello world operation
@Project.operation
@Project.post(greeted)
def hello(job):
    print("Hello {}".format(job._id))
    with job:
        with open("hello.txt", "w") as f:
            f.write("Hello {}".format(job._id))


if __name__ == "__main__":
    Project().main()
