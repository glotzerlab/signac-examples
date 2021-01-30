import joblib
import signac
from flow import FlowProject

project = signac.get_project()


class Project(FlowProject):
    pass


@Project.operation
@Project.pre.isfile("estimator.joblib")
@Project.post.isfile("estimator_fit.joblib")
def fit_estimator(job):
    estimator = joblib.load(job.fn("estimator.joblib"))

    with project.data:
        # Fit estimator on training data
        estimator.fit(project.data.X_train, project.data.y_train)

    # Save fitted model
    joblib.dump(estimator, job.fn("estimator_fit.joblib"))


@Project.operation
@Project.pre.after(fit_estimator)
@Project.post.isfile("confusion_matrix.png")
def plot_confusion_matrix(job):
    # See also:
    # https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    import matplotlib
    import matplotlib.pyplot as plt
    from sklearn.metrics import plot_confusion_matrix

    matplotlib.use("Agg")

    estimator = joblib.load(job.fn("estimator_fit.joblib"))

    with project.data:
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
