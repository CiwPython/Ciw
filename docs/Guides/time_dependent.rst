.. _timedependent-dists:

==========================================
How to Define Time Dependent Distributions
==========================================

In Ciw we can get a time dependent distribution, that is a service time or inter-arrival time distribution that changes as the simulation time progresses.
In order to do this a time dependent function, that returns a sampled time, must be defined.
This must take in a time variable `t`.

For example, say we wish to have arrivals once every 30 minutes in the morning, every 15 minutes over lunch, every 45 minutes in the afternoon, and every 90 minutes throughout the night::

    >>> def my_time_dependent_distribution(t):
    ...     if t % 24 < 12.0:
    ...         return 0.5
    ...     if t % 24 < 14.0:
    ...         return 0.25
    ...     if t % 24 < 20.0:
    ...         return 0.75
    ...     return 1.5

This function returns inter-arrival times of 0.5 hrs between midnight (0) and 12, 0.25 hrs between 12 and 14, 0.75 hrs between 14 and 20, and 1.5 hrs between 20 and midnight (24).
Then repeats. Testing this function we see::

    >>> my_time_dependent_distribution(9.5)
    0.5
    >>> my_time_dependent_distribution(11.0)
    0.5
    >>> my_time_dependent_distribution(13.25)
    0.25
    >>> my_time_dependent_distribution(17.0)
    0.75
    >>> my_time_dependent_distribution(22.0)
    1.5
    >>> my_time_dependent_distribution(33.2) # half 9 the next day
    0.5

Let's implement this into a one node infinite server queue::

    >>> params = {
    ...     'Arrival_distributions': [['TimeDependent', lambda t : my_time_dependent_distribution(t)]],
    ...     'Service_distributions': [['Deterministic', 0.0]],
    ...     'Transition_matrices': [[0.0]],
    ...     'Number_of_servers': ['Inf']
    ... }

We'll then simulate this for 1 day.
We would expect 24 arrivals in the morning (12 hours, one every half an hour); 8 arrivals over lunch (2 hours, one every 15 minutes), 8 arrivals in the afternoon (6 hours, one every 45 mins); and 2 arrivals in the night (4 hours, one every hour and a half).
Therefore a total of customers passed through the system::

   >>> import ciw
   >>> N = ciw.create_network(params)
   >>> Q = ciw.Simulation(N)
   >>> Q.simulate_until_max_time(24.0)

   >>> len(Q.nodes[-1].all_individuals)
   42
