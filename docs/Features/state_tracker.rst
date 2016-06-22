.. _state-tracker:

==============
State Trackers
==============

Ciw has the option to activate a :code:`statetracker` in order to track the state of the system as the simulation progresses. The default is the basic :code:`StateTracker` which does nothing (unless the simulation is detecting deadlock, otherwise :code:`NaiveTracker` is the default). The state trackers have their uses when simulating until deadlock, as a time to deadlock is recorded for every state the simulation reaches.

Currently Ciw has the following state trackers:

- :ref:`naive`
- :ref:`matrix`


.. _naive:

-----------------
The Naïve Tracker
-----------------

The Naïve Tracker records the number of customers at each node, and how many of those customers are currently blocked.
An example for a four node queueing network is shown below::

    ((3, 0), (1, 4), (10, 0), (8, 1))

This denotes 3 customers at the first node, 0 of which are blocked; 5 customers at the second node, 4 of which are blocked; 10 customers at the third node, 0 of which are blocked; and 9 customers at the fourth node, 1 of which are blocked.

The Simulation object takes in the optional argument :code:`tracker` used as follows::

    >>> Q = ciw.Simulation(N, tracker='Naive') # doctest:+SKIP


.. _matrix:

------------------
The Matrix Tracker
------------------

The Matrix Tracker records the order and destination of blockages in the form of a matrix. Alongside this the number of customers at each node is tracked. The first component, a matrix, lists the blockages from row node to column node. The entries are lists of all blockages of this type, and the numbers within denote the order at which these become blocked.
An example for a four node queueing network is shown below::

    ( ( ( (),  (),     (), ()  ),
        ( (),  (1, 4), (), (2) ),
        ( (),  (),     (), ()  ),
        ( (3), (),     (), ()  ) ),
      ( 3, 5, 10, 9) )

This denotes 3 customers at the first node, 5 customers at the second node, 10 customers at the third node, and 9 customers at the fourth node. It also tells us the order and destination of the blockages. Of the customers blocked, the first to be blocked was at node 2 to node 2; the second was at node 2 to node 4; the third was at node 4 to node 1; the fourth was at node 2 to node 2.

The Simulation object takes in the optional argument :code:`tracker` used as follows::

    >>> Q = ciw.Simulation(N, tracker='Matrix') # doctest:+SKIP
