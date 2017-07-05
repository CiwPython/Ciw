.. _set-dists:

==========================================
How to Set Arrival & Service Distributions
==========================================

Ciw offeres a variety of inter-arrival and service time distributions.
A full list can be found :ref:`here <refs-dists>`.
They are defined when creating a Network with the :code:`'Arrival_distributions'` and :code:`'Service_distributions'` keywords.

+ :code:`'Arrival_distributions'`: This is the distribution that inter-arrival times are drawn from. That is the time between two consecutive arrivals. It is particular to specific nodes and customer classes.
+ :code:`'Service_distributions'`: This is the distribution that service times are drawn from. That is the amount of time a customer spends with a server (independent of how many servers there are). It is particular for to specific node and customer classes.

The following example, with two nodes and two customer classes, uses eight different arrival and service rate distributions::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     Arrival_distributions={'Class 0': [['Deterministic', 0.4],
    ...                                        ['Empirical', [0.1, 0.1, 0.1, 0.2]]],
    ...                            'Class 1': [['Deterministic', 0.2],
    ...                                        ['Custom', [0.2, 0.4], [0.5, 0.5]]]},
    ...     Service_distributions={'Class 0': [['Exponential', 6.0],
    ...                                        ['Lognormal', -1, 0.5]],
    ...                            'Class 1': [['Uniform', 0.1, 0.7],
    ...                                        ['Triangular', 0.2, 0.7, 0.3]]},
    ...     Transition_matrices={'Class 0': [[0.0, 0.0], [0.0, 0.0]],
    ...                          'Class 1': [[0.0, 0.0], [0.0, 0.0]]},
    ...     Number_of_servers=[1, 1]
    ... )

We'll run this (in :ref:`exact <exact-arithmetic>` mode) for 25 time units::

    >>> ciw.seed(10)
    >>> Q = ciw.Simulation(N, exact=10)
    >>> Q.simulate_until_max_time(50)
    >>> recs = Q.get_all_records()

The system uses the following eight distributions:

+ :code:`['Deterministic', 0.4]`:
   + Always sample 0.4.
+ :code:`['Deterministic', 0.2]`:
   + Always sample 0.2.
+ :code:`['Empirical', [0.1, 0.1, 0.1, 0.2]`:
   + Randomly sample from the numbers 0.1, 0.1, 0.1 and 0.2.
+ :code:`['Custom', [[0.5, 0.2], [0.5, 0.4]]]`:
   + Sample 0.2 half the time, and 0.4 half the time.
+ :code:`['Exponential', 6.0]`:
   + Sample from the `exponential <https://en.wikipedia.org/wiki/Exponential_distribution>`_ distribution with parameter :math:`\lambda = 6.0`. Expected mean of 0.1666...
+ :code:`['Uniform', 0.1, 0.7]`:
   + Sample any number between 0.1 and 0.7 with equal probablity. Expected mean of 0.4.
+ :code:`['Lognormal', -1, 0.5]`:
   + Sample from the `lognormal <https://en.wikipedia.org/wiki/Log-normal_distribution>`_ distribution with parameters :math:`\mu = -1` and :math:`\sigma = 0.5`. Expected mean of 0.4724...
+ :code:`['Triangular', 0.2, 0.7, 0.3]`:
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
    Decimal('0.1650563448')

    >>> sum(servicetimes_n2c0) / len(servicetimes_n2c0) # Expected 0.4724...
    Decimal('0.4228601677')

    >>> sum(servicetimes_n1c1) / len(servicetimes_n1c1) # Expected 0.4
    Decimal('0.4352210564')

    >>> sum(servicetimes_n2c1) / len(servicetimes_n2c1) # Expected 0.4
    Decimal('0.4100529676')

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