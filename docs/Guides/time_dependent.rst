.. _timedependent-dists:

====================================================
How to Define Time and State Dependent Distributions
====================================================

By defining custom distribution obejcts, both time-dependent and state-dependent distributions can be defined.
They could be combined to create time-and-state-dependent distributions too.

This custom distribution object must inherit from the gerenic :code:`ciw.dists.Distribution` object, and define a :code:`.sample` method that returns a sampled time.
This method needs to take in a time variable :code:`t`, and also the concerned individual :code:`ind`.


Time Dependent Distributions
----------------------------

In Ciw we can get a time dependent distribution, that is a service time, inter-arrival time, or batching distribution that changes as the simulation time progresses.
In order to do this a time dependent distribution object, that has a :code:`sample` method to sample the time, must be defined.

For example, say we wish to have arrivals once every 30 minutes in the morning, every 15 minutes over lunch, every 45 minutes in the afternoon, and every 90 minutes throughout the night::

    >>> import ciw
    >>> class TimeDependentDist(ciw.dists.Distribution):
    ...     def sample(self, t, ind=None):
    ...         if t % 24 < 12.0:
    ...             return 0.5
    ...         if t % 24 < 14.0:
    ...             return 0.25
    ...         if t % 24 < 20.0:
    ...             return 0.75
    ...         return 1.5

This function returns inter-arrival times of 0.5 hrs between midnight (0) and 12, 0.25 hrs between 12 and 14, 0.75 hrs between 14 and 20, and 1.5 hrs between 20 and midnight (24).
Then repeats.
Testing this function we see::

    >>> D = TimeDependentDist()
    >>> D.sample(9.5)
    0.5
    >>> D.sample(11.0)
    0.5
    >>> D.sample(13.25)
    0.25
    >>> D.sample(17.0)
    0.75
    >>> D.sample(22.0)
    1.5
    >>> D.sample(33.2) # half 9 the next day
    0.5

Let's implement this into a one node infinite server queue::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[TimeDependentDist()],
    ...     service_distributions=[ciw.dists.Deterministic(value=0.0)],
    ...     number_of_servers=['Inf']
    ... )

We'll then simulate this for 1 day.
We would expect 24 arrivals in the morning (12 hours, one every half an hour); 8 arrivals over lunch (2 hours, one every 15 minutes); 8 arrivals in the afternoon (6 hours, one every 45 mins); and 2 arrivals in the night (4 hours, one every hour and a half).
Therefore a total of 42 customers passed through the system::

   >>> Q = ciw.Simulation(N)
   >>> Q.simulate_until_max_time(24.0)
   >>> len(Q.nodes[-1].all_individuals)
   42




State Dependent Distributions
-----------------------------

In adddition to the time parameter :code:`t`, the sample method takes in the concerned individual :code:`ind`.
Therefore individuals can use this individual's attributes when sampling a service time (*note it does not make sense to use this to sample inter-arrival times as that individual has not been created yet!*).
This individual has a :code:`ind.simulation` attribute, which points to the :code:`Simulation` object, meaning it has access to the whole state of the system.

Now we can take advantage of this to define state dependent distributions.

As an example, let's define a distribution for a one node system that returns:
    + :code:`0.20` if there are 0 people at that node,
    + :code:`0.15` if there is 1 person at that node,
    + :code:`0.10` if there are 2 people at that node,
    + :code:`0.05` if there are 3 people at that node,
    + :code:`0.00` otherwise.
 
This corresponds the the function:
    
    $$\max(-0.05n + 0.2, 0)$$
 
where :math:`n` is the number of customers at that node.
Write a distribution class to use::

    >>> class StateDependentDist(ciw.dists.Distribution):
    ...     def sample(self, t=None, ind=None):
    ...         n = ind.simulation.statetracker.state
    ...         return max((-0.05*n) + 0.2, 0)

where we access the system's state by considering the :ref:`state tracker <state-trackers>`.
Now to test if this is working, the average service time should be roughly equal to the above function applied to the average queue size::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=4)],
    ...     service_distributions=[StateDependentDist()],
    ...     number_of_servers=[1]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
    >>> Q.simulate_until_max_time(500)
    >>> recs = Q.get_all_records()

    >>> services = [r.service_time for r in recs if r.arrival_date > 100]
    >>> sum(services) / len(services)
    0.1549304...

    >>> average_queue_size = sum(s*p for s, p in Q.statetracker.state_probabilities().items())
    >>> (-0.05 * average_queue_size) + 0.2
    0.1552347...

For arrival distributions - when creating the :code:`Simulation` object, the distribution objects are given a :code:`.simulation` attribute, so something similar can happen. For example, the following distribution will sample form an Exponential distribution unil :code:`limit` number of individuals has been sampled::

    >>> class LimitedExponential(ciw.dists.Exponential):
    ...     def __init__(self, rate, limit):
    ...         super().__init__(rate)
    ...         self.limit = limit
    ...         
    ...     def sample(self, t=None, ind=None):
    ...         if self.simulation.nodes[0].number_of_individuals < self.limit:
    ...             return super().sample()
    ...         else:
    ...             return float('Inf')

And to see it working, a limit of 44 individuals::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[LimitedExponential(rate=1, limit=44)],
    ...     service_distributions=[ciw.dists.Exponential(rate=3)],
    ...     number_of_servers=[2]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(3000)
    >>> recs = Q.get_all_records()
    >>> len(recs)
    44