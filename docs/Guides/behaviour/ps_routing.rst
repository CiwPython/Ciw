.. _ps-routing:

================================================
Join Shortest Queue in Processor Sharing Systems
================================================

In this example we will consider multiple parallel processor sharing queues, where customers are routed to the least busy node. This is calles a Join Shortest Queue, or JSQ system.

Consider three independent parallel processor sharing nodes. Customers arrive and are sent to the least busy node.
This can be modelled as a 4 node system: the first node is a dummy node where customers arrive, and routes the customer to one of the thee remaining processor sharing nodes.
If the arrival distribution is Poisson with rate 8, and required service times are exponentially distributed with parameter 10, then our network is::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=8),
    ...                            ciw.dists.NoArrivals(),
    ...                            ciw.dists.NoArrivals(),
    ...                            ciw.dists.NoArrivals()],
    ...     service_distributions=[ciw.dists.Deterministic(value=0),
    ...                            ciw.dists.Exponential(rate=10),
    ...                            ciw.dists.Exponential(rate=10),
    ...                            ciw.dists.Exponential(rate=10)],
    ...     number_of_servers=[float('inf'),
    ...                        float('inf'),
    ...                        float('inf'),
    ...                        float('inf')],
    ...     routing=[[0, 0, 0, 0],
    ...              [0, 0, 0, 0],
    ...              [0, 0, 0, 0],
    ...              [0, 0, 0, 0]]
    ... )

For each of the three parallel processor sharing nodes, we can use the :code:`ciw.PSNode` class.
However, we now need a custom node class for the initial dummy node, to take care of the routing decisions.
We'll call this class :code:`RoutingDecision`::

    >>> class RoutingDecision(ciw.Node):
    ...     def next_node(self, ind):
    ...         """
    ...         Finds the next node by looking at nodes 2, 3, and 4,
    ...         seeing how busy they are, and routing to the least busy.
    ...         """
    ...         busyness = {n: self.simulation.nodes[n].number_of_individuals for n in [2, 3, 4]}
    ...         chosen_n = sorted(busyness.keys(), key=lambda x: busyness[x])[0]
    ...         return self.simulation.nodes[chosen_n]

Now let's build a simulation object, where the first node uses our custom :code:`RoutingDecision` class, and the others use the built-in :code:`ciw.PSNode` class. We'll also add a state tracker for analysis::

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(
    ...     N, tracker=ciw.trackers.SystemPopulation(),
    ...     node_class=[RoutingDecision, ciw.PSNode, ciw.PSNode, ciw.PSNode])

We'll run this for 100 time units::

    >>> Q.simulate_until_max_time(100)

We can look at the state probabilities, that is, the proportion of time the system spent in each state, where a state represents the number of customers present in the system::

    >>> Q.statetracker.state_probabilities(observation_period=(10, 90)) # doctest:+SKIP
    {0: 0.425095024227593,
     1: 0.35989517302304014,
     2: 0.14629711075255158,
     3: 0.054182634504608064,
     4: 0.01124224242623659,
     5: 0.002061285633093934,
     6: 0.0012265294328765105}
