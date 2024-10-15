'''Distributions available in Ciw.'''

import copy
from itertools import cycle
from operator import add, mul, sub, truediv
from random import (
    expovariate,
    uniform,
    triangular,
    gammavariate,
    lognormvariate,
    weibullvariate,
)
from typing import List, NoReturn

import numpy as np

from ciw.auxiliary import *
from ciw.individual import Individual

class Distribution(object):
    """
    A general distribution from which all other distirbutions will inherit.
    """

    def __repr__(self):
        return "Distribution"

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
            raise ValueError("Invalid time sampled.")

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
        return "CombinedDistribution"

    def sample(self, t=None, ind=None):
        s1 = self.d1.sample(t, ind)
        s2 = self.d2.sample(t, ind)
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
            raise ValueError("Uniform distribution must sample positive numbers only.")
        if upper < lower:
            raise ValueError(
                "Uniform distirbution upper bound should be >= lower bound."
            )
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return f"Uniform(lower={self.lower}, upper={self.upper})"

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
            raise ValueError(
                "Deterministic distribution must sample positive numbers only."
            )
        self.value = value

    def __repr__(self):
        return f"Deterministic(value={self.value})"

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
            raise ValueError(
                "Triangular distribution must sample positive numbers only."
            )
        if not lower <= mode <= upper:
            raise ValueError(
                "Triangular distribution lower bound must be <= mode must be <= upper bound."
            )
        self.lower = lower
        self.mode = mode
        self.upper = upper

    def __repr__(self):
        return f"Triangular(lower={self.lower}, mode={self.mode}, upper={self.upper})"

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
            raise ValueError(
                "Exponential distribution must sample positive numbers only."
            )
        self.rate = rate

    def __repr__(self):
        return f"Exponential(rate={self.rate})"

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
        return f"Gamma(shape={self.shape}, scale={self.scale})"

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
        return f"Normal(mean={self.mean}, sd={self.sd})"

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
        return f"Lognormal(mean={self.mean}, sd={self.sd})"

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
        return f"Weibull(shape={self.shape}, scale={self.scale})"

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
            raise ValueError(
                "Empirical distribution must sample positive numbers only."
            )
        self.observations = observations

    def __repr__(self):
        return "Empirical"

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
            raise ValueError(
                "Sequential distribution must sample positive numbers only."
            )
        self.sequence = sequence
        self.generator = cycle(self.sequence)

    def __repr__(self):
        if len(self.sequence) <= 3:
            return f"Sequential({self.sequence})"
        else:
            return f"Sequential([{self.sequence[0]}, ..., {self.sequence[-1]}])"

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
            raise ValueError("Pmf must sample positive numbers only.")
        if any(p < 0 or p > 1.0 for p in probs):
            raise ValueError("Pmf must have valid probabilities.")
        if not np.isclose(sum(probs), 1.0):
            raise ValueError("Pmf probabilities must sum to 1.0.")
        self.values = values
        self.probs = probs

    def __repr__(self):
        return f"Pmf(values={self.values}, probs={self.probs})"

    def sample(self, t=None, ind=None):
        return random_choice(self.values, self.probs)


class PhaseType(Distribution):
    """
    A distribution defined by an initial vector and an absorbing Markov chain

    Takes:
      - `initial_state` the intial probabilities of being in each state
      - `absorbing_matrix` the martix representation of the absorbing Markov
        chain, with the final state the absorbing state
    """

    def __init__(self, initial_state, absorbing_matrix):
        if any(p < 0 or p > 1.0 for p in initial_state):
            raise ValueError("Initial state vector must have valid probabilities.")
        if sum(initial_state) > 1.0 + 10 ** (-10) or sum(initial_state) < 1.0 - 10 ** (
            -10
        ):
            raise ValueError("Initial state vector probabilities must sum to 1.0.")
        if any(len(absorbing_matrix) != len(row) for row in absorbing_matrix):
            raise ValueError("Matrix of the absorbing Markov chain must be square.")
        if len(initial_state) != len(absorbing_matrix):
            raise ValueError(
                "Initial state vector must have same number of states as absorbing Markov chain matrix."
            )
        if any(
            row[j] < 0
            for i, row in enumerate(absorbing_matrix)
            for j in range(len(absorbing_matrix))
            if i != j
        ):
            raise ValueError("Transition rates must be positive.")
        if not all(
            -(10 ** (-10)) < sum(row) < 10 ** (-10)
            for i, row in enumerate(absorbing_matrix)
        ):
            raise ValueError("Matrix rows must sum to 0.")
        if not all(r == 0 for r in absorbing_matrix[-1]):
            raise ValueError("Final state must be the absorbing state.")
        if not any(row[-1] > 0 for row in absorbing_matrix):
            raise ValueError("Must be possible to reach the absorbing state.")
        self.initial_state = initial_state
        self.states = tuple(range(len(initial_state)))
        self.absorbing_matrix = absorbing_matrix

    def __repr__(self):
        return "PhaseType"

    def sample_transition(self, rate):
        if rate <= 0.0:
            return float("Inf")
        return expovariate(rate)

    def sample(self, t=None, ind=None):
        cumulative_time = 0
        current_state = random_choice(self.states, probs=self.initial_state)
        while current_state != self.states[-1]:
            potential_transitions = [
                self.sample_transition(r) for r in self.absorbing_matrix[current_state]
            ]
            time, idx = min(
                (time, idx) for (idx, time) in enumerate(potential_transitions)
            )
            cumulative_time += time
            current_state = idx
        return cumulative_time


class Erlang(PhaseType):
    """
    An shortcut for the Erlang distribution, using the PhaseType distribution

    Takes:
      - `rate` the rate spent in each phase
      - `num_phases` the number of phases in series
    """

    def __init__(self, rate, num_phases):
        if rate <= 0.0:
            raise ValueError("Rate must be positive.")
        if num_phases < 1:
            raise ValueError("At least one phase is required.")
        self.rate = rate
        self.num_phases = num_phases
        initial_state = [1] + [0] * num_phases
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for phase in range(num_phases):
            absorbing_matrix[phase][phase] = -self.rate
            absorbing_matrix[phase][phase + 1] = self.rate
        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        return f"Erlang(rate={self.rate}, k={self.num_phases})"


class HyperExponential(PhaseType):
    """
    A shortcut for the HyperExponential distribution, using the PhaseType distribution

    Takes:
      - `rates` a vector of rates for each phase
      - `probs` a probability vector for starting in each phase
    """

    def __init__(self, rates, probs):
        if any(r <= 0.0 for r in rates):
            raise ValueError("Rates must be positive.")
        initial_state = probs + [0]
        num_phases = len(probs)
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for phase in range(num_phases):
            absorbing_matrix[phase][phase] = -rates[phase]
            absorbing_matrix[phase][num_phases] = rates[phase]
        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        return "HyperExponential"


class HyperErlang(PhaseType):
    """
    A shortcut for the HyperErlang distribution, using the PhaseType distribution

    Takes:
      - `rates` a vector of rates for each phase
      - `probs` a probability vector for starting in each phase
      - `phase_lengths` the number of sub-phases in each phase
    """

    def __init__(self, rates, probs, phase_lengths):
        if any(r <= 0.0 for r in rates):
            raise ValueError("Rates must be positive.")
        if any(n < 1 for n in phase_lengths):
            raise ValueError("At least one phase is required for each sub-phase.")
        initial_state = []
        for p, n in zip(probs, phase_lengths):
            initial_state += [p]
            initial_state += [0] * (n - 1)
        initial_state += [0]

        num_phases = sum(phase_lengths)
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for i, r in enumerate(rates):
            for subphase in range(phase_lengths[i]):
                offset = sum(phase_lengths[:i])
                absorbing_matrix[offset + subphase][offset + subphase] = -r
                if subphase < phase_lengths[i] - 1:
                    absorbing_matrix[offset + subphase][offset + subphase + 1] = r
                else:
                    absorbing_matrix[offset + subphase][-1] = r

        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        return "HyperErlang"


class Coxian(PhaseType):
    """
    A shortcut for the Coxian distribuion, using the PhaseType distribution

    Takes:
      - `rates` a vector of rates for each phase
      - `probs` a vector of the probability of absorption at each phase
    """

    def __init__(self, rates, probs):
        if any(r <= 0.0 for r in rates):
            raise ValueError("Rates must be positive.")
        if any(p < 0 or p > 1.0 for p in probs):
            raise ValueError("Probability vector must have valid probabilities.")
        if probs[-1] != 1.0:
            raise ValueError(
                "The probability of going to the absorbing state from the final phase must be 1.0."
            )
        num_phases = len(rates)
        initial_state = [1] + [0] * num_phases
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for i, (p, r) in enumerate(zip(probs, rates)):
            absorbing_matrix[i][i] = -r
            absorbing_matrix[i][i + 1] = (1 - p) * r
            absorbing_matrix[i][-1] = p * r
        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        return "Coxian"


class PoissonIntervals(Sequential):
    """
    A time-dependant Poission distribution for arrivals.

    Takes:
      - `rates` a list of Possion rates for each time interval
      - `endpoints` the endpoints of each time interval
      - `max_sample_date` the point where no more arrivals can occur

    The idea is to first sample the number of arrivals in each time
    interval from a Poisson distribution. Then to randomly distribute
    those arrival dates within the interval using a Uniform distribution.
    Then to take consecutive differences of these arrivals as the
    inter-arrival times, and use Ciw's Sequential distribution to output
    them.
    """

    def __init__(self, rates, endpoints, max_sample_date):
        if any(r < 0.0 for r in rates):
            raise ValueError("All rates must be positive.")
        if any(e <= 0.0 for e in endpoints):
            raise ValueError("All interval endpoints must be positive.")
        if max_sample_date <= 0.0:
            raise ValueError("Maximum sample date must be positive.")
        diffs = [s - t for s, t in zip(endpoints[1:], endpoints[:-1])]
        if any(d <= 0.0 for d in diffs):
            raise ValueError("Interval endpoints must be strictly increasing.")
        if len(rates) != len(endpoints):
            raise ValueError(
                "Consistent number of intervals (rates and endpoints) must be used."
            )

        self.rates = rates
        self.endpoints = endpoints
        self.max_sample_date = max_sample_date
        self.get_intervals()
        self.get_dates()
        self.inter_arrivals = [t - s for s, t in zip(self.dates, self.dates[1:])]
        if self.inter_arrivals == []:
            self.inter_arrivals = [float("inf")]
        super().__init__(self.inter_arrivals)

    def __repr__(self):
        return "PoissonIntervals"

    def get_intervals(self):
        self.num_intervals = len(self.endpoints)
        self.intervals = [(0, self.endpoints[0])]
        i, t1, t2 = 0, 0, 0
        while self.intervals[-1][-1] < self.max_sample_date:
            if i % self.num_intervals == self.num_intervals - 1:
                t2 = t1 + self.endpoints[-1]
            self.intervals.append(
                (
                    t1 + self.endpoints[i % self.num_intervals],
                    min(
                        t2 + self.endpoints[(i + 1) % self.num_intervals],
                        self.max_sample_date,
                    ),
                )
            )
            i += 1
            t1 = t2

    def get_dates(self):
        self.dates = [0.0]
        for i, interval in enumerate(self.intervals):
            n = ciw.rng.poisson(
                self.rates[i % self.num_intervals] * (interval[1] - interval[0])
            )
            interval_dates = [
                random.uniform(interval[0], interval[1]) for _ in range(n)
            ]
            interval_dates = sorted(interval_dates)
            self.dates += interval_dates


class Poisson(Distribution):
    """
    The Poisson distribution.
    Note that this is a discrete integer distribution, for use with Batching.

    Takes:
      - `rate` the rate parameter, lambda
    """

    def __init__(self, rate):
        if rate <= 0.0:
            raise ValueError("Poisson distribution must sample positive numbers only.")
        self.rate = rate

    def sample(self, t=None, ind=None):
        return ciw.rng.poisson(lam=self.rate)

    def __repr__(self):
        return f"Poisson(rate={self.rate})"


class Geometric(Distribution):
    """
    The Geometric distribution.
    Note that this is a discrete integer distribution, for use with Batching.

    Takes:
      - `prob` the probability parameter
    """

    def __init__(self, prob):
        if prob <= 0.0 or prob >= 1:
            raise ValueError(
                "Geometric distribution must have parameter between 0 and 1."
            )
        self.prob = prob

    def sample(self, t=None, ind=None):
        return ciw.rng.geometric(p=self.prob)

    def __repr__(self):
        return f"Geometric(prob={self.prob})"


class Binomial(Distribution):
    """
    The Binomial distribution.
    Note that this is a discrete integer distribution, for use with Batching.

    Takes:
      - `n` the parameter representing the total number of experiments
      - `prob` the probability parameter
    """

    def __init__(self, n, prob):
        if prob <= 0.0 or prob >= 1:
            raise ValueError(
                "Binomial distribution have probability parameter between 0 and 1."
            )
        if not isinstance(n, int) or n <= 0:
            raise ValueError(
                "The number of trials of the Binomial distirbution must be a positive integer."
            )
        self.n = n
        self.prob = prob

    def sample(self, t=None, ind=None):
        return ciw.rng.binomial(n=self.n, p=self.prob)

    def __repr__(self):
        return f"Binomial(n={self.n}, prob={self.prob})"


class MixtureDistribution(Distribution):
    """
    A mixture distribution combining multiple probability distributions.

    Parameters
    ----------
    dists : List[Distribution]
        A list of probability distributions to be combined in the mixture.
    probs : List[float]
        A list of weights corresponding to the importance of each distribution in the mixture.
        The weights must sum to 1.

    Attributes
    ----------
    probs : List[float]
        List of weights assigned to each distribution in the mixture.
    dists : List[Distribution]
        List of probability distributions in the mixture.

    Methods
    -------
    sample(t: float, ind: Individual = None) -> float:
        Generate a random sample from the mixture distribution.

    Notes
    -----
    The weights in `probs` should sum to 1, indicating the relative importance of each distribution
    in the mixture. The distributions in `dists` should be instances of `ciw.dists.Distribution`.
    """

    def __init__(self, dists: List[Distribution], probs: List[float]) -> NoReturn:
        """
        Initialize the MixtureDistribution.

        Parameters
        ----------
        dists : List[Distribution]
            A list of probability distributions to be combined in the mixture.
        probs : List[float]
            A list of weights corresponding to the importance of each distribution in the mixture.
            The weights must sum to 1.
        """
        self.probs = probs
        self.dists = dists

    def sample(self, t: float = None, ind: Individual = None) -> float:
        """
        Generate a random sample from the mixture distribution.

        Parameters
        ----------
        t : float
            The time parameter for the sample generation.
        inds : Individual, optional
           The individual to sample a time for, if applicable.

        Returns
        -------
        float
            A random sample from the mixture distribution.
        """
        chosen_dist = random.choices(
            population=self.dists,
            weights=self.probs,
            k=1)[0]

        return chosen_dist.sample(t, ind)
        
    def __repr__(self):
        return "MixtureDistribution"
