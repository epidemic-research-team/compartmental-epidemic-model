
import time
from collections import namedtuple
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

from model import COVIDGPModel


class _Timer(object):
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time


_Experiment_cls = namedtuple(
    'Experiment',
    [
        'model', 'likelihood', 'kernel', 'mle',
        'train_dates', 'test_dates', 'train_size', 
        'test_size', 'n_inducing_points', 'run_time',
        'var_within_sample', 'var_out_sample', 
        'within_sample', 'out_sample', 
        'week_1', 'week_2', 'week_3',
        'model_obj'
    ]
)


class Experiment(_Experiment_cls):
    
    _FRIENDLY_NAMES = {
        'model': 'Model', 
        'likelihood':'Likelihood',
        'kernel':'Kernel', 
        'mle':'ELBO', 
        'train_dates':'Training-set dates',
        'test_dates':'Test-set dates', 
        'n_inducing_points':'Number of inducing points',
        'time_run':'Model run time (s)', 
        'var_within_sample':'Train average variance',
        'var_out_sample':'Test average variance', 
        'within_sample':'Train average error',
        'out_sample':'Test average error', 
        'week_1':'1st week average error',
        'week_2':'2nd week average error', 
        'week_3':'3rd week average error'
    }
    
    def to_dict(self):
        d = self._asdict()
        d.pop('model_obj')
        return d
    
    def to_pandas(self):
        df = pd.DataFrame.from_dict(self.to_dict(), orient='index', columns=["Summary"])
        return df.rename(index=self._FRIENDLY_NAMES)
    
    def __key(self):
        return (self.model, self.likelihood, self.kernel)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Experiment):
            return self.__key() == other.__key()
        return False


class Report(pd.DataFrame):
    
    _metadata = ['results', 'name']
    
    def __init__(self, results, name=''):
        self.results = results
        self.name = name
        super().__init__([e.to_dict() for e in results])
        
        if self.name:
            self.style.set_caption(self.name)
    
    def _repr_html_(self, *args, **kwargs):
        if self.name:
            return self.style.set_caption(self.name)._repr_html_()
        return super()._repr_html_()


def _default_train_test_split_func(t, X, y):
    return train_test_split(t, X, y, test_size=0.2)

def run_experiment(name, t, X, y, model_params=None, train_test_split_func=None, plot=False):
    model_params = model_params or {}
    train_test_split_func = train_test_split_func or _default_train_test_split_func
    
    with _Timer() as timer:
        np.random.seed(123)

        t_train, t_test, X_train, X_test, y_train, y_test = train_test_split_func(t, X, y)

        y_scaler = preprocessing.StandardScaler().fit(y_train)
        y_train = y_scaler.transform(y_train)
        y_test = y_scaler.transform(y_test)
        y = y_scaler.transform(y)

        x_scaler = preprocessing.StandardScaler().fit(X_train)
        X_train = x_scaler.transform(X_train)
        X_test = x_scaler.transform(X_test)
        X = x_scaler.transform(X)

        model = COVIDGPModel(name, **model_params)
        model.train(X_train, y_train)

        mean_train, var_train = model.predict(X_train)
        y_train_pred = y_scaler.inverse_transform(mean_train.numpy())
        y_train_true = y_scaler.inverse_transform(y_train)

        mean_test, var_test = model.predict(X_test)
        y_test_pred = y_scaler.inverse_transform(mean_test.numpy())
        y_test_true = y_scaler.inverse_transform(y_test)

    train_date_start = np.datetime_as_string(min(t_train), unit='D')[0]
    train_date_end = np.datetime_as_string(max(t_train), unit='D')[0]
    test_date_start = np.datetime_as_string(min(t_test), unit='D')[0]
    test_date_end = np.datetime_as_string(max(t_test), unit='D')[0]

    results = Experiment(
        model = model.name,
        likelihood = model.likelihood.__class__.__name__,
        kernel = model.kernel.__class__.__name__,
        mle = round(model.score, 2),
        train_dates = f"{train_date_start} to {train_date_end}",
        test_dates = f"{test_date_start} to {test_date_end}",
        train_size = y_train.shape[0],
        test_size = y_test.shape[0],
        n_inducing_points = model._model.inducing_variable.Z.shape[0],
        run_time = timer.elapsed,
        within_sample = round(np.mean(y_train_true - y_train_pred), 0),
        var_within_sample = round(np.mean(var_train), 4),
        out_sample = round(np.mean(y_test_true - y_test_pred), 0),
        var_out_sample = round(np.mean(var_test), 4),
        week_1 = round(np.mean(y_test_true[:7] - y_test_pred[:7]), 0),
        week_2 = round(np.mean(y_test_true[7:14] - y_test_pred[7:14]), 0),
        week_3 = round(np.mean(y_test_true[14:] - y_test_pred[14:]), 0),
        model_obj = model
    )

    if plot:
        f = plt.figure(figsize=(30,4))
        ax = f.add_subplot(1, 4, (1, 2))
        model.plot_prediction(t, X, y, t_test, y_test, ax=ax)
        ax = f.add_subplot(1, 4, 3)
        model.plot_prediction(t_test, X_test, y_test, t_test, y_test, ax=ax, test=True)
        ax = f.add_subplot(1, 4, 4)
        model.plot_elbo(ax=ax)
        
    return results, model
