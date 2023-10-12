from flow import FlowProject, aggregator


class Project(FlowProject):
    pass


RANKS_PER_JOB = 2
JOBS_PER_AGGREGATE = 2


def mpi_task(job, comm):
    """Does some work for a signac job with a given MPI communicator."""
    size = comm.Get_size()
    rank = comm.Get_rank()
    # Broadcast the state point to all ranks
    if rank == 0:
        data = job.statepoint()
    else:
        data = None
    data = comm.bcast(data, root=0)
    print(f"In the mpi_task function, {rank=} of {size=} has {data=}.")


mpi_aggregator = aggregator.groupsof(num=JOBS_PER_AGGREGATE)

@Project.operation(
    aggregator=mpi_aggregator,
    directives={"nranks": lambda *jobs: RANKS_PER_JOB * len(jobs)},
)
def do_mpi_task(*jobs):
    from mpi4py import MPI

    world_comm = MPI.COMM_WORLD
    world_rank = world_comm.Get_rank()
    world_size = world_comm.Get_size()
    num_jobs = len(jobs)
    if world_rank == 0:
        print(
            f"Launching MPI tasks for {len(jobs)} jobs. Rank {world_rank} of {world_size}."
        )

    # Use MPI splitting to make new communicators
    communicator_size = world_size // num_jobs
    color = world_rank // communicator_size
    key = world_rank % communicator_size
    print(f"{world_rank=}, {color=}, {key=}")

    split_comm = world_comm.Split(color, key)
    split_rank = split_comm.Get_rank()
    split_size = split_comm.Get_size()

    # Select the job from the aggregate to run in the split communicator.
    job = jobs[color]

    print(f"{world_rank=}, {split_rank=}, {split_size=}, {job.statepoint=}")

    # Now you can use the split communicator with your application!
    # Call your function with job, split_comm:
    mpi_task(job, split_comm)


if __name__ == "__main__":
    Project().main()
