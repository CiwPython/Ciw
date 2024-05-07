.. _refs-statetrackers:

==================================
List of Implemented State Trackers
==================================

Currently Ciw has the following state trackers:

- :ref:`population`
- :ref:`nodepop`
- :ref:`nodepopsubset`
- :ref:`groupednodepop`
- :ref:`nodeclssmatrix`
- :ref:`naiveblock`
- :ref:`matrixblock`


.. _population:

----------------------------
The SystemPopulation Tracker
----------------------------

The SystemPopulation Tracker records the number of customers in the whole system, regardless of which node they are at.
States take the form of a number::

    4

This denotes that there are four customers in the system.

The Simulation object takes in the optional argument :code:`tracker` used as follows::

    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation()) # doctest:+SKIP


.. _nodepop:

--------------------------
The NodePopulation Tracker
--------------------------

The NodePopulation Tracker records the number of customers at each node.
States take the form of list of numbers. An example for a three node queueing network is shown below::

    (2, 0, 5)

This denotes that there are two customers at the first node, no customers at the second node, and five customers at the third node.

The Simulation object takes in the optional argument :code:`tracker` used as follows::

    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.NodePopulation()) # doctest:+SKIP


.. _nodepopsubset:

--------------------------------
The NodePopulationSubset Tracker
--------------------------------

The NodePopulationSubset Tracker, similar to the NodePopulation Tracker, records the number of customers at each node. However this allows users to only track a subset of the nodes in the system.
States take the form of list of numbers. An example of tracking a three node queueing network is shown below::

    (2, 0, 5)

This denotes that there are two customers at the first observed node, no customers at the second observed node, and five customers at the third observed node.

The Simulation object takes in the optional argument :code:`tracker`, which takes an argument :code:`observed_nodes` a list of node numbers to observe, used as follows (observing the first, second, and fifth nodes)::

    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.NodePopulationSubset([0, 1, 4])) # doctest:+SKIP


.. _groupednodepop:

---------------------------------
The GroupedNodePopulation Tracker
---------------------------------

The GroupedNodePopulation Tracker, similar to the NodePopulation Tracker, records the number of customers at each node. However this allows users to group nodes together into one state.
States take the form of list of numbers. An example of tracking a queueing network with three grouped nodes is shown below::

    (2, 0, 5)

This denotes that there are two customers at the first group of nodes, no customers at the second group of nodes, and five customers at the third group of nodes.

The Simulation object takes in the optional argument :code:`tracker`, which takes an argument :code:`groups` a list of groups of nodes (a list of lists, nodes in the same list are in the same group), used as follows (the first group observes the total population in the 1st and 7th nodes, the second group observed the population of the 4th node, and the 3th group observes the population in the 2nd, 3rd, 5th and 6th nodes::

    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.GroupedNodePopulation(groups=[[0, 6], [3], [1, 2, 4, 5]])) # doctest:+SKIP


.. _nodeclssmatrix:

---------------------------
The NodeClassMatrix Tracker
---------------------------

The NodeClassPopulation Tracker records the number of customers at each node, split by customer class.
States take the form of matrix, that is a list of lists, where the rows denote the nodes and the columns denote the customer classes. An example for a three node queueing network with two customer classes is shown below::

    ((3, 0),
     (0, 1),
     (4, 1))

This denotes that there are:
  + Three customers at the first node - three of Class 0, and none of Class 1
  + One customer at the second node - none of Class 0, and one of Class 1
  + Five customers at the third node - four of Class 0, and one of Class 1.

The Simulation object takes in the optional argument :code:`tracker`,  which takes an argument :code:`class_ordering`, an ordered list of customerclass names to order the customer classes, used as follows::

    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.NodeClassMatrix(['Class 0', 'Class 1'])) # doctest:+SKIP


.. _naiveblock:

-------------------------
The NaiveBlocking Tracker
-------------------------

The NaiveBlocking Tracker records the number of customers at each node, and how many of those customers are currently blocked.
An example for a four node queueing network is shown below::

    ((3, 0), (1, 4), (10, 0), (8, 1))

This denotes 3 customers at the first node, 0 of which are blocked; 5 customers at the second node, 4 of which are blocked; 10 customers at the third node, 0 of which are blocked; and 9 customers at the fourth node, 1 of which are blocked.

The Simulation object takes in the optional argument :code:`tracker` used as follows::

    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.NaiveBlocking()) # doctest:+SKIP


.. _matrixblock:

--------------------------
The MatrixBlocking Tracker
--------------------------

The MatrixBlocking Tracker records the order and destination of blockages in the form of a matrix.
Alongside this the number of customers at each node is tracked.
The first component, a matrix, lists the blockages from row node to column node.
The entries are lists of all blockages of this type, and the numbers within denote the order at which these become blocked.
An example for a four node queueing network is shown below::

    ( ( ( (),  (),     (), ()  ),
        ( (),  (1, 4), (), (2) ),
        ( (),  (),     (), ()  ),
        ( (3), (),     (), ()  ) ),
      (3, 5, 10, 9) )

This denotes:

+ 3 customers at the first node
+ 5 customers at the second node
+ 10 customers at the third node
+ 9 customers at the fourth node

It also tells us the order and destination of the blockages:

+ Of the customers blocked, the first to be blocked was at node 2 to node 2
+ The second was at node 2 to node 4
+ The third was at node 4 to node 1
+ The fourth was at node 2 to node 2.

The Simulation object takes in the optional argument :code:`tracker` used as follows::

    >>> Q = ciw.Simulation(N, tracker=ciw.trackers.MatrixBlocking()) # doctest:+SKIP
