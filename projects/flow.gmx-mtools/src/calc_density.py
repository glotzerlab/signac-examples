"""Calculates the density of a system over the length of a trajectory"""
import os

from mtools.post_process import calc_density
import signac

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt

import numpy as np
import mdtraj as md


project = signac.get_project()

for job in project.find_jobs():
    top_file = os.path.join(job.workspace(), "sample.gro")
    trj_file = os.path.join(job.workspace(), "sample.trr")
    data_file = os.path.join(job.workspace(), "rho.txt")
    img_file = os.path.join(job.workspace(), "rho.pdf")
    if os.path.isfile(top_file) and os.path.isfile(trj_file):
        trj = md.load(trj_file, top=top_file)
        rho = calc_density(trj, units="macro")
        data = np.vstack([trj.time, rho])
        np.savetxt(
            data_file, np.transpose(data), header="# Time (ps)\tDensity (kg/m^3)"
        )
        fig, ax = plt.subplots()
        ax.plot(trj.time, rho)
        ax.set_xlabel("Simulation time (ps)")
        ax.set_ylabel("Density (kg/m^3)")
        ax.set_title("Box of C_{}".format(job.statepoint()["C_n"]))
        fig.savefig(img_file)

fig, ax = plt.subplots()
for job in project.find_jobs():
    data_file = os.path.join(job.workspace(), "rho.txt")
    if os.path.isfile(data_file):
        data = np.loadtxt(data_file)
        t = data[:, 0]
        rho = data[:, 1]

        try:
            import block_avg as ba
        except ImportError:
            ba = None
            pass

        if ba:
            t_b, t_std = ba.block_avg(t, 50)
            rho_b, rho_std = ba.block_avg(rho, 50)
            t_b = t_b.reshape(-1)
            t_std = t_std.reshape(-1)
            rho_b = rho_b.reshape(-1)
            rho_std = rho_std.reshape(-1)
            (myline,) = ax.plot(
                t_b,
                rho_b,
                marker="o",
                markersize=5,
                label="C_{}".format(job.statepoint()["C_n"]),
            )
            ax.fill_between(
                t_b,
                rho_b - rho_std,
                rho_b + rho_std,
                alpha=0.2,
                facecolor=myline.get_color(),
            )
        else:
            (myline,) = ax.plot(
                t, rho, marker="o", markersize=5, label=job.statepoint()["C_n"]
            )
ax.set_xlabel("Simulation time (ps)")
ax.set_ylabel("Density (kg/m^3)")
ax.legend(title="Alkane length", loc="lower right", fontsize="x-small")
fig.savefig(os.path.join(project.workspace(), "rho-summary.pdf"))
