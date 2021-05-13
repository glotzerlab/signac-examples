from flow import FlowProject, aggregator, directives


class Project(FlowProject):
    pass


@Project.operation
@directives(nranks=lambda *jobs: 2 * len(jobs))
@aggregator.groupsof(8)
def do_mpi_task(*jobs):
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_jobs = len(jobs)
    print(f"Launching MPI tasks for {len(jobs)} jobs. " f"Rank {rank} of {size}.")

    # Use MPI splitting to make new communicators
    communicator_size = size // num_jobs
    color = rank // communicator_size
    key = rank % communicator_size
    print(f"{rank=}, {color=}, {key=}")

    split_comm = comm.Split(color, key)
    split_rank = split_comm.Get_rank()
    split_size = split_comm.Get_size()
    job = jobs[color]

    print(f"{rank=}, {split_rank=}, {split_size=}, {job=}")

    # Now you can use the split communicator with your application!
    # Call your function with job, split_comm


if __name__ == "__main__":
    Project().main()
