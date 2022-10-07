.. _refs-dists:

===============================
List of Supported Distributions
===============================

Ciw allows a number continuous service and inter-arrival time distributions, as well as empirical, user defined, time dependent, and custom discrete distributions.
Note that when choosing parameters for these distributions, ensure that no negative numbers may be sampled.
The following are currently supported:


- :ref:`uniform_dist`
- :ref:`deterministic_dist`
- :ref:`triangular_dist`
- :ref:`exponential_dist`
- :ref:`gamma_dist`
- :ref:`normal_dist`
- :ref:`lognormal_dist`
- :ref:`weibull_dist`
- :ref:`empirical_dist`
- :ref:`sequential_dist`
- :ref:`pmf_dist`
- :ref:`phasetype_dist`
- :ref:`erlang_dist`
- :ref:`hyperexponential_dist`
- :ref:`hypererlang_dist`
- :ref:`coxian_dist`
- :ref:`poissonintervals_dist`
- :ref:`no_arrivals`



.. _uniform_dist:

------------------------
The Uniform Distribution
------------------------

The uniform distribution samples a random number between two numbers `a` and `b`.
Write a uniform distribution between `4` and `9` as follows::

    ciw.dists.Uniform(lower=4.0, upper=9.0)





.. _deterministic_dist:

------------------------------
The Deterministic Distribution
------------------------------

The deterministic distribution is non-stochastic, and produces the same service time repeatedly.
Write a deterministic distribution that repeatedly gives a value of `18.2` as follows::

    ciw.dists.Deterministic(value=18.2)





.. _triangular_dist:

---------------------------
The Triangular Distribution
---------------------------

The triangular distribution samples a continuous pdf that rises linearly from its minimum value `low` to its mode value `mode`, and then decreases linearly to its highest attainable value `high`.
Write a triangular distribution between `2.1` and `7.6` with mode of `3.4` as follows::

    ciw.dists.Triangular(lower=2.1, mode=3.4, upper=7.6)





.. _exponential_dist:

----------------------------
The Exponential Distribution
----------------------------

The exponential distribution samples a random number from the negative exponential distribution with mean :math:`1 / \lambda`.
Write an exponential distribution with mean `0.2` as follows::

    ciw.dists.Exponential(rate=5)





.. _gamma_dist:

----------------------
The Gamma Distribution
----------------------

The gamma distribution samples a random number from the gamma distribution with shape parameter :math:`\alpha` and scale parameter :math:`\beta`.
Write a gamma distribution with parameters :math:`\alpha = 0.6` and :math:`\beta = 1.2` as follows::

    ciw.dists.Gamma(shape=0.6, scale=1.2)





.. _normal_dist:

---------------------------------
The Truncated Normal Distribution
---------------------------------

The truncated normal distribution samples a random number from the normal distribution with mean :math:`\mu` and standard deviation :math:`\sigma`.
The distribution is truncated at 0, thus if negative numbers are sampled then that observation is resampled until a positive value is sampled.
Write a normal distribution with parameters :math:`\mu = 0.7` and :math:`\sigma = 0.4` as follows::

    ciw.dists.Normal(mean=0.7, sd=0.4)





.. _lognormal_dist:

--------------------------
The Lognormal Distribution
--------------------------

The lognormal distribution samples a random number from the log of the normal distribution with mean :math:`\mu` and standard deviation :math:`\sigma`.
Write a lognomal distribution, that is a log of the normal distribution with :math:`\mu = 4.5` and :math:`\sigma = 2.0`, as follows::

    ciw.dists.Lognormal(mean=4.5, sd=2.0)





.. _weibull_dist:

------------------------
The Weibull Distribution
------------------------

The Weibull distribution samples a random number from the Weibull distribution with scale parameter :math:`\alpha` and shape parameter :math:`\beta`.
Write a Weibull distribution with :math:`\alpha = 0.9` and :math:`\beta = 0.8` as follows::

    ciw.dists.Weibull(scale=0.9, shape=0.8)





.. _empirical_dist:

-----------------------
Empirical Distributions
-----------------------

The empirical distribution randomly selects values from a list.
If values appear in the list more frequently, then they will be sampled more frequently.
Input list of observations::

    ciw.dists.Empirical(observations=[0.3, 0.3, 0.3, 0.4, 0.5, 0.6, 0.8, 0.9, 1.1, 1.1, 1.1, 1.1])





.. _sequential_dist:

------------------------
Sequential Distributions
------------------------

The sequential distribution takes a list, and iteratively returns the next observation in that list over time.
The distribution is cyclic, and so once all elements of the list have been sampled, the sequence of sampled values begins again from the beginning of the list::

    ciw.dists.Sequential(sequence=[0.1, 0.1, 0.2, 0.1, 0.3, 0.2])





.. _pmf_dist:

--------------------------
Probability Mass Functions
--------------------------

Ciw allows users to define their own custom PMFs to sample from.
This distribution samples from a set of values given a probability for each value, that is sampling the value :math:`x` with probability :math:`P(x)`.
For example, if :math:`P(1.4) = 0.2`, :math:`P(1.7) = 0.5`, and :math:`P(1.9) = 0.3`, this is defined in the following way::

    ciw.dists.Pmf(values=[1.4, 1.7, 1.9], probs=[0.2, 0.5, 0.3])


.. _phasetype_dist:

------------------------
Phase-Type Distributions
------------------------

Phase-Type distributions are defined by an initial state vector and transition matrix of its underlying Markov chain. More information is found :ref:`on the Guide to Phase-Type distributions <phase-type>`::

    initial_state = [0.7, 0.2, 0.1, 0.0]
    absorbing_matrix = [
        [-6, 2, 0, 4],
        [0, -3, 3, 0],
        [1, 0, -5, 4],
        [0, 0, 0, 0]
    ]
    ciw.dists.PhaseType(initial_state, absorbing_matrix)


.. _erlang_dist:

-----------------------
The Erlang Distribution
-----------------------

An Erlang distribution with parameters :math:`\lambda` and :math:`n` is the sum of :math:`n` Exponential distributions with parameter :math:`\lambda`.
Write an Erlang distribution with :math:`\lambda = 9` and :math:`n = 4` as follows::

    ciw.dists.Erlang(rate=9, num_phases=4)


.. _hyperexponential_dist:

---------------------------------
The HyperExponential Distribution
---------------------------------

An HyperExponential distribution is defined by a probability vector :math:`\mathbf{p}` and rate vector :math:`\mathbf{\lambda}`, and samples an Exponential distribution with parameter :math:`\lambda_i` with probability :math:`p_i`.
Write a HyperExponential distribution with :math:`\mathbf{\lambda} = \left(9, 5, 6, 1\right)` and :math:`\mathbf{p} = \left(0.2, 0.1, 0.6, 0.1\right)` as follows::

    ciw.dists.HyperExponential(rates=[9, 5, 6, 1], probs=[0.2, 0.1, 0.6, 0.1])


.. _hypererlang_dist:

----------------------------
The HyperErlang Distribution
----------------------------

A HyperErlang distribution is defined by parameters :math:`\mathbf{\lambda}`, :math:`\mathbf{p}`, and :math:`\mathbf{n}`, and samples an Erlang distribution of size :math:`n_i` with parameter :math:`\lambda_i` with probability :math:`p_i`.
Write a HyperErlang distribution with :math:`\mathbf{\lambda} = \left(5, 2, 3\right)`, :math:`\mathbf{p} = \left(0.5, 0.25, 0.25\right)`, and :math:`n = \left(2, 1, 2\right)` as follows::

    ciw.dists.HyperErlang(rates=[5, 2, 3], probs=[0.5, 0.25, 0.25], phase_lengths=[2, 1, 2])


.. _coxian_dist:

--------------------
Coxian Distributions
--------------------

A Coxian distribution is a specific type of Phase-Type distribution defined by parameters :math:`\mathbf{\lambda}`, the rates of each phase, and :math:`\mathbf{p}`, the probability of going to the absorbing state after each phase.
Write a Coxian distribution with :math:`\mathbf{\lambda} = \left(5, 2, 3, 7\right)` and :math:`\mathbf{p} = \left(0.5, 0.3, 0.65, 1\right)` as follows::

    ciw.dists.Coxian(rates=[5, 2, 3, 7], probs=[0.5, 0.3, 0.65, 1])


.. _poissonintervals_dist:

------------------------------
Poisson Intervals Distribution
------------------------------

The Poisson Intervals Distribution is a time-dependent distribution, where different time intervals sample arrivals from Poisson distributions, or inter-arrival times from Exponential distributions. It is used to overcome the problem of skipping arrivals accross interval thresholds.

For Exponential arrivals with rate 3 in the time interval (0, 4.8), rate 5.5 in the time interval (4.8, 9.3), and rate 0.1 in the time interval (9.3, 12), and repeating in the same manner thereafter until the time 100::

    ciw.dists.PoissonIntervals(rates=[3, 5.5, 0.1], endpoints=[4.8, 9.3, 12], max_sample_date=100)


.. _no_arrivals:

-----------
No Arrivals
-----------

If a node does not have any arrivals of a certain class, then the following may be input instead of a distribution::

    ciw.dists.NoArrivals()

Note that this is only valid for arrivals, and shouldn't be input into the :code:`Service_distributions` option.