"""Meta-estimator for using signac to track results from scikit-learn.

Adapted from dask-ml.wrappers.ParallelPostFit, https://ml.dask.org/meta-estimators.html
"""
import logging

import joblib
import numpy as np
import signac
import sklearn.base
import sklearn.metrics

logger = logging.getLogger(__name__)


def _copy_learned_attributes(from_estimator, to_estimator):
    attrs = {k: v for k, v in vars(from_estimator).items() if k.endswith("_")}

    for k, v in attrs.items():
        setattr(to_estimator, k, v)


class SignacMetaEstimator(sklearn.base.BaseEstimator, sklearn.base.MetaEstimatorMixin):
    """Meta-estimator for using signac to track results from scikit-learn estimators.

    Parameters
    ----------
    estimator : Estimator
        The underlying estimator that is fit.

    scoring : string or callable, optional
        A single string (see :ref:`scoring_parameter`) or a callable
        (see :ref:`scoring`) to evaluate the predictions on the test set.

        For evaluating multiple metrics, either give a list of (unique)
        strings or a dict with names as keys and callables as values.

        NOTE that when using custom scorers, each scorer should return a
        single value. Metric functions returning a list/array of values
        can be wrapped into multiple scorers that return one value each.

        See :ref:`multimetric_grid_search` for an example.

        .. warning::

           If None, the estimator's default scorer (if available) is used.
           Most scikit-learn estimators will convert large Dask arrays to
           a single NumPy array, which may exhaust the memory of your worker.
           You probably want to always specify `scoring`.
    """

    def __init__(self, estimator=None, scoring=None, project_dir=None):
        self.estimator = estimator
        self.scoring = scoring
        self.project_dir = project_dir
        self._project = None

    def fit(self, X, y=None, **kwargs):
        """Fit the underlying estimator.

        Parameters
        ----------
        X, y : array-like
        **kwargs
            Additional fit-kwargs for the underlying estimator.

        Returns
        -------
        self : object
        """
        logger.info("Starting fit.")
        estimator = sklearn.base.clone(self.estimator)
        self.estimator = estimator.fit(X, y, **kwargs)

        # Copy over learned attributes
        _copy_learned_attributes(self.estimator, self)

        # Save this estimator
        self._save_estimator()
        return self

    def transform(self, X):
        """Transform data.

        If the underlying estimator does not have a ``transform`` method, then
        an ``AttributeError`` is raised.

        Parameters
        ----------
        X : array-like

        Returns
        -------
        transformed : array-like
        """
        self._check_method("transform")
        return self.estimator.transform(X)

    def _save_estimator(self):
        """Saves a clone of the estimator to the signac job directory."""
        job = self.get_job().init()
        if not job.isfile("estimator.joblib"):
            estimator = sklearn.base.clone(self.estimator)
            joblib.dump(estimator, job.fn("estimator.joblib"))

    def score(self, X, y, compute=True):
        """Returns the score on the given data.

        Saves the estimator to ``estimator.joblib`` in the signac job directory.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Input data, where n_samples is the number of samples and
            n_features is the number of features.

        y : array-like, shape = [n_samples] or [n_samples, n_output], optional
            Target relative to X for classification or regression;
            None for unsupervised learning.

        Returns
        -------
        score : float
        """
        scoring = self.scoring

        if not scoring:
            if sklearn.base.is_regressor(self.estimator):
                scoring = "r2"
            elif sklearn.base.is_classifier(self.estimator):
                scoring = "accuracy"
        else:
            scoring = self.scoring

        if scoring:
            scorer = sklearn.metrics.get_scorer(scoring)
            score = scorer(self, X, y)
        else:
            score = self.estimator.score(X, y)
        return score

    def predict(self, X):
        """Predict for X.

        Parameters
        ----------
        X : array-like

        Returns
        -------
        y : array-like
        """
        self._check_method("predict")
        return self.estimator.predict(X)

    def predict_proba(self, X):
        """Probability estimates.

        If the underlying estimator does not have a ``predict_proba``
        method, then an ``AttributeError`` is raised.

        Parameters
        ----------
        X : array or dataframe

        Returns
        -------
        y : array-like
        """
        self._check_method("predict_proba")
        return self.estimator.predict_proba(X)

    def predict_log_proba(self, X):
        """Log of proability estimates.

        If the underlying estimator does not have a ``predict_proba``
        method, then an ``AttributeError`` is raised.

        Parameters
        ----------
        X : array or dataframe

        Returns
        -------
        y : array-like
        """
        self._check_method("predict_log_proba")
        return np.log(self.predict_proba(X))

    def _check_method(self, method):
        """Check if self.estimator has 'method'.

        Raises
        ------
        AttributeError
        """
        estimator = self.estimator
        if not hasattr(estimator, method):
            msg = "The wrapped estimator '{}' does not have a '{}' method.".format(
                estimator, method
            )
            raise AttributeError(msg)
        return getattr(estimator, method)

    def _check_project(self):
        """Check if project is set."""
        if self.project_dir is None:
            raise AttributeError(
                "The project_dir parameter must be set to a signac project directory."
            )

    def _get_project(self):
        """Caches a signac project object."""
        if self._project is None or self._project.root_directory() != self.project_dir:
            self._project = signac.get_project(self.project_dir)
        return self._project

    def get_job(self):
        """Returns a signac job for the current estimator and set of parameters."""
        self._check_project()
        params = {
            "estimator": type(self.estimator).__name__,
            "params": self.estimator.get_params(),
        }
        return self._get_project().open_job(params)
