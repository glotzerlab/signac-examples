#!/usr/bin/env python3
from signac_dashboard import Dashboard
from signac_dashboard.modules import ImageViewer, StatepointList, TextDisplay


class MLDashboard(Dashboard):
    def job_title(self, job):
        estimator = job.sp.estimator
        return "{estimator}, C = {C}, gamma = {gamma}, {kernel} kernel".format(
            estimator=estimator, **job.sp.params
        )


def testing_accuracy(job):
    return round(job.doc.score, 4)


if __name__ == "__main__":
    modules = [
        StatepointList(),
        ImageViewer(),
        TextDisplay(name="Testing Accuracy", message=testing_accuracy),
    ]
    MLDashboard(modules=modules).main()
