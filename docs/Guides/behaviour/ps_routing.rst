.. _ps-routing:

===========================================
Load Balancing in Processor Sharing Systems
============================================

In this example we will consider multiple parallel processor sharing queues, where customers are routed to the least busy node. This is calles a Load Balancing, a type of Join Shortest Queue, or JSQ system.

Consider three independent parallel processor sharing nodes. Customers arrive and are sent to the least busy node.
This can be modelled as a 4 node system: the first node is a dummy node where customers arrive, and routes the customer to one of the thee remaining processor sharing nodes.
If the arrival distribution is Poisson with rate 8, and required service times are exponentially distributed with parameter 10, then our network is::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=8),
    ...                            None,
    ...                            None,
    ...                            None],
    ...     service_distributions=[ciw.dists.Deterministic(value=0),
    ...                            ciw.dists.Exponential(rate=10),
    ...                            ciw.dists.Exponential(rate=10),
    ...                            ciw.dists.Exponential(rate=10)],
    ...     number_of_servers=[float('inf'),
    ...                        float('inf'),
    ...                        float('inf'),
    ...                        float('inf')],
    ...     routing=ciw.routing.NetworkRouting(routers=[
    ...         ciw.routing.LoadBalancing(destinations=[2, 3, 4]),
    ...         ciw.routing.Leave(),
    ...         ciw.routing.Leave(),
    ...         ciw.routing.Leave()
    ...     ])
    ... )

For each of the three parallel processor sharing nodes, we can use the :code:`ciw.PSNode` class. The routing decisions are derived from the routing objects, where the first node is given the :code:`LoadBalancing` object, that balances the load in nodes 2, 3 and 4; that is, it sends the individual one of these nodes, whichever currently has the least individuals.

Now let's build a simulation object, where the first node uses the usual :code:`ciw.Node` class, and the others use the built-in :code:`ciw.PSNode` class. We'll also add a state tracker for analysis::

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(
    ...     N, tracker=ciw.trackers.SystemPopulation(),
    ...     node_class=[ciw.Node, ciw.PSNode, ciw.PSNode, ciw.PSNode])

We'll run this for 100 time units::

    >>> Q.simulate_until_max_time(100)

We can look at the state probabilities, that is, the proportion of time the system spent in each state, where a state represents the number of customers present in the system::

    >>> state_probs = Q.statetracker.state_probabilities(observation_period=(10, 90))
    >>> for n in range(8):
    ...     print(n, round(state_probs[n], 5))
    0 0.436
    1 0.37895
    2 0.13629
    3 0.03238
    4 0.01255
    5 0.00224
    6 0.00109
    7 0.00051
