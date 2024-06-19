.. _jockeying-customers:

===================================
How to Simulate Jockeying Customers
===================================

Jockeying is when a customer :ref:`reneges<reneging-customers>` from one queue but then joins another. In Ciw this is implemented in the same way as reneging, with the destinations determined by the routing object.

Consider a two node network, the first node is an M/M/1, :math:`\lambda = 5` and :math:`\mu = 2`, queue where customers renege if they have spend more than 6 time units in the queue. Upon reneging they are sent to the second node. The second node has no arrivals, one server with exponential services :math:`\mu = 4`, and no reneging.

First we need to define a :ref:`Routing object<routing-objects>`. Here the usual routing is to leave the system, so we can begin by inheriting the :code:`ciw.routing.Leave` class. The difference will be to re-define the object's :code:`next_node_for_jockeying` method::

    >>> import ciw
    >>> class Jockey(ciw.routing.Leave):
    ...     def next_node_for_jockeying(self, ind):
    ...         """
    ...         Jockeys to Node 2
    ...         """
    ...         return self.simulation.nodes[2]

Once this is defined, we can create the network object and run the simulation::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(5),
    ...                            None],
    ...     service_distributions=[ciw.dists.Exponential(2),
    ...                            ciw.dists.Exponential(4)],
    ...     number_of_servers=[1, 1],
    ...     routing=ciw.routing.NetworkRouting(
    ...         routers=[Jockey(), ciw.routing.Leave()]
    ...     ),
    ...     reneging_time_distributions=[ciw.dists.Deterministic(6),
    ...                                  None],
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

