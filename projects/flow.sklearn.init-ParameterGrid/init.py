"""This example performs grid search, saving the results of each evaluated
parameter set into a signac data space.

See also:
https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html
"""
import joblib
import signac
from sklearn import datasets, svm
from sklearn.model_selection import ParameterGrid, train_test_split


if __name__ == '__main__':
    # Load sample data
    dataset = datasets.load_digits()
    X = dataset.data
    y = dataset.target
    class_names = dataset.target_names.tolist()

    # Split the data into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.5, random_state=0)

    # Initialize the signac project and save the training/testing data into the
    # project's HDF5 data store
    project = signac.init_project('gridsearch')
    with project.data:
        project.data.X_train = X_train
        project.data.X_test = X_test
        project.data.y_train = y_train
        project.data.y_test = y_test

    # Class names are non-numeric so they go into the project document.
    project.doc.class_names = class_names

    param_grid = {
        'kernel': ('linear', 'rbf'),
        'C': (0.1, 1, 10, 100),
        'gamma': ('scale',)
    }

    # Create the jobs for each estimator
    for params in ParameterGrid(param_grid):
        print('Creating job for', params)
        job = project.open_job(params).init()
        estimator = svm.SVC(**params)
        joblib.dump(estimator, job.fn('estimator.joblib'))
