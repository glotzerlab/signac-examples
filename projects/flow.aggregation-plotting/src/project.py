import matplotlib.pyplot as plt
from flow import FlowProject, aggregator


class Project(FlowProject):
    pass


def get_pressure(crystal_name, density):
    """Pretend function returning a fake pressure value."""
    if crystal_name == "fcc":
        pressure = 1000 * density**2
    else:
        pressure = 5000 * density**3
    return pressure


@aggregator.groupby("crystal", sort_by="density")
@Project.operation
def plot_pressure_by_crystal(*jobs):
    """Plot the pressure as a function of density for each group."""
    pressures = {}
    for job in jobs:
        crystal_name = job.sp.crystal
        density = job.sp.density

        # In a real workflow, this data would come from a simulation.
        pressure = get_pressure(crystal_name, density)
        pressures[density] = pressure

        # Write an output file for each job.
        with open(job.fn("output.txt"), "w") as output_file:
            output_file.write(f"Pressure: {pressure}, Density: {density}")

    # Make the plot.
    fig, ax = plt.subplots()
    plt.plot(pressures.keys(), pressures.values())
    plt.title(f"{crystal_name} Density vs. Pressure")
    plt.savefig(f"{crystal_name}_density_vs_pressure.png")
    plt.close()


@aggregator(sort_by="density")
@Project.operation
def plot_pressure_all(*jobs):
    """Plot pressure for all data on the same axes."""
    crystal_pressures = {"fcc": [], "bcc": []}
    for job in jobs:
        crystal_name = job.sp.crystal
        density = job.sp.density

        # In a real workflow, this data would come from a simulation.
        pressure = get_pressure(crystal_name, density)
        crystal_pressures[crystal_name].append((density, pressure))

    # Make the plot.
    fig, ax = plt.subplots()
    for crystal_name, densities_and_pressures in crystal_pressures.items():
        densities = [v[0] for v in densities_and_pressures]
        pressures = [v[1] for v in densities_and_pressures]
        plt.plot(densities, pressures, label=crystal_name)
    plt.legend()
    plt.title("Density vs. Pressure")
    plt.savefig("density_vs_pressure.png")
    plt.close()


if __name__ == "__main__":
    Project().main()
