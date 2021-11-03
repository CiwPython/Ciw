.. _set-dists:

==========================================
How to Set Arrival & Service Distributions
==========================================

Ciw offeres a variety of inter-arrival and service time distributions.
A full list can be found :ref:`here <refs-dists>`.
They are objects, that are defined in the :code:`Network` with the :code:`'arrival_distributions'` and :code:`'service_distributions'` keywords.

+ :code:`'Aarival_distributions'`: This is the distribution that inter-arrival times are drawn from. That is the time between two consecutive arrivals. It is particular to specific nodes and customer classes.
+ :code:`'service_distributions'`: This is the distribution that service times are drawn from. That is the amount of time a customer spends with a server (independent of how many servers there are). It is particular for to specific node and customer classes.

The following example, with two nodes and two customer classes, uses eight different arrival and service rate distributions::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions={'Class 0': [ciw.dists.Deterministic(value=0.4),
    ...                                        ciw.dists.Empirical(observations=[0.1, 0.1, 0.1, 0.2])],
    ...                            'Class 1': [ciw.dists.Deterministic(value=0.2),
    ...                                        ciw.dists.Pmf(values=[0.2, 0.4], probs=[0.5, 0.5])]},
    ...     service_distributions={'Class 0': [ciw.dists.Exponential(rate=6.0),
    ...                                        ciw.dists.Lognormal(mean=-1, sd=0.5)],
    ...                            'Class 1': [ciw.dists.Uniform(lower=0.1, upper=0.7),
    ...                                        ciw.dists.Triangular(lower=0.2, mode=0.3, upper=0.7)]},
    ...     routing={'Class 0': [[0.0, 0.0], [0.0, 0.0]],
    ...              'Class 1': [[0.0, 0.0], [0.0, 0.0]]},
    ...     number_of_servers=[1, 1]
    ... )

We'll run this (in :ref:`exact <exact-arithmetic>` mode) for 25 time units::

    >>> ciw.seed(10)
    >>> Q = ciw.Simulation(N, exact=10)
    >>> Q.simulate_until_max_time(50)
    >>> recs = Q.get_all_records()

The system uses the following eight distribution objects:

+ :code:`ciw.dists.Deterministic(value=0.4)`:
   + Always sample 0.4.
+ :code:`ciw.dists.Deterministic(value=0.2)`:
   + Always sample 0.2.
+ :code:`ciw.dists.Empirical(observations=[0.1, 0.1, 0.1, 0.2])`:
   + Randomly sample from the numbers 0.1, 0.1, 0.1 and 0.2.
+ :code:`ciw.dists.Pmf(values=[0.2, 0.4], probs=[0.5, 0.5])`:
   + Sample 0.2 half the time, and 0.4 half the time.
+ :code:`ciw.dists.Exponential(rate=6.0)`:
   + Sample from the `exponential <https://en.wikipedia.org/wiki/Exponential_distribution>`_ distribution with parameter :math:`\lambda = 6.0`. Expected mean of 0.1666...
+ :code:`ciw.dists.Uniform(lower=0.1, upper=0.7)`:
   + Sample any number between 0.1 and 0.7 with equal probablity. Expected mean of 0.4.
+ :code:`ciw.dists.Lognormal(mean=-1, sd=0.5)`:
   + Sample from the `lognormal <https://en.wikipedia.org/wiki/Log-normal_distribution>`_ distribution with parameters :math:`\mu = -1` and :math:`\sigma = 0.5`. Expected mean of 0.4724...
+ :code:`ciw.dists.Triangular(lower=0.2, mode=0.3, upper=0.7)`:
   + Sample from the `triangular <https://en.wikipedia.org/wiki/Triangular_distribution>`_ distribution, with mode 0.3, lower limit 0.2 and upper limit 0.7. Expected mean of 0.4.

From the records, collect the service times and arrival dates for each node and each customer class::

    >>> servicetimes_n1c0 = [r.service_time for r in recs if r.node==1 and r.customer_class==0]
    >>> servicetimes_n2c0 = [r.service_time for r in recs if r.node==2 and r.customer_class==0]
    >>> servicetimes_n1c1 = [r.service_time for r in recs if r.node==1 and r.customer_class==1]
    >>> servicetimes_n2c1 = [r.service_time for r in recs if r.node==2 and r.customer_class==1]
    >>> arrivals_n1c0 = sorted([r.arrival_date for r in recs if r.node==1 and r.customer_class==0])
    >>> arrivals_n2c0 = sorted([r.arrival_date for r in recs if r.node==2 and r.customer_class==0])
    >>> arrivals_n1c1 = sorted([r.arrival_date for r in recs if r.node==1 and r.customer_class==1])
    >>> arrivals_n2c1 = sorted([r.arrival_date for r in recs if r.node==2 and r.customer_class==1])

Now let's see if the mean service time and inter-arrival times of the simulation matches the distributions::

    >>> from decimal import Decimal

    >>> sum(servicetimes_n1c0) / len(servicetimes_n1c0) # Expected 0.1666...
    Decimal('0.1600313200')

    >>> sum(servicetimes_n2c0) / len(servicetimes_n2c0) # Expected 0.4724...
    Decimal('0.4250531396')

    >>> sum(servicetimes_n1c1) / len(servicetimes_n1c1) # Expected 0.4
    Decimal('0.4108660556')

    >>> sum(servicetimes_n2c1) / len(servicetimes_n2c1) # Expected 0.4
    Decimal('0.3942034906')

    >>> set([r2-r1 for r1, r2 in zip(arrivals_n1c0, arrivals_n1c0[1:])]) # Should only sample 0.4
    {Decimal('0.4')}

    >>> set([r2-r1 for r1, r2 in zip(arrivals_n1c1, arrivals_n1c1[1:])]) # Should only sample 0.2
    {Decimal('0.2')}

    >>> expected_samples = {Decimal('0.2'), Decimal('0.1')} # Should only sample 0.1 and 0.2
    >>> set([r2-r1 for r1, r2 in zip(arrivals_n2c0, arrivals_n2c0[1:])]) == expected_samples
    True

    >>> expected_samples = {Decimal('0.2'), Decimal('0.4')}#  Should only sample 0.2 and 0.4
    >>> set([r2-r1 for r1, r2 in zip(arrivals_n2c1, arrivals_n2c1[1:])]) == expected_samples
    True

​ 

Custom Distributions
--------------------

A distribution is defined by inheriting from the generic `ciw.dists.Distribution` class.
This allows users to define their own distributions.

Consider a distribution that samples the value `3.0` 50% of the time, and samples a uniform random number between 0 and 1 otherwise. That is written by inheriting from the generic class, and defining a new :code:`sample` method::

    >>> import random
    >>> class CustomDistribution(ciw.dists.Distribution):
    ...     def sample(self, t=None, ind=None):
    ...         if random.random() < 0.5:
    ...             return 3.0
    ...         return random.random()

This can then be implemented into a :code:`Network` object in the usual way.


Combined Distributions
----------------------

As distribution objects inherit from the generic distirbution function, they can be *combined* using the operations :code:`+`, :code:`-`, :code:`*`, and :code:`/`.

For example, let's combine an Exponential distribution with a Deterministic distribution in all four ways::

    >>> Exp_add_Det = ciw.dists.Exponential(rate=0.05) + ciw.dists.Deterministic(value=3.0)
    >>> Exp_sub_Det = ciw.dists.Exponential(rate=0.05) - ciw.dists.Deterministic(value=3.0)
    >>> Exp_mul_Det = ciw.dists.Exponential(rate=0.05) * ciw.dists.Deterministic(value=3.0)
    >>> Exp_div_Det = ciw.dists.Exponential(rate=0.05) / ciw.dists.Deterministic(value=3.0)

These combined distributions return the combined sampled values:

    >>> ciw.seed(10)
    >>> Ex = ciw.dists.Exponential(rate=0.05)
    >>> Dt = ciw.dists.Deterministic(value=3.0)
    >>> [round(Ex.sample(), 2) for _ in range(5)]
    [16.94, 11.2, 17.26, 4.62, 33.57]
    >>> [round(Dt.sample(), 2) for _ in range(5)]
    [3.0, 3.0, 3.0, 3.0, 3.0]

    >>> # Addition
    >>> ciw.seed(10)
    >>> [round(Exp_add_Det.sample(), 2) for _ in range(5)]
    [19.94, 14.2, 20.26, 7.62, 36.57]

    >>> # Subtraction
    >>> ciw.seed(10)
    >>> [round(Exp_sub_Det.sample(), 2) for _ in range(5)]
    [13.94, 8.2, 14.26, 1.62, 30.57]

    >>> # Multiplication
    >>> ciw.seed(10)
    >>> [round(Exp_mul_Det.sample(), 2) for _ in range(5)]
    [50.83, 33.61, 51.78, 13.85, 100.7]

    >>> # Division
    >>> ciw.seed(10)
    >>> [round(Exp_div_Det.sample(), 2) for _ in range(5)]
    [5.65, 3.73, 5.75, 1.54, 11.19]
