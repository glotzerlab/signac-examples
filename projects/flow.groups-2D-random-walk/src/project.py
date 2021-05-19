import flow
import matplotlib.pyplot as plt
import numpy as np


# Helper functions
def get_first_replica(jobs, first_index=1):
    try:
        job = next(filter(lambda job: job.sp.replica == first_index, jobs))
    except StopIteration:
        raise RuntimeError("First replica not found.")
    return job


def positions_generator(jobs):
    for job in jobs:
        with job.data:
            yield job.data.positions


def aggregate_cond_true(doc_attr):
    """Create a condition which is true if all jobs have doc_attr as truthy."""
    def true_for_all_docs(*jobs):
        return all(job.doc.get(doc_attr, False) for job in jobs)

    return true_for_all_docs


class Project(flow.FlowProject):
    """Create a workflow for simulating 2D Gaussian random walks."""
    pass


@Project.label
def simulated(job):
    return "positions" in job.data


def all_simulated(*jobs):
    return all(simulated(job) for job in jobs)


# Define all groups
# -----------------
plot = Project.make_group("aggregate-plot")
analyze_and_plot = Project.make_group("post-processing")


@Project.post(simulated)
@Project.operation
def simulate(job):
    """Simulate a 2D random walk."""
    # use job id as random seed
    n_steps = job._project.doc.run_steps
    generator = np.random.default_rng(int(job.id, 16))
    # Generate all moves at once since they are independent
    moves = generator.normal(
        job.sp.mean, job.sp.std, (n_steps, 2))
    position = np.empty((n_steps + 1, 2), dtype=float)
    position[0, :] = [0, 0]
    # Store the results: cumsum aggregates all previous moves from the origin
    position[1:] = np.cumsum(moves, axis=0)
    job.data.positions = position


@analyze_and_plot
@flow.aggregator.groupby("std")
@Project.pre(all_simulated)
@Project.post(aggregate_cond_true("msd_analyzed"))
@Project.operation
def analyze_mean_squared_distance(*jobs):
    """Compute and store the mean squared displacement for all std."""
    msd = np.zeros((jobs[0]._project.doc.run_steps + 1), dtype=float)
    for position in positions_generator(jobs):
        msd += np.sum(np.multiply(position, position), axis=1)
    msd /= len(jobs)
    # Store msd in only first replica (job.sp.replica == 1)
    get_first_replica(jobs).data["msd"] = msd
    for job in jobs:
        job.doc.msd_analyzed = True


@Project.pre.true("msd_analyzed")
@Project.pre(lambda job: job.sp.replica == 1)
@Project.post.isfile("msd.png")
@Project.operation
def plot_mean_squared_distance(job):
    """Plot the MSD for all std."""
    with job.data:
        msd = job.data.msd[:]
    fig, ax = plt.subplots()
    ax.plot(msd)
    ax.set_title(f"MSD for {job.sp.std} std")
    ax.set_xlabel("x")
    ax.set_ylabel("MSD")
    # Only save figure to the first replica
    fig.savefig(job.fn("msd.png"))


@analyze_and_plot
@plot
@flow.aggregator.groupby("std", select=lambda job: job.sp.replica <= 5)
@Project.pre(all_simulated)
@Project.post(aggregate_cond_true("plotted_walks"))
@Project.operation
def plot_walk(*jobs):
    """Plot the first 5 replicas random walks for each std."""
    fig, ax = plt.subplots()
    for position, job in zip(positions_generator(jobs), jobs):
        ax.plot(
            position[:, 0], position[:, 1], label=f"Replica {job.sp.replica}")
    ax.legend()
    ax.set_title(f"Random Walks with {jobs[0].sp.std} std")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    # Only save figure to the first replica
    fig.savefig(get_first_replica(jobs).fn("random-walks.png"))
    for job in jobs:
        job.doc.plotted_walks = True


@analyze_and_plot
@plot
@flow.aggregator.groupby("std")
@Project.pre(all_simulated)
@Project.post(aggregate_cond_true("plotted_histogram"))
@Project.operation
def plot_histogram(*jobs):
    """Create a 2D histogram of the final positions of random walks per std."""
    final_positions = np.array(
        [position[-1] for position in positions_generator(jobs)])
    histogram, x_bins, y_bins = np.histogram2d(
        final_positions[:, 0], final_positions[:, 1])
    fig, ax = plt.subplots()
    image = ax.imshow(
        histogram, extent=[x_bins[0], x_bins[-1], y_bins[0], y_bins[-1]],
        cmap="viridis")
    plt.colorbar(image)
    ax.set_title("Heatmap of Final Positions")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.savefig(get_first_replica(jobs).fn("histogram.png"))
    for job in jobs:
        job.doc.plotted_histogram = True


if __name__ == "__main__":
    Project().main()