.. _detect-deadlock:

======================
How to Detect Deadlock
======================

Deadlock is the phenomenon whereby all movement and customer flow in a restricted queueing network ceases, due to circular blocking.
The diagram below shows an example, where the customer at the top node is blocked to the bottom node, and the customer at the bottom node is blocked to the top node.
This circular blockage results is no more natural movement happening.

.. image:: ../_static/2nodesindeadlock.svg
   :scale: 100 %
   :alt: A 2 node queueing network in deadlock.
   :align: center

Ciw's has built in deadlock detection capability.
With Ciw, a queueing network can be simulated until it reaches deadlock.
Ciw then records the time until deadlock from each state.
(Please see the documentation on :ref:`state trackers <state-trackers>`.)

In order to take advantage of this feature, set the :code:`deadlock_detection` argument to one of the deadlock detection methods when creating the Simulation object.
Currently only :code:`'StateDigraph'` is implemented.
Then use the :code:`simulate_until_deadlock` method.
The attribute :code:`times_to_deadlock` contains the times to deadlock from each state.

Consider the :ref:`M/M/1/3 <kendall-notation>` queue where customers have probability 0.5 of rejoining the queue after service.
If the queue is full then that customer gets blocked, and hence the system deadlocks.

Parameters::

    >>> import ciw
    >>> N = ciw.create_network(
    ...    Arrival_distributions=[['Exponential', 6.0]],
    ...    Service_distributions=[['Exponential', 5.0]],
    ...    Transition_matrices=[[0.5]],
    ...    Number_of_servers=[1],
    ...    Queue_capacities=[3]
    ... )

Running until deadlock::

    >>> import ciw
    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N, deadlock_detector='StateDigraph')
    >>> Q.simulate_until_deadlock()
    >>> Q.times_to_deadlock # doctest:+SKIP
    {((0, 0),): 0.94539784..., ((1, 0),): 0.92134933..., ((2, 0),): 0.68085451..., ((3, 0),): 0.56684471..., ((3, 1),): 0.0, ((4, 0),): 0.25332344...}

Here the keys correspond to states recorded by the state tracker.



.. _state-trackers:

How to Set a State Tracker
==========================

Ciw has the option to activate a state :code:`tracker` in order to track the state of the system as the simulation progresses towards deadlock.
The default is the basic :code:`StateTracker` which does nothing (unless the simulation is detecting deadlock, in which case :code:`NaiveTracker` is the default).
The state trackers have their uses when simulating until deadlock, as a time to deadlock is recorded for every state the simulation reaches.

For a list and explanation of the state trackers that Ciw currently supports see :ref:`refs-statetrackers`.

Consider the M/M/2/1 queue with a feedback loop.
The following states are expected if a Naive Tracker is used: ((0, 0)), ((1, 0)), ((2, 0)), ((3, 0)), ((2, 1)), ((1, 2)).
Simulating until deadlock, the :code:`times_to_deadlock` dictionary will contain a subset of these states as keys::

    >>> import ciw
    >>> N = ciw.create_network(
    ...    Arrival_distributions=[['Exponential', 6.0]],
    ...    Service_distributions=[['Exponential', 5.0]],
    ...    Transition_matrices=[[0.5]],
    ...    Number_of_servers=[2],
    ...    Queue_capacities=[1]
    ... )

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N, deadlock_detector='StateDigraph', tracker='Naive')
    >>> Q.simulate_until_deadlock()
    >>> Q.times_to_deadlock # doctest:+SKIP
    {((0, 0),): 1.3354..., ((1, 0),): 1.3113..., ((1, 2),): 0.0, ((2, 0),): 1.0708..., ((2, 1),): 0.9353..., ((3, 0),): 0.9568...}

The following states are expected if a Matrix Tracker is used: ((()), (0)), ((()), (1)), ((()), (2)), ((()), (3)), (((1)), (3)), (((1, 2)), (3)).

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N, deadlock_detector='StateDigraph', tracker='Matrix')
    >>> Q.simulate_until_deadlock()
    >>> Q.times_to_deadlock # doctest:+SKIP
    {((((),),), (0,)): 1.3354..., ((((),),), (1,)): 1.3113..., ((((),),), (2,)): 1.0708..., ((((),),), (3,)): 0.9568..., ((((1,),),), (3,)): 0.9353..., ((((1, 2),),), (3,)): 0.0}

Notice that in this simple case, the Naive and Matric trackers correspond to the same states.
In other examples, where customers may get blocked in different orders and to different places, then the two trackers may track different system states.