.. _timedependent-dists:

==========================================
How to Define Time Dependent Distributions
==========================================

In Ciw we can get a time dependent distribution, that is a service time or inter-arrival time distribution that changes as the simulation time progresses.
In order to do this a time dependent function, that returns a sampled time, must be defined.
This must take in a time variable `t`.

For example, say we wish to have arrivals once every 30 minutes in the morning, every 15 minutes over lunch, every 45 minutes in the afternoon, and every 90 minutes throughout the night::

    >>> def time_dependent_function(t):
    ...     if t % 24 < 12.0:
    ...         return 0.5
    ...     if t % 24 < 14.0:
    ...         return 0.25
    ...     if t % 24 < 20.0:
    ...         return 0.75
    ...     return 1.5

This function returns inter-arrival times of 0.5 hrs between midnight (0) and 12, 0.25 hrs between 12 and 14, 0.75 hrs between 14 and 20, and 1.5 hrs between 20 and midnight (24).
Then repeats.
Testing this function we see::

    >>> time_dependent_function(9.5)
    0.5
    >>> time_dependent_function(11.0)
    0.5
    >>> time_dependent_function(13.25)
    0.25
    >>> time_dependent_function(17.0)
    0.75
    >>> time_dependent_function(22.0)
    1.5
    >>> time_dependent_function(33.2) # half 9 the next day
    0.5

Let's implement this into a one node infinite server queue::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     Arrival_distributions=[['TimeDependent', time_dependent_function]],
    ...     Service_distributions=[['Deterministic', 0.0]],
    ...     Number_of_servers=['Inf']
    ... )

We'll then simulate this for 1 day.
We would expect 24 arrivals in the morning (12 hours, one every half an hour); 8 arrivals over lunch (2 hours, one every 15 minutes); 8 arrivals in the afternoon (6 hours, one every 45 mins); and 2 arrivals in the night (4 hours, one every hour and a half).
Therefore a total of 42 customers passed through the system::

   >>> Q = ciw.Simulation(N)
   >>> Q.simulate_until_max_time(24.0)

   >>> len(Q.nodes[-1].all_individuals)
   42

Time dependent function can be used for batching distributions too.
In this case the time dependent function must return the number of individuals that must enter the simulation at the given time.
Note that the function must return a float number, but the result will then be rounded to the nearest integer.
The function may return zero, if no individuals are expected to enter the simulation at the given time.