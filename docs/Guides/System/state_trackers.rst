.. _state-trackers:

===============================
How to Track the System's State
===============================

The system's state is the configuration of individuals around the system. It can be measured in a variety of ways - for example, a state can be the number of customers waiting at each node.

Ciw has the option to activate a state :code:`tracker` in order to track the state of the system as the simulation progresses through the simulation. This tracker has a number of uses: the system state's full history can be obtained, from which state probabilities can be found, and it has uses when investigating deadlock.

The default is the basic :code:`StateTracker` which does nothing.
A number of other state trackers can be implemented, which record the system's state in a number of ways. These objects inherit from the basic :code:`StateTracker` class, and so custom state trackers can also be implemented by doing this.
For a list and explanation of the state trackers that Ciw currently supports see :ref:`refs-statetrackers`.


Example: consider an M/M/1 queue. The :code:`SystemPopulation` tracker defines a state as the number of individuals in the system::

    >>> import ciw
    >>> N = ciw.create_network(
    ...    arrival_distributions=[ciw.dists.Exponential(rate=0.1)],
    ...    service_distributions=[ciw.dists.Exponential(rate=0.2)],
    ...    number_of_servers=[1]
    ... )

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N,
    ...     tracker=ciw.trackers.SystemPopulation()
    ... )
    >>> Q.simulate_until_max_time(250)

Now the system's history can be viewed::

    >>> Q.statetracker.history # doctest:+SKIP
    [[0.0, 0],
     [1.44291..., 1],
     [10.84369..., 0],
     [15.87259..., 1],
     [17.34491..., 0],
     [22.71318..., 1],
     [25.69774..., 0],
     ...
    ]                                  

This shows that the system was in state :code:`0` from time 0.0 to 1.44291, was in state :code:`1` from time 1.44291 to 10.84369, went back to state :code:`0` from 10.84369 to time 15.87259, and so on.

From this we can obtain the proportion of time the system spend in each state::

    >>> Q.statetracker.state_probabilities() # doctest:+SKIP
    {0: 0.55425..., 1: 0.24676..., 2: 0.13140..., 3: 0.06757...}

So the system was in state :code:`0` (no individuals in the system) 55.4% of the time, in state :code:`1` (one individual in the system) 24.7% of the time, state :code:`2` (two individuals in the system) 13.1% of the time, and state :code:`3` (three individuals in the system) 6.8% of the time.

If a warm up and cool down time is required when calculating the state probabilities, we can put in an observation period. For example, if we with to find the proportion of time the system spend in each state, between dates :code:`50` and :code:`200`, then we can use the following::

    >>> Q.statetracker.state_probabilities(observation_period=(50, 200)) # doctest:+SKIP

Note that different trackers represent different states in different ways, see :ref:`refs-statetrackers` for a list of implemented trackers.

