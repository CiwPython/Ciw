.. _set-seed:

=================
How to Set a Seed
=================

Users may wish to ensure that exactly the same steam of random numbers is used everytime a simulation is run. This ensures reproducibility of results. This can be done by setting the seed for all random number streams that Ciw uses. This can be done using the Ciw functon :code:`ciw.seed`::
    
    >>> import ciw
    >>> ciw.seed(5)

Note that due to sampling on initialisation, the seed will need to be set **before** the :code:`ciw.Simulation` object is created.

As an example, take the following network::

    >>> params = {
    ...     'Arrival_distributions': [['Exponential', 5]],
    ...     'Service_distributions': [['Exponential', 10]],
    ...     'Transition_matrices': [[0.0]],
    ...     'Number_of_servers': [1]
    ... }
    >>> N = ciw.create_network(params)

Now let's run the system for 20 time units, using a seed of 1, and get the average waiting time::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.0544115013161...

Using the same seed again, the exact same average waiting time result will occur::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.0544115013161...

Now using a different seed, a different result will occur::

    >>> ciw.seed(2)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.0832990490158...
