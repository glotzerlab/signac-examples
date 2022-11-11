from signac_dashboard import Dashboard
from signac_dashboard.modules import (
    DocumentList,
    ImageViewer,
    Notes,
    StatepointList,
    VideoViewer,
)


class MyDashboard(Dashboard):
    def job_title(self, job):
        return f"Total epochs={job.sp.epochs}, Learning rate={job.sp.lr}, Latent space dimension={job.sp.latent_dim}"

    def job_sorter(self, job):
        return (-job.sp.lr, job.sp.hidden_dim, job.sp.epochs)


if __name__ == "__main__":
    MyDashboard(
        modules=[
            ImageViewer(img_globs=["Loss.jpg"], name="Learning Curve"),
            ImageViewer(img_globs=["latent.jpg"], name="Latent Space"),
            ImageViewer(img_globs=["digits_recon.jpg"], name="Reconstructed"),
            ImageViewer(img_globs=["digits_orig.jpg"], name="Original"),
            StatepointList(),
            VideoViewer(),
            DocumentList(),
            Notes(),
        ]
    ).main()
