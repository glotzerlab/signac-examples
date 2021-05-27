"""Define the operations for the 2D Gaussian Random Walk project."""

import flow
import matplotlib.pyplot as plt
import numpy as np


# Helper functions
def get_replica(jobs, replica):
    """Get a certain replica from a group of jobs."""
    try:
        job = next(filter(lambda job: job.sp.replica == replica, jobs))
    except StopIteration:
        raise RuntimeError(f"No replica {replica} found.")
    return job


def generate_stores(jobs, store_name):
    """Yield a data store for each job in jobs."""
    for job in jobs:
        with job.data:
            yield job.data[store_name]


class RandomWalkProject(flow.FlowProject):
    """Create a workflow for simulating 2D Gaussian random walks."""

    pass


@RandomWalkProject.label
def simulated(job):
    """Return whether the job simulated."""
    return "positions" in job.data


def all_simulated(*jobs):
    """Return whether all jobs simulated."""
    return all(simulated(job) for job in jobs)


# Operations on individual jobs

# Group for operations on single jobs that are reachable from simulate
base = RandomWalkProject.make_group("base")


@base
@RandomWalkProject.post(simulated)
@RandomWalkProject.operation
def simulate(job):
    """Simulate a 2D random walk."""
    # use job id as random seed
    n_steps = job.doc.run_steps
    generator = np.random.default_rng(int(job.id, 16))
    # Generate all moves at once since they are independent
    moves = generator.normal(job.sp.mean, job.sp.standard_deviation, (n_steps, 2))
    position = np.zeros((n_steps + 1, 2), dtype=float)
    # Store the results: cumsum aggregates all previous moves from the origin
    position[1:] = np.cumsum(moves, axis=0)
    job.data.positions = position


@base
@RandomWalkProject.pre.after(simulate)
@RandomWalkProject.post.true("radius_of_gyration")
@RandomWalkProject.operation
def compute_radius_of_gyration(job):
    """Compute the radius of gyration for a random walk."""
    with job.data:
        positions = job.data["positions"][:]
    avg_position = positions.mean(axis=0)
    deviation = positions - avg_position
    job.doc.radius_of_gyration = np.sqrt(
        np.sum(deviation * deviation) / deviation.shape[0]
    )
    job.doc.average_position = avg_position


@base
@RandomWalkProject.pre.after(simulate)
@RandomWalkProject.post.true("end_to_end")
@RandomWalkProject.operation
def compute_end_to_end_distance(job):
    """Compute the radius of gyration for a random walk."""
    with job.data:
        positions = job.data["positions"]
        job.doc["end_to_end"] = np.linalg.norm(positions[-1] - positions[0])


@base
@RandomWalkProject.pre.after(simulate)
@RandomWalkProject.post(lambda job: "squared_distance" in job.data)
@RandomWalkProject.operation
def compute_squared_distance(job):
    """Compute the squared distance for a random walk."""
    with job.data:
        positions = job.data.positions[:]
    job.data.squared_distance = np.sum(positions * positions, axis=1)


# This operation happens after computing the msd so it isn't in base.
# Also we use pre as a filter for jobs ensuring this job only ever runs on the zeroth
# replica for a given standard deviation.
@RandomWalkProject.pre.true("msd_analyzed")
@RandomWalkProject.pre(lambda job: job.sp.replica == 0)
@RandomWalkProject.post.isfile("msd.png")
@RandomWalkProject.operation
def plot_msd(job):
    """Plot the MSD for all std."""
    with job.data:
        msd = job.data.msd[:]
    fig, ax = plt.subplots()
    ax.plot(msd)
    ax.set_title(f"MSD for {job.sp.standard_deviation} std")
    ax.set_xlabel("x")
    ax.set_ylabel("MSD")
    # Only save figure to the first replica
    fig.savefig(job.fn("msd.png"))
    fig.close()


# Aggregate operations on individual standard deviations across replicas

# Create aggregator that combines all replicas with a single standard deviation
std_aggregator = flow.aggregator.groupby("standard_deviation")


# Define all aggregate groups
agg_plot = RandomWalkProject.make_group(
    "aggregate-plot", group_aggregator=std_aggregator
)
agg_analyze_and_plot = RandomWalkProject.make_group(
    "post-processing", group_aggregator=std_aggregator
)


@agg_analyze_and_plot
@std_aggregator
@RandomWalkProject.pre(all_simulated)
@RandomWalkProject.post.true("msd_analyzed")
@RandomWalkProject.operation
def compute_mean_squared_distance(*jobs):
    """Compute and store the mean squared displacement for all std."""
    squared_distance_iterator = generate_stores(jobs, "squared_distance")
    squared_distance = next(squared_distance_iterator)
    msd = np.copy(squared_distance)
    for squared_distance in squared_distance_iterator:
        msd += squared_distance
    msd /= len(jobs)
    # Store msd in only first replica (job.sp.replica == 1)
    job_replica_zero = get_replica(jobs, replica=0)
    job_replica_zero.data["msd"] = msd
    for job in jobs:
        job.doc.msd_analyzed = True


# Since this uses a separate aggragator to restrict aggregates to the first 5 replicas,
# we cannot assign this operation to either agg_plot or agg_analyze_and_plot
@flow.aggregator.groupby("standard_deviation", select=lambda job: job.sp.replica <= 4)
@RandomWalkProject.pre(all_simulated)
@RandomWalkProject.post.true("plotted_walks")
@RandomWalkProject.operation
def plot_walk(*jobs):
    """Plot the first 5 replicas random walks for each standard_deviation."""
    fig, ax = plt.subplots()
    for position, job in zip(generate_stores(jobs, "positions"), jobs):
        ax.plot(position[:, 0], position[:, 1], label=f"Replica {job.sp.replica}")
    ax.legend()
    ax.set_title(
        f"Random Walks with {jobs[0].sp.standard_deviation} standard_deviation"
    )
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    # Only save figure to the first replica
    fig.savefig(get_replica(jobs, replica=0).fn("random-walks.png"))
    fig.close()
    for job in jobs:
        job.doc.plotted_walks = True


@agg_analyze_and_plot
@agg_plot
@std_aggregator
@RandomWalkProject.pre(all_simulated)
@RandomWalkProject.post.true("plotted_histogram")
@RandomWalkProject.operation
def plot_histogram(*jobs):
    """Create a 2D histogram of the final positions of random walks per std."""
    final_positions = np.array(
        [position[-1] for position in generate_stores(jobs, "positions")]
    )
    histogram, x_bins, y_bins = np.histogram2d(
        final_positions[:, 0], final_positions[:, 1]
    )
    fig, ax = plt.subplots()
    image = ax.imshow(
        histogram, extent=[x_bins[0], x_bins[-1], y_bins[0], y_bins[-1]], cmap="viridis"
    )
    plt.colorbar(image)
    ax.set_title("Heatmap of Final Positions")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.savefig(get_replica(jobs, replica=0).fn("histogram.png"))
    fig.close()
    for job in jobs:
        job.doc.plotted_histogram = True


if __name__ == "__main__":
    RandomWalkProject().main()
