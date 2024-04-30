.. _refs-routing:

=======================
List of Routing Objects
=======================

Ciw allows a number network router objects and node router objects.
The following network routers are currently supported:

- :ref:`network_router`
- :ref:`trans_mat`
- :ref:`pb_route`

The following node routers are currently supported:

- :ref:`leave`
- :ref:`direct`
- :ref:`probabilistic`
- :ref:`jsq`
- :ref:`load_balancing`



Network Routing Objects
=======================

.. _network_router:

--------------------------
The General Network Router
--------------------------

The general network router allows us to define separate node routing objects for each node. For a two node network::

    ciw.routing.NetworkRouting(
        routers=[
            ciw.routing.NodeRouting(), # should be replaced with one of the node routers below
            ciw.routing.NodeRouting(), # should be replaced with one of the node routers below
            ciw.routing.NodeRouting()  # should be replaced with one of the node routers below
        ]
    )


.. _trans_mat:

----------------------------
The Transition Matrix Router
----------------------------

The :ref:`transition matrix<transition-matrix>` router takes in a transition matrix, a list of lists, with elements :math:`R_{ij}` representing the probability of entering node :math:`j` after service at node :math:`i`. For a two node network::

    ciw.routing.TransitionMatrix(
        transition_matrix=[
            [0.2, 0.8],
            [0.0, 0.3]
        ]
    )


.. _pb_route:

------------------------
The Process Based Router
------------------------

The :ref:`process based<process-based>` router takes in a function that returns a pre-defined list of destinations that a customer will follow in order. E.g. all routing where all customers go to Node 2, then Node 1, then Node 1 again::

    ciw.routing.ProcessBased(
        routing_function=lambda ind, simulation: [2, 1, 1]
    )




Node Routing Objects
====================

.. _leave:

-----
Leave
-----

Leaves the system after service at the node::

    ciw.routing.Leave()


.. _direct:

------
Direct
------

The customer goes direct to another node after service at the node. E.g. going to Node 2 direct form the node::

    ciw.routing.Direct(to=2)



.. _probabilistic:

-------------
Probabilistic
-------------

The customer is routed to another node probabilistically after service at the node. E.g. going to Node 1 with probability 0.4, and Node 3 with probability 0.1::

    ciw.routing.Probabilistic(
        destinations=[1, 3],
        probs=[0.4, 0.1]
    )


.. _jsq:

-------------------
Join Shortest Queue
-------------------

The customer goes :ref:`joins the shortest queue<join-shortest-queue>` out of a subset of destinations::

    ciw.routing.JoinShortestQueue(destinations=[1, 3], tie_break='random')

The :code:`tie_break` argument is optional, and can take one of two strings: :code:`'random'` or :code:`'order'`. When there is a tie between the nodes with the shortest queue, tie breaks are either dealt with by choosing randomly between the ties (:code:`'random'`), or take precedence by the order listed in the :code:`destinations` list (:code:`'order'`). If omitted, random tie-breaking is used.

.. _load_balancing:


--------------
Load Balancing
--------------

The customer goes :ref:`joins the node with the least amount of customers present<example_lb>` out of a subset of destinations::

    ciw.routing.LoadBalancing(destinations=[1, 3], tie_break='random')

The :code:`tie_break` argument is optional, and can take one of two strings: :code:`'random'` or :code:`'order'`. When there is a tie between the nodes with the least amount of customers present, tie breaks are either dealt with by choosing randomly between the ties (:code:`'random'`), or take precedence by the order listed in the :code:`destinations` list (:code:`'order'`). If omitted, random tie-breaking is used.
