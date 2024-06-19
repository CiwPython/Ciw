.. _reneging-customers:

==================================
How to Simulate Reneging Customers
==================================

Ciw allows customers to renege, that is leave a queue after a certain amount of time waiting for service.
In Ciw, this works by sampling from a :code:`reneging_time_distribution`, giving the date that that customer will renege if their service has not started by that time.

For example, let's say we have an :ref:`M/M/1 <kendall-notation>`, :math:`\lambda = 5` and :math:`\mu = 2`, queue where customers renege if they have spend more than 6 time units in the queue::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(5)],
    ...     service_distributions=[ciw.dists.Exponential(2)],
    ...     number_of_servers=[1],
    ...     reneging_time_distributions=[ciw.dists.Deterministic(6)]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N, exact=5)
    >>> Q.simulate_until_max_time(10)

Reneging events are recorded as :code:`DataRecords` and so are collected along with service records with the :code:`get_all_records` method. They are distinguished by the :code:`record_type` field (services have :code:`service` record type, while reneging events have :code:`renege` record types).

For the above example, we see that no customer receiving service waited longer than 6 time units, as expected. We also see that all four reneging events happened after the customer waited 6 time units::

    >>> recs = Q.get_all_records()
    >>> max([r.waiting_time for r in recs if r.record_type == 'service'])
    Decimal('5.8880')

    >>> [r.waiting_time for r in recs if r.record_type == 'renege']
    [Decimal('6.0000'), Decimal('6.0000'), Decimal('6.0000'), Decimal('6.0000')]

By default, when a customer reneges, they leave the network, that is they are sent to the exit node.

**Note**: Similarly to all other customer-level keyword arguments, :code:`reneging_time_distributions` can take either a list of distributions indicating which reneging distribution to use at each node in the network; or dictionary mapping customer classes to these lists, allowing different reneging time distributions for each customer class.
