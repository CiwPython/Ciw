'''Distributions available in Ciw.''' 

import copy
import math
import random
from math import sqrt, exp, pi, erf
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
import statistics as st

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
    
    @property
    def mean(self):
        """default mean of a distribution"""
        return float('nan')

    @property
    def variance(self):
        """default variance of a distribution"""
        return float('nan')

    @property
    def sd(self):
        """default standard deviation of a distribution"""
        return math.sqrt(self.variance)

    @property
    def median(self):
        """default median of a distribution""" 
        return float('nan')

    @property
    def upper_limit(self):
         """default upper range of a distribution""" 
         return float('nan')

    @property
    def lower_limit(self):
        """default lower range of a distribution""" 
        return float('nan')


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

    @property
    def mean(self):
        m1 = self.d1.mean
        m2 = self.d2.mean
        if self.operator == add:
            return m1 + m2
        elif self.operator == sub:
            return m1 - m2
        elif self.operator == mul:
            return m1 * m2
        elif self.operator == truediv:
            if m2 == 0:
                return float('nan')
            return m1 / m2  # delta-method mean

    @property
    def variance(self):
        m1 = self.d1.mean
        m2 = self.d2.mean
        v1 = self.d1.variance
        v2 = self.d2.variance

        if self.operator in (add, sub):
            # Var(A + B) = Var(A) + Var(B), assuming independence
            # Var(A - B) = Var(A) + Var(B), assuming independence
            return v1 + v2
        elif self.operator == mul:
            # Var(A * B) = v1*v2 + m2^2*v1 + m1^2*v2, assuming independence
            return v1 * v2 + (m2 ** 2) * v1 + (m1 ** 2) * v2
        elif self.operator == truediv:
            # delta-method approximation for Var(A/B)
            if m2 == 0:
                return float('nan')
            return (v1 / (m2 ** 2)) + ((m1 ** 2) * v2) / (m2 ** 4)

    @property
    def upper_limit(self):
        if self.operator == add:
            return self.d1.upper_limit + self.d2.upper_limit
        return float('nan')

    @property
    def lower_limit(self):
        if self.operator == add:
            return self.d1.lower_limit + self.d2.lower_limit
        return float('nan')


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

    @property
    def mean(self):
        """Returns the mean of the Uniform distribution."""
        return (self.lower + self.upper) / 2

    @property
    def variance(self):
        """Returns the variance of the Uniform distribution."""
        return ((self.upper - self.lower) ** 2) / 12
 
    @property
    def median(self):
        return (self.lower + self.upper) / 2

    @property
    def upper_limit(self):
        return self.upper
    
    @property
    def lower_limit(self):
        return self.lower


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

    @property
    def mean(self):
        """Returns the mean of the Deterministic distribution."""
        return self.value

    @property
    def variance(self):
        """Variance of a Deterministic distribution is always 0."""
        return 0.0

    @property
    def median(self):
        return self.value

    @property
    def upper_limit(self):
        return self.value
    
    @property
    def lower_limit(self):
        return self.value


class Triangular(Distribution):
    """
    The Triangular distribution.

    Takes:
      - `lower` the lower bound
      - `upper` the upper bound
      - `mode`  the modal value
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

    @property
    def mean(self):
        """Returns the mean of the Triangular distribution."""
        return (self.lower + self.mode + self.upper) / 3

    @property
    def variance(self):
        """Returns the variance of the Triangular distribution."""
        a, b, c = self.lower, self.upper, self.mode
        return (a**2 + b**2 + c**2 - a*b - a*c - b*c) / 18
 
    @property
    def median(self):
        # True median of a Triangular(a, c, b)
        a, c, b = self.lower, self.mode, self.upper
        mid = (a + b) / 2
        if c >= mid:
            return a + (((b - a) * (c - a) / 2) ** 0.5)
        return b - (((b - a) * (b - c) / 2) ** 0.5)

    @property
    def upper_limit(self):
        return self.upper
    
    @property
    def lower_limit(self):
        return self.lower


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

    @property
    def mean(self):
        """Returns the mean of the Exponential distribution."""
        return 1 / self.rate

    @property
    def variance(self):
        """Returns the variance of the Exponential distribution."""
        return 1 / (self.rate ** 2)


    @property
    def median(self):
        return math.log(2) / self.rate

    @property
    def upper_limit(self):
        return float('inf')
    
    @property
    def lower_limit(self):
        return 0 


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

    @property
    def mean(self):
        """Returns the mean of the Gamma distribution."""
        return self.shape * self.scale

    @property
    def variance(self):
        """Returns the variance of the Gamma distribution."""
        return self.shape * (self.scale ** 2)

    @property
    def upper_limit(self):
        return float('inf')
    
    @property
    def lower_limit(self):
        return 0


class Normal(Distribution):
    """
    Truncated Normal distribution (truncated below at 0).

    Parameters:
        mean (float): Mean of the original normal distribution.
        sd (float): Standard deviation of the original normal distribution.
    """
    def __init__(self, mean, sd):
        self._mean = mean
        self._sd = sd

    def __repr__(self):
        return f"Normal(mean={self._mean}, sd={self._sd})"

    def sample(self, t=None, ind=None):
        return truncated_normal(self._mean, self._sd)

    @property
    def mean(self):
        z = self._mean / self._sd
        phi = (1 / sqrt(2 * pi)) * exp(-0.5 * z ** 2)
        Phi = 0.5 * (1 + erf(z / sqrt(2)))
        return self._mean + self._sd * (phi / Phi)

    @property
    def variance(self):
        z = self._mean / self._sd
        phi = (1 / sqrt(2 * pi)) * exp(-0.5 * z ** 2)
        Phi = 0.5 * (1 + erf(z / sqrt(2)))
        term = phi / Phi
        return (self._sd ** 2) * (1 - z * term - (term ** 2))

    @property
    def median(self):
        # Truncated below at 0 
        z = self._mean / self._sd
        Norm = st.NormalDist(0, 1)
        target = 1.0 - 0.5 * Norm.cdf(z)
        return self._mean + self._sd * Norm.inv_cdf(target)

    @property
    def upper_limit(self):
        return float('inf')
    
    @property
    def lower_limit(self):
        return 0


class Lognormal(Distribution):
    """
    The Lognormal distribution.

    Takes:
      - `mean` the mean of the Normal, mu
      - `sd`   the standard deviation of the Normal, sigma
    """
    def __init__(self, mean, sd):
        self._mean = mean
        self._sd = sd

    def __repr__(self):
        return f"Lognormal(mean={self._mean}, sd={self._sd})"

    def sample(self, t=None, ind=None):
        return lognormvariate(self._mean, self._sd)

    @property
    def mean(self):
        return math.exp(self._mean + (self._sd ** 2) / 2)

    @property
    def variance(self):
        return (math.exp(self._sd ** 2) - 1) * math.exp(2 * self._mean + self._sd ** 2)

    @property
    def median(self):
        return math.exp(self._mean)

    @property
    def upper_limit(self):
        return float('inf')
    
    @property
    def lower_limit(self):
        return 0


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

    @property
    def mean(self):
        """Returns the mean of the Weibull distribution."""
        return self.scale * math.gamma(1 + 1 / self.shape)

    @property
    def variance(self):
        """Returns the variance of the Weibull distribution."""
        g1 = math.gamma(1 + 1 / self.shape)
        g2 = math.gamma(1 + 2 / self.shape)
        return (self.scale ** 2) * (g2 - (g1 ** 2))

    @property
    def median(self):
        return self.scale * (math.log(2) ** (1 / self.shape))

    @property
    def upper_limit(self):
        return float ('inf')
    
    @property
    def lower_limit(self):
        return 0


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

    @property
    def mean(self):
        """Returns the mean of the Empirical distribution."""
        return sum(self.observations) / len(self.observations)

    @property
    def variance(self):
        """Returns the variance of the Empirical distribution."""
        m = self.mean
        return sum((x - m) ** 2 for x in self.observations) / len(self.observations)
    
    @property
    def median(self):
        # standard sample-median:
        #  - odd n: middle element
        #  - even n: average of the two middle elements
        xs = sorted(self.observations)
        n = len(xs)
        mid = n // 2
        if n % 2 == 1:
            return xs[mid]
        else:
            return (xs[mid - 1] + xs[mid]) / 2

    @property
    def upper_limit(self):
        return max(self.observations)
    
    @property
    def lower_limit(self):
        return min(self.observations)


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

    @property
    def mean(self):
        """Returns the mean of the Sequential distribution."""
        return sum(self.sequence) / len(self.sequence)

    @property
    def variance(self):
        """Returns the variance of the Sequential distribution."""
        m = self.mean
        return sum((x - m) ** 2 for x in self.sequence) / len(self.sequence)

    @property
    def median(self):
        # sample median of the fixed sequence 
        #  - odd n: middle element
        #  - even n: average of the two middle elements
        xs = sorted(self.sequence)
        n = len(xs)
        mid = n // 2
        if n % 2 == 1:
            return xs[mid]
        else:
            return (xs[mid - 1] + xs[mid]) / 2

    @property
    def upper_limit(self):
        return max(self.sequence)
    
    @property
    def lower_limit(self):
        return min(self.sequence)


class Pmf(Distribution):
    """
    A distribution defined by a probability mass function (pmf).

    Takes:
      - `values` the values to sample
      - `probs`  the associated probabilities
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

    @property
    def mean(self):
        """Returns the mean of the PMF distribution."""
        return sum(v * p for v, p in zip(self.values, self.probs))

    @property
    def variance(self):
        """Returns the variance of the PMF distribution."""
        m = self.mean 
        return sum(p * (v - m) ** 2 for v, p in zip(self.values, self.probs))

    @property 
    def median(self): 
        pairs = sorted(zip(self.values, self.probs), key=lambda t: t[0]) 
        cum = 0.0 
        for v, p in pairs: 
            cum += p 
            if cum >= 0.5: 
                return v 
        return pairs[-1][0] 

    @property
    def upper_limit(self):
        return max(self.values)
    
    @property
    def lower_limit(self):
        return min(self.values) 


class PhaseType(Distribution): 
    """
    A distribution defined by an initial vector and an absorbing Markov chain

    Takes:
      - `initial_state`   the intial probabilities of being in each state
      - `absorbing_matrix` the martix representation of the absorbing Markov
        chain, with the final state the absorbing state
    """

    def __init__(self, initial_state, absorbing_matrix): 
        if any(p < 0 for p in initial_state): 
            raise ValueError("Initial state vector must have positive probabilities.") 
        if any(p > 1.0 for p in initial_state): 
            raise ValueError("Initial state vector probabilities must be no more than 1.0.") 
        if sum(initial_state) > 1.0 + 10 ** (-10) or sum(initial_state) < 1.0 - 10 ** (-10): 
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

    @property
    def mean(self):
        Q = np.array(self.absorbing_matrix)[:-1, :-1]
        alpha = np.array(self.initial_state[:-1])
        ones = np.ones(len(Q))
        return float(alpha @ np.linalg.inv(-Q) @ ones)

    @property
    def variance(self):
        Q = np.array(self.absorbing_matrix)[:-1, :-1]
        alpha = np.array(self.initial_state)[:-1]
        ones = np.ones(len(Q))
        invQ = np.linalg.inv(-Q)

        # E[T] and E[T^2]
        mean = float(alpha @ invQ @ ones)
        second_moment = float(2 * alpha @ invQ @ invQ @ ones)

        # Var(T) = E[T^2] - (E[T])^2  (with tinynegative clamp)
        v = second_moment - (mean ** 2)
        return v

    @property
    def upper_limit(self):
        return float('inf')
    
    @property
    def lower_limit(self):
        return 0


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

    @property
    def mean(self):
        return self.num_phases / self.rate

    @property
    def variance(self):
        return self.num_phases / (self.rate ** 2)


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
        self.rates = rates
        self.probs = probs
        initial_state = probs + [0]
        num_phases = len(probs)
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for phase in range(num_phases):
            absorbing_matrix[phase][phase] = -rates[phase]
            absorbing_matrix[phase][num_phases] = rates[phase]
        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        return "HyperExponential"

    @property
    def mean(self):
        return sum(p / r for p, r in zip(self.probs, self.rates))

    @property
    def variance(self):
        mean = self.mean
        return sum(2 * p / (r ** 2) for p, r in zip(self.probs, self.rates)) - (mean ** 2)


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
        self.rates = rates
        self.probs = probs
        self.phase_lengths = phase_lengths

        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        return "HyperErlang"

    @property
    def mean(self):
        return sum(
            p * k / r for p, r, k in zip(self.probs, self.rates, self.phase_lengths)
        )
   
    @property
    def variance(self):
        mean = self.mean  # âˆ‘ p * k / r
        #  second moment for Erlang(k, r) is k*(k+1)/r^2
        second_moment = sum(
            p * (k * (k + 1)) / (r ** 2)
            for p, r, k in zip(self.probs, self.rates, self.phase_lengths)
        )
        v = second_moment - (mean ** 2)
        return v


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
        self.inter_arrivals = [t - s for s, t in zip(self.dates, self.dates[1:])] + [float('inf')]
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
    
    @property
    def overall_rate(self):
        deltas = [self.endpoints[0]] + [
            self.endpoints[i] - self.endpoints[i - 1]
            for i in range(1, len(self.endpoints))
        ]
        P = self.endpoints[-1]
        LambdaP = sum(r * d for r, d in zip(self.rates, deltas))
        return LambdaP / P

    @property
    def mean(self):
        O_R = self.overall_rate
        return 1 / O_R if O_R > 0 else float('inf')

    @property
    def variance(self):
        return float('nan')

    @property
    def median(self):
        return float('nan')

    @property
    def upper_limit(self):
        return float('inf')
    
    @property
    def lower_limit(self):
        return 0

    
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

    @property
    def mean(self):
        return self.rate

    @property
    def variance(self):
        return self.rate

    @property
    def median(self):
        """this is a well known approximation of the median of a Poisson distribution"""
        return math.floor(self.rate + (1 / 3) - (0.02 / self.rate))

    @property
    def upper_limit(self):
        return float('inf')

    @property
    def lower_limit(self):
        return 0

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

    @property
    def mean(self):
        return 1 / self.prob

    @property
    def variance(self):
        return (1 - self.prob) / (self.prob ** 2)
    
    @property
    def median(self):
        return math.ceil(-1 / math.log(1 - self.prob, 2))

    @property
    def upper_limit(self):
        return float('inf')
    
    @property
    def lower_limit(self):
        return 0


class Binomial(Distribution):
    """
    The Binomial distribution.
    Note that this is a discrete integer distribution, for use with Batching.

    Takes:
      - `n`   the total number of experiments
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

    @property
    def mean(self):
        return self.n * self.prob

    @property
    def variance(self):
        return self.n * self.prob * (1 - self.prob)

    @property
    def median(self):
        return round(self.n * self.prob)

    @property
    def upper_limit(self):
        return float('inf')

    @property
    def lower_limit(self):
        return 0


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
        """
        chosen_dist = random.choices(
            population=self.dists,
            weights=self.probs,
            k=1
        )[0]

        return chosen_dist.sample(t, ind)

    def __repr__(self):
        return "MixtureDistribution"

    @property
    def mean(self):
        return sum(
            p * dist.mean for p, dist in zip(self.probs, self.dists)
        )

    @property
    def variance(self):
        mu = self.mean
        var = sum(
            p * (dist.variance + dist.mean ** 2) for p, dist in zip(self.probs, self.dists)
        ) - mu ** 2
        return max(var, 0)

    @property
    def upper_limit(self):
        if any(math.isnan(dist.upper_limit) for dist in self.dists):
            return float('nan')
        return max(dist.upper_limit for dist in self.dists)

    @property
    def lower_limit(self):
        if any(math.isnan(dist.lower_limit) for dist in self.dists):
            return float('nan')
        return min(dist.lower_limit for dist in self.dists)
