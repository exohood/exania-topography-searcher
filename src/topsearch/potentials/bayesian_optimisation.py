""" Module that contains the different acquisition function classes for use
    in Bayesian optimisation. Both expected improvement and upper confidence
    bound are available """

import scipy.stats
import numpy as np
from nptyping import NDArray

from topsearch.potentials.gaussian_process import GaussianProcess
from .potential import Potential


class ExpectedImprovement(Potential):

    """
    Description
    -------------

    Evaluate the expected improvement function to determine the utility
    in picking a particular point for a next experiment in BayesOpt.
    The function is constructed from a given Gaussian process that provides.
    Defined assuming maximisation of a dataset

    Attributes
    -------------
    gaussian_process : object
        The gaussian process fit from which we build the acquisition function
    zeta : float
        Parameter in the acquisition functions that controls exploration vs
        exploitation
    """

    def __init__(self, gaussian_process: GaussianProcess, zeta: float) -> None:
        self.atomistic = False
        self.gaussian_process = gaussian_process
        self.zeta = zeta

    def function(self, position: NDArray) -> float:
        """ Return the expected improvement at position """
        current_max = np.max(self.gaussian_process.model_data.response)
        mean, std = self.gaussian_process.function_and_std(position)
        prefactor = mean - current_max - self.zeta
        return prefactor*scipy.stats.norm.cdf(prefactor/std) + \
            std*scipy.stats.norm.pdf(prefactor/std)


class UpperConfidenceBound(Potential):

    """
    Description
    -------------

    Evaluate the upper confidence bound, which gives the utility in picking
    a given point as the next experiment in Bayesian optimisation.
    The function is constructed from a given Gaussian process that provides
    both mean and variance. Defined assuming minimisation of a dataset

    Attributes
    -------------
    gaussian_process : object
        The gaussian process fit from which we build the acquisition function
    zeta : float
        Parameter in the acquisition functions that controls exploration vs
        exploitation
    """

    def __init__(self, gaussian_process: GaussianProcess, zeta: float) -> None:
        self.atomistic = False
        self.gaussian_process = gaussian_process
        self.zeta = zeta

    def function(self, position: NDArray) -> float:
        """ Return the value of the acquisition function """
        mean, std = self.gaussian_process.function_and_std(position)
        return float(mean - self.zeta*std)
