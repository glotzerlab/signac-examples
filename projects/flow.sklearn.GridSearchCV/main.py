"""This example performs grid search, saving the results of each evaluated
parameter set into a signac data space.

Adapted from: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html
"""  # noqa: E501

import signac
from estimator import SignacMetaEstimator
from sklearn import datasets, svm
from sklearn.model_selection import GridSearchCV, train_test_split

# Load sample data
dataset = datasets.load_digits()
X = dataset.data
y = dataset.target
class_names = dataset.target_names.tolist()


# Split the data into a training set and a test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0)

# Initialize the signac project and save the training/testing data into the
# project's HDF5 data store
project = signac.init_project("gridsearch")
with project.data:
    project.data.X_train = X_train
    project.data.X_test = X_test
    project.data.y_train = y_train
    project.data.y_test = y_test

# Class names are non-numeric so they go into the project document.
project.doc.class_names = class_names

# These parameter names use scikit-learn's double underscore convention:
# https://scikit-learn.org/stable/glossary.html#term-double-underscore
parameters = {
    "estimator__kernel": ("linear", "rbf"),
    "estimator__C": (0.1, 1, 10, 100),
    "estimator__gamma": ("scale",),
}

# Create the estimators
svc = svm.SVC()
signac_estimator = SignacMetaEstimator(
    estimator=svc, project_dir=project.root_directory()
)

# Fit the GridSearchCV meta-estimator
with project.data:
    clf = GridSearchCV(signac_estimator, parameters, cv=5)
    clf.fit(project.data.X_train, project.data.y_train)

for k, v in clf.cv_results_.items():
    print(k, v)
