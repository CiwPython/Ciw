.. system-capacity:

===================================================
How to Set a Maximium Capacity for the Whole System
===================================================

We have seen that :ref:`node capacities<_tutorial-vi>` can define restricted queueing networks. Ciw also allows for a whole system capacity to be set. When a system capacity is set, when the total number of customers present in *all* the nodes of the system is equal to the system capacity, then newly arriving customers will be rejected. Once the total number of customers drops back below the system capacity, then customers will be accepted into the system again.

In order to implement this, we use the :code:`system_capacity` keyworks when creating the network::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=2),
    ...                            ciw.dists.Exponential(rate=1)],
    ...     service_distributions=[ciw.dists.Exponential(rate=1),
    ...                            ciw.dists.Exponential(rate=1)],
    ...     routing=[[0.0, 0.5],
    ...              [0.0, 0.0]],
    ...     number_of_servers=[3, 2],
    ...     system_capacity=4
    ... )

In this case, the total capacity of nodes 1 and 2 is 4, and the system will never have more than 4 individuals. To see this, let's run this with a :ref:`state tracker<state-trackers>` and see that the system never reaches more than 4 people::

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
    >>> Q.simulate_until_max_time(100)
    >>> state_probs = Q.statetracker.state_probabilities()
    >>> state_probs
    {0: 0.03369655546653017, 1: 0.1592711312247873, 2: 0.18950832844418355, 3: 0.2983478656854591, 4: 0.31917611917904}

