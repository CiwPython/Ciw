.. _set-seed:

=================
How to Set a Seed
=================

To ensure reproducibility of results users can set a seed for all the random number streams that Ciw uses.
This can be done using the Ciw functon :code:`ciw.seed`::
    
    >>> import ciw
    >>> ciw.seed(5)

Note that due to sampling on initialisation, the seed will need to be set **before** the :code:`ciw.Simulation` object is created.

As an example, take the following network::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=5)],
    ...     service_distributions=[ciw.dists.Exponential(rate=10)],
    ...     number_of_servers=[1]
    ... )

Now let's run the system for 20 time units, using a seed of 1, and get the average waiting time::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.0824058654563...

Using the same seed again, the exact same average waiting time result will occur::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.0824058654563...

Now using a different seed, a different result will occur::

    >>> ciw.seed(2)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.1691349404558...
