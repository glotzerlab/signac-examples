from flow import FlowProject


class Project(FlowProject):
    pass


@Project.label
def greeted(job):
    return job.isfile("hello.txt")


# Add hello world operation
@Project.post(greeted)
@Project.operation
def hello(job):
    print(f"Hello {job._id}")
    with job:
        with open("hello.txt", "w") as f:
            f.write(f"Hello {job._id}")


if __name__ == "__main__":
    Project().main()
