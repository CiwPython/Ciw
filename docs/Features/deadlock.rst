.. _deadlock-detection:

=============================
Deadlock Detection Capability
=============================

Ciw's has built in deadlock detection capability. With Ciw, a queueing network can be simulated until it reaches deadlock. Ciw then records the time until deadlock from each state.

In order to take advantage of this feature, set the :code:`deadlock_detection` argument to one of the deadlock detection methods when creating the Simulation object::

    >>> Q = ciw.Simulation(N, deadlock_detector='StateDigraph') # doctest:+SKIP

Then use the :code:`simulate_until_deadlock` method. The attribute :code:`times_to_deadlock` contains the times to deadlock from each state (the state being recorded by :ref:`state-tracker`)::

    >>> import ciw
    >>> N = ciw.create_network(params) # doctest:+SKIP
    >>> Q = ciw.Simulation(N, deadlock_detector='StateDigraph') # doctest:+SKIP
    >>> Q.simulate_until_deadlock() # doctest:+SKIP
    >>> times = Q.times_to_deadlock # doctest:+SKIP

where :code:`times` is a dictionary with states as keys and times to deadlock as values.



------------------
Example - Deadlock
------------------

Consider the M/M/1/3 queue where customers have probability 0.5 of rejoining the queue after service. If the queue is full then that customer gets blocked, and hence the system deadlocks.

Parameters::

    >>> params = {'Arrival_distributions': {'Class 0': [['Exponential', 6.0]]},
    ...           'Number_of_nodes': 1,
    ...           'Number_of_servers': [1],
    ...           'Queue_capacities': [3],
    ...           'Number_of_classes': 1,
    ...           'Service_distributions': {'Class 0': [['Exponential', 5.0]]},
    ...           'Transition_matrices': {'Class 0': [[0.5]]}}

Running until deadlock::

    >>> import ciw
    >>> ciw.seed(99)
    >>> N = ciw.create_network(params)
    >>> Q = ciw.Simulation(N, deadlock_detector='StateDigraph')
    >>> Q.simulate_until_deadlock()
    >>> self.times_to_deadlock # doctest:+SKIP
    {((1, 0),): 1.0845416939916719, ((3, 0),): 0.5436399978272065, ((0, 0),): 1.1707879982560288, ((4, 0),): 0.15650986183172932, ((3, 1),): 0.0, ((2, 0),): 1.0517097907100657}

Here the state :code:`((i, j),)` denotes the state where there are `i` customers at the node, `j` of which are blocked (See :ref:`state-tracker`).
