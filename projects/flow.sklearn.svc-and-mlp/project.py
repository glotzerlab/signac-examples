import signac
from flow import FlowProject

project = signac.get_project()


class Project(FlowProject):
    pass


@Project.operation
@Project.pre.isfile("estimator.joblib")
@Project.post.isfile("confusion_matrix.png")
def plot_confusion_matrix(job):
    # Adapted from
    # https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    import joblib
    import matplotlib
    import matplotlib.pyplot as plt
    from sklearn.metrics import plot_confusion_matrix

    matplotlib.use("Agg")

    estimator = joblib.load(job.fn("estimator.joblib"))

    with project.data:
        # Re-fit estimator on full training data (not cross-validation subset)
        estimator.fit(project.data.X_train, project.data.y_train)
        job.doc.score = estimator.score(project.data.X_test, project.data.y_test)
        disp = plot_confusion_matrix(
            estimator=estimator,
            X=project.data.X_test,
            y_true=project.data.y_test,
            display_labels=project.doc.class_names,
            cmap=plt.cm.Blues,
            normalize="true",
        )
    disp.ax_.set_title("Confusion matrix")
    disp.figure_.savefig(job.fn("confusion_matrix.png"))


if __name__ == "__main__":
    Project().main()
