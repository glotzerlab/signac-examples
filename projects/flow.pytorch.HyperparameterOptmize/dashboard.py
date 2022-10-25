from signac_dashboard import Dashboard
from signac_dashboard.modules import (
    ImageViewer,
    StatepointList,
    VideoViewer,
    DocumentList,
)

class MyDashboard(Dashboard):
    def job_title(self, job):
        return f"Total epochs={job.sp.epochs}, Learning rate={job.sp.lr}, Latent space dimension={job.sp.latent_dim}"


if __name__ == "__main__":
    MyDashboard(
        modules=[ImageViewer(), StatepointList(), VideoViewer(), DocumentList()]
    ).main()
