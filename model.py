
import numpy as np
import gpflow as gpf
import tensorflow as tf
import matplotlib.pyplot as plt

class COVIDGPModel(object):
    
    def __init__(
        self, 
        name,
        likelihood=None,
        kernel=None,
        inducing_variable_func=None,
        variational_optimizer=None,
        model_variables_optimizer=None,
        n_iter=1000,
        n_inducing=15
    ):
        self.name = name
        self.likelihood = likelihood or gpf.likelihoods.Gaussian()
        self.kernel = kernel or gpf.kernels.Matern32()
        self.inducing_variable_func = inducing_variable_func or self._inducing_variable_func
        self.variational_optimizer = variational_optimizer or gpf.optimizers.NaturalGradient(gamma=1.0)
        self.model_variables_optimizer = model_variables_optimizer or tf.optimizers.Adam(0.01)
        self.n_iter = n_iter
        self.n_inducing = n_inducing
        
        self._model = None
        self._x_scaler = None
        self._y_scaler = None
        self._elbo = []
        
    def _inducing_variable_func(self, data):
        Z = data[
            np.random.randint(data.shape[0], size=self.n_inducing), 0
        ]

        if data.shape[1] <= 1:
            return Z.reshape((-1, 1))
        
        for col in range(1, data.shape[1]):
            Z = np.vstack([
                Z, data[
                    np.random.randint(data.shape[0], size=self.n_inducing), col
                ]
            ])
            
        return Z.T
           
    def _init_model(self, X):
        self._inducing_variable = self.inducing_variable_func(X)
        
        self._model = gpf.models.SVGP(
            likelihood=self.likelihood,
            kernel=self.kernel,
            inducing_variable=self._inducing_variable, 
            num_data=X.shape[0]
        )

        gpf.set_trainable(self._model.q_mu, False)
        gpf.set_trainable(self._model.q_sqrt, False)
        
        return self._model
        
    def _loss_function(self, X, y):
        model = self._model
        def _loss():
            return model.training_loss((X, y))
        return _loss
        
    def train(self, X, y):
        self._init_model(X)

        for _ in range(gpf.ci_utils.ci_niter(self.n_iter)):
            self.model_variables_optimizer.minimize(
                self._loss_function(X, y),
                self._model.trainable_variables
            )
            self.variational_optimizer.minimize(
                self._loss_function(X, y),
                [(self._model.q_mu, self._model.q_sqrt)]
            )
            self._elbo.append(self._model.elbo((X, y)))

    def predict(self, X):
        return self._model.predict_f(X)
    
    @property
    def score(self):
        return self._elbo[-1].numpy()
    
    def plot_elbo(self, ax=None):
        if not self._model:
            raise RuntimeError('The model must be trained first')
            
        if not ax:
            ax = plt
        ax.plot(self._elbo)
        
    def plot_prediction(self, t, X, y, t_test=None, y_test=None, num_samples=20, ax=None, test=False):
        if not ax:
            _fig, ax = plt.subplots(1, figsize=(15, 4))
        
        Ypred = self._model.predict_f_samples(X, full_cov=True, num_samples=num_samples)
        mean, var = self._model.predict_f(X)

        if not test:            
            z_init = list(self._inducing_variable[:, 0])
            z_init_points = [np.argmin(np.abs(X[:, 0]-k)) for i, k in enumerate(z_init)]
            Z_init_dates = t[z_init_points, 0]
            ax.plot(Z_init_dates, np.zeros_like(z_init_points), "k|", mew=4, label="Initial inducing locations")

            z_opt = list(self._model.inducing_variable.Z.numpy()[:, 0])
            z_opt_points = [np.argmin(np.abs(X[:, 0]-k)) for i, k in enumerate(z_opt)]
            Z_opt_dates = t[z_opt_points, 0]
            ax.plot(Z_opt_dates, np.zeros_like(z_opt_points), "k|", mew=4, c="orange", label="Inducing locations")
        
        ax.plot(t, np.squeeze(Ypred).T, "C1", alpha=0.2)
        ax.plot(t, mean, "-", c="C0")

        lo = (mean - 2 * tf.sqrt(var)).numpy()
        hi = (mean + 2 * tf.sqrt(var)).numpy()
        ax.fill_between(t.flatten(), lo.flatten(), hi.flatten(), alpha=0.3)
        ax.plot(t, y, "o", c="C2", alpha=0.7, label="train")
        if (t_test is not None) and (y_test is not None):
            ax.plot(t_test, y_test, "o", c="C3", alpha=0.7, label="test")
            ax.legend()
