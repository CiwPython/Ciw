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


Reneging Locations
------------------

After a customer reneges, by default they are sent to the exit node. However, it is also possible to send customers to any other node in the network, using the :code:`reneging_destinations` keyword argument.

Consider a two node network, the first node is an M/M/1, :math:`\lambda = 5` and :math:`\mu = 2`, queue where customers renege if they have spend more than 6 time units in the queue. Upon reneging they are sent to the second node. The second node has no arrivals, one server with exponential services :math:`\mu = 4`, and no reneging::


    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(5), ciw.dists.NoArrivals()],
    ...     service_distributions=[ciw.dists.Exponential(2), ciw.dists.Exponential(4)],
    ...     number_of_servers=[1, 1],
    ...     routing=[[0, 0], [0, 0]],
    ...     reneging_time_distributions=[ciw.dists.Deterministic(6), None],
    ...     reneging_destinations=[2, -1]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N, exact=5)
    >>> Q.simulate_until_max_time(11)

Now we will see that the id number and arrival dates of the customers served at Node 2 are identical to the reneging times of the reneging customers, as the only way to get a service at Node 2 is to renege there::

    >>> recs = Q.get_all_records()
    >>> [(r.id_number, r.exit_date) for r in recs if r.record_type == 'renege']
    [(12, Decimal('8.0805')), (13, Decimal('8.1382')), (20, Decimal('10.441')), (21, Decimal('10.569')), (22, Decimal('10.758'))]
    >>> [(r.id_number, r.arrival_date) for r in recs if r.node == 2]
    [(12, Decimal('8.0805')), (13, Decimal('8.1382')), (20, Decimal('10.441')), (21, Decimal('10.569')), (22, Decimal('10.758'))]


**Note**: Similarly :code:`reneging_destinations` can take either a list of destination indicating which node to send reneging customer from node in the network; or dictionary mapping customer classes to these lists, allowing different reneging destinations for each customer class.
