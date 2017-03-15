.. _state-trackers:

==========================
How to Set a State Tracker
==========================

Ciw has the option to activate a state :code:`tracker` in order to track the state of the system as the simulation progresses. The default is the basic :code:`StateTracker` which does nothing (unless the simulation is detecting deadlock, otherwise :code:`NaiveTracker` is the default). The state trackers have their uses when simulating until deadlock, as a time to deadlock is recorded for every state the simulation reaches.

For a list and explanation of the state trackers that Ciw currently supports see :ref:`refs-statetrackers`.

Consider the M/M/2/1 queue with feedback loop. The following states are expected if a Naïve Tracker is used: ((0, 0)), ((1, 0)), ((2, 0)), ((3, 0)), ((2, 1)), ((1, 2)). Simulating until deadlock, the :code:`times_to_deadlock` dictionary will contain a subset of these states as keys::

    >>> import ciw
    >>> params = {'Arrival_distributions': [['Exponential', 6.0]],
    ...           'Service_distributions':[['Exponential', 5.0]],
    ...           'Transition_matrices': [[0.5]],
    ...           'Number_of_servers': [2],
    ...           'Queue_capacities': [1]}

    >>> ciw.seed(1)
    >>> N = ciw.create_network(params)
    >>> Q = ciw.Simulation(N, deadlock_detector='StateDigraph', tracker='Naive')
    >>> Q.simulate_until_deadlock()
    >>> Q.times_to_deadlock # doctest:+SKIP
    {((0, 0),): 1.3354..., ((1, 0),): 1.3113..., ((1, 2),): 0.0, ((2, 0),): 1.0708..., ((2, 1),): 0.9353..., ((3, 0),): 0.9568...}

The following states are expected if a Matrix Tracker is used: ((()), (0)), ((()), (1)), ((()), (2)), ((()), (3)), (((1)), (3)), (((1, 2)), (3)).

    >>> ciw.seed(1)
    >>> N = ciw.create_network(params)
    >>> Q = ciw.Simulation(N, deadlock_detector='StateDigraph', tracker='Matrix')
    >>> Q.simulate_until_deadlock()
    >>> Q.times_to_deadlock # doctest:+SKIP
    {((((),),), (0,)): 1.3354..., ((((),),), (1,)): 1.3113..., ((((),),), (2,)): 1.0708..., ((((),),), (3,)): 0.9568..., ((((1,),),), (3,)): 0.9353..., ((((1, 2),),), (3,)): 0.0}

Notice that in this simple case, the Naïve and Matric trackers correspond to the same states. In other examples, where customers may get blocked in different orders and to different places, then the two trackers may track different system states.