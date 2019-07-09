from ciw.auxiliary import *
from itertools import cycle
import copy
from operator import add, mul, sub, truediv
from random import (expovariate, uniform, triangular, gammavariate,
                    lognormvariate, weibullvariate)

class Distribution(object):
    """
    A general distribution from which all other distirbutions will inherit.
    """
    def __repr__(self):
        return 'Distribution'

    def sample(self, t=None, ind=None):
        pass

    def _sample(self, t=None, ind=None):
        """
        Performs vaildity checks before sampling.
        """
        s = self.sample(t=t, ind=ind)
        if (isinstance(s, float) or isinstance(s, int)) and s >= 0:
            return s
        else:
            raise ValueError('Invalid time sampled.')

    def __add__(self, dist):
        """
        Add two distributions such that sampling is the sum of the samples.
        """
        return CombinedDistribution(self, dist, add)

    def __sub__(self, dist):
        """
        Subtract two distributions such that sampling is the difference of the samples.
        """
        return CombinedDistribution(self, dist, sub)

    def __mul__(self, dist):
        """
        Multiply two distributions such that sampling is the product of the samples.
        """
        return CombinedDistribution(self, dist, mul)

    def __truediv__(self, dist):
        """
        Divide two distributions such that sampling is the ratio of the samples.
        """
        return CombinedDistribution(self, dist, truediv)


class CombinedDistribution(Distribution):
    """
    A distribution that combines the samples of two other distributions, `dist1`
    and `dist2`, using `operator`.
    """

    def __init__(self, dist1, dist2, operator):
        self.d1 = copy.deepcopy(dist1)
        self.d2 = copy.deepcopy(dist2)
        self.operator = operator

    def __repr__(self):
        return 'CombinedDistribution'

    def sample(self, t=None, ind=None):
        s1 = self.d1.sample()
        s2 = self.d2.sample()
        return self.operator(s1, s2)


class Uniform(Distribution):
    """
    The Uniform distribution.

    Takes:
      - `lower` the lower bound
      - `upper` the upper bound
    """
    def __init__(self, lower, upper):
        if lower < 0.0 or upper < 0.0:
            raise ValueError('Uniform distribution must sample positive numbers only.')
        if upper < lower:
            raise ValueError('Uniform distirbution upper bound should be >= lower bound.')
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return 'Uniform: {0}, {1}'.format(self.lower, self.upper)

    def sample(self, t=None, ind=None):
        return uniform(self.lower, self.upper)


class Deterministic(Distribution):
    """
    The Deterministic distribution.

    Takes:
      - `value` the value to return
    """
    def __init__(self, value):
        if value < 0.0:
            raise ValueError('Deterministic distribution must sample positive numbers only.')
        self.value = value

    def __repr__(self):
        return 'Deterministic: {0}'.format(self.value)

    def sample(self, t=None, ind=None):
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
        if lower < 0.0 or upper < 0.0 or mode < 0.0:
            raise ValueError('Triangular distribution must sample positive numbers only.')
        if not lower <= mode <= upper:
            raise ValueError('Triangular distribution lower bound must be <= mode must be <= upper bound.')
        self.lower = lower
        self.mode = mode
        self.upper = upper

    def __repr__(self):
        return 'Triangular: {0}, {1}, {2}'.format(self.lower, self.mode, self.upper)

    def sample(self, t=None, ind=None):
        return triangular(self.lower, self.upper, self.mode)


class Exponential(Distribution):
    """
    The Exponential distribution.

    Takes:
      - `rate` the rate parameter, lambda
    """
    def __init__(self, rate):
        if rate <= 0.0:
            raise ValueError('Exponential distribution must sample positive numbers only.')
        self.rate = rate

    def __repr__(self):
        return 'Exponential: {0}'.format(self.rate)

    def sample(self, t=None, ind=None):
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

    def __repr__(self):
        return 'Gamma: {0}, {1}'.format(self.shape, self.scale)

    def sample(self, t=None, ind=None):
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

    def __repr__(self):
        return 'Normal: {0}, {1}'.format(self.mean, self.sd)

    def sample(self, t=None, ind=None):
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

    def __repr__(self):
        return 'Lognormal: {0}, {1}'.format(self.mean, self.sd)

    def sample(self, t=None, ind=None):
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

    def __repr__(self):
        return 'Weibull: {0}, {1}'.format(self.scale, self.shape)

    def sample(self, t=None, ind=None):
        return weibullvariate(self.scale, self.shape)


class Empirical(Distribution):
    """
    The Empirical distribution.

    Takes:
      - `observations` the observations from which to sample
    """
    def __init__(self, observations):
        if any(o < 0 for o in observations):
            raise ValueError('Empirical distribution must sample positive numbers only.')
        self.observations = observations

    def __repr__(self):
        return 'Empirical'

    def sample(self, t=None, ind=None):
        return random_choice(self.observations)


class Sequential(Distribution):
    """
    The Sequential distribution.

    Takes:
      - `sequence` the sequence to cycle through
    """
    def __init__(self, sequence):
        if any(o < 0 for o in sequence):
            raise ValueError('Sequential distribution must sample positive numbers only.')
        self.sequence = sequence
        self.generator = cycle(self.sequence)

    def __repr__(self):
        return 'Sequential'

    def sample(self, t=None, ind=None):
        return next(self.generator)


class Pmf(Distribution):
    """
    A distribution defined by a probability mass function (pmf).

    Takes:
      - `values` the values to sample
      - `probs` the associated probabilities
    """
    def __init__(self, values, probs):
        if any(o < 0 for o in values):
            raise ValueError('Pmf must sample positive numbers only.')
        if any(p < 0 or p > 1.0 for p in probs):
            raise ValueError('Pmf must have valid probabilities.')
        if sum(probs) != 1.0:
            raise ValueError('Pmf probabilities must sum to 1.0.')
        self.values = values
        self.probs = probs

    def __repr__(self):
        return 'Pmf'

    def sample(self, t=None, ind=None):
        return random_choice(self.values, self.probs)


class NoArrivals(Distribution):
    """
    A placeholder distribution if there are no arrivals.
    """
    def __repr__(self):
        return 'NoArrivals'

    def sample(self, t=None, ind=None):
        return float('Inf')
