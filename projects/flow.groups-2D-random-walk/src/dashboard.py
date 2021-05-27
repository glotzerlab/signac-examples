"""Create a dashboard for viewing the jobs status."""

from signac_dashboard import Dashboard
from signac_dashboard.modules import DocumentList, FileList, ImageViewer, StatepointList

if __name__ == "__main__":
    Dashboard(
        modules=[ImageViewer(), DocumentList(), StatepointList(), FileList()]
    ).main()
