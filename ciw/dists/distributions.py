from ciw.auxiliary import *
from itertools import cycle
from random import (expovariate, uniform, triangular, gammavariate,
                    lognormvariate, weibullvariate)

class Distribution(object):
    """
    A general distribution from which all other distirbutions will inherit.
    """
    pass


class Uniform(Distribution):
    """
    The Uniform distribution.

    Takes:
      - `lower` the lower bound
      - `upper` the upper bound
    """
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper

    def sample(self, t=None):
        return uniform(self.lower, self.upper)


class Deterministic(Distribution):
    """
    The Deterministic distribution.

    Takes:
      - `value` the value to return
    """
    def __init__(self, value):
        self.value = value

    def sample(self, t=None):
        return self.value


class Triangular(Distribution):
    """
    The Triangular distribution.

    Takes:
      - `lower` the lower bound
      - `upper` the upper bound
      - `mode` the modal value
    """
    def __init__(self, lower, mode, upper):
        self.lower = lower
        self.mode = mode
        self.upper = upper

    def sample(self, t=None):
        return triangular(self.lower, self.upper, self.mode)


class Exponential(Distribution):
    """
    The Exponential distribution.

    Takes:
      - `rate` the rate parameter, lambda
    """
    def __init__(self, rate):
        self.rate = rate

    def sample(self, t=None):
        return expovariate(self.rate)

class Gamma(Distribution):
    """
    The Gamma distribution.

    Takes:
      - `shape` the shape parameter, alpha
      - `scale` the scale parameter, beta
    """
    def __init__(self, shape, scale):
        self.shape = shape
        self.scale = scale

    def sample(self, t=None):
        return gammavariate(self.shape, self.scale)


class Normal(Distribution):
    """
    The Truncated Normal distribution.

    Takes:
      - `mean` the mean of the Normal, mu
      - `sd` the standard deviation of the Normal, sigma
    """
    def __init__(self, mean, sd):
        self.mean = mean
        self.sd = sd

    def sample(self, t=None):
        return truncated_normal(self.mean, self.sd)


class Lognormal(Distribution):
    """
    The Lognormal distribution.

    Takes:
      - `mean` the mean of the Normal, mu
      - `sd` the standard deviation of the Normal, sigma
    """
    def __init__(self, mean, sd):
        self.mean = mean
        self.sd = sd

    def sample(self, t=None):
        return lognormvariate(self.mean, self.sd)


class Weibull(Distribution):
    """
    The Weibull distribution.

    Takes:
      - `scale` the scale parameter, alpha
      - `shape` the shape parameter, beta
    """
    def __init__(self, scale, shape):
        self.scale = scale
        self.shape = shape

    def sample(self, t=None):
        return weibullvariate(self.scale, self.shape)


class Empirical(Distribution):
    """
    The Empirical distribution.

    Takes:
      - `observations` the observations from which to sample
    """
    def __init__(self, observations):
        self.observations = observations

    def sample(self, t=None):
        return random_choice(self.observations)


class Sequential(Distribution):
    """
    The Sequential distribution.

    Takes:
      - `sequence` the sequence to cycle through
    """
    def __init__(self, sequence):
        self.sequence = sequence
        self.generator = cycle(self.sequence)

    def sample(self, t=None):
        return next(self.generator)


class Pmf(Distribution):
    """
    A distribution defined by a probability mass function (pmf).

    Takes:
      - `values` the values to sample
      - `probs` the associated probabilities
    """
    def __init__(self, values, probs):
        self.values = values
        self.probs = probs

    def sample(self, t=None):
        return random_choice(self.values, self.probs)


class NoArrivals(Distribution):
    """
    A placeholder distribution if there are no arrivals.
    """
    def sample(self, t=None):
        return float('Inf')
