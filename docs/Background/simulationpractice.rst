.. _simulation-practice:

===================
Simulation Practice
===================

Ensuring good practice when simulation modelling is important to get meaningful analyses from the models. A recommended book on the subject is 'Simulation: The practice of model development and use' by Stewart Robinson. This page will briefly summarise some important aspects of carrying out simulation model analysis.

--------------------------------
Performing Multiple Replications
--------------------------------

Users should not rely on the results of a single run of the simulation due to the intrinsic stochastic nature of simulation. When only running one replication, users cannot know whether the behaviour of that run is typical, extreme or unusual. To counter this multiple replications must be performed, each using different random number streams. Then analyses on the distribution of results can be performed (for example taking mean values of key performance indicators).

In Ciw, the simplest way of implementing this is to create and run the simulation in a loop, using a different random seed every time.

------------
Warm-up Time
------------

Simulation models often begin in unrealistic circumstances, that is they have unrealistic initial conditions. In Ciw, the default initial condition is an empty system. Of course there may be situations where collecting all results from an empty system is required, but in other situations, for example when analysing systems in equilibrium, these initial conditions cause unwanted bias. One standard method of overcoming this is to use a warm-up time. The simulation is run for a certain amount of time (the warm-up time) to get the system in an appropriate state before results are collected.

In Ciw, the simplest way of implementing this is to filter out records that were created before the warm-up time.

The example below shows the simplest way to perform multiple replications, and use a warm up time, in Ciw. It shows how to find the average waiting time in an M/M/1 queue::

    >>> import ciw
    >>> params = {'Arrival_distributions': [['Exponential', 5.0]],
    ...           'Service_distributions': [['Exponential', 8.0]],
    ...           'Transition_matrices': [[0.0]],
    ...           'Number_of_servers': [1]}
    >>>
    >>> average_waits = []
    >>> warmup = 50
    >>>
    >>> for s in range(100):
    ...     ciw.seed(s)
    ...     N = ciw.create_network(params)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(200)
    ...     recs = Q.get_all_records()
    ...     waits = [r.waiting_time for r in recs if r.arrival_date > warmup]
    ...     average_waits.append(sum(waits)/len(waits))
    >>>
    >>> average_wait = sum(average_waits)/len(average_waits)
    >>> print(round(average_wait, 5))
    0.21071

