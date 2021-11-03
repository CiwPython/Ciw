.. _simulation-practice:

===================
Simulation Practice
===================

Ensuring good practice when simulation modelling is important to get meaningful analyses from the models.
This is shown in :ref:`Tutorial IV <tutorial-iv>`.
A recommended resource on the subject is [SW14]_.
This page will briefly summarise some important aspects of carrying out simulation model analysis.

-------------------------------
Performing Multiple Repetitions
-------------------------------

Users should not rely on the results of a single run of the simulation due to the intrinsic stochastic nature of simulation.
When only running one repetition, users cannot know whether the behaviour of that run is typical, extreme or unusual.
To counter this multiple replications must be performed, each using different random number streams.
Then analyses on the distribution of results can be performed (for example taking mean values of key performance indicators).

In Ciw, the simplest way of implementing this is to create and run the simulation in a loop, using a different random seed every time.

------------
Warm-up Time
------------

Simulation models often begin in unrealistic circumstances, that is they have unrealistic initial conditions.
In Ciw, the default initial condition is an empty system.
Of course there may be situations where collecting all results from an empty system is required, but in other situations, for example when analysing systems in equilibrium, these initial conditions cause unwanted bias.
One standard method of overcoming this is to use a warm-up time.
The simulation is run for a certain amount of time (the warm-up time) to get the system in an appropriate state before results are collected.

In Ciw, the simplest way of implementing this is to filter out records that were created during the warm-up time.


--------------
Cool-down Time
--------------

If collecting records using the :code:`get_all_records` method, then this will only collect completed records.
There may be a need to collect arrival or waiting information of those individuals still in service.
In Ciw, we can do this by simulating past the end of the observation period, and then only collect those relevant records that are in the observation period.

In Ciw, the simplest way of implementing this is to filter out records that were created after the cool-down time began.



-------
Example
-------


The example below shows the simplest way to perform multiple replications, and use a warm-up and cool-down time, in Ciw.
It shows how to find the average waiting time in an :ref:`M/M/1 <kendall-notation>` queue::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=5.0)],
    ...     service_distributions=[ciw.dists.Exponential(rate=8.0)],
    ...     routing=[[0.0]],
    ...     number_of_servers=[1]
    ... )
    >>>
    >>> average_waits = []
    >>> warmup = 10
    >>> cooldown = 10
    >>> maxsimtime = 40
    >>>
    >>> for s in range(25):
    ...     ciw.seed(s)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(warmup + maxsimtime + cooldown)
    ...     recs = Q.get_all_records()
    ...     waits = [r.waiting_time for r in recs if r.arrival_date > warmup and r.arrival_date < warmup + maxsimtime]
    ...     average_waits.append(sum(waits) / len(waits))
    >>>
    >>> average_wait = sum(average_waits) / len(average_waits)
    >>> average_wait
    0.201313...

