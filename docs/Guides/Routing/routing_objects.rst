.. _routing-objects:

==========================
How to Use Routing Objects
==========================

Routing objects in Ciw are objects that determine what an individual's next node will be. There are two types:

+ **Network routing objects**: these determine routing for the entire network;
+ **Node routing objects**: these determine routing from a particular node.

Ciw has a number of these built in, however their primary use is to be defined by the user. Examples of Network routing objects are:

+ :code:`ciw.routing.TransitionMatrix`, allowing users to define :ref:`transition matrices<transition-matrix>`, that is a matrix of probabilities of being transferred to each node in the network after service at every other node.
+ :code:`ciw.routing.ProcessBased`, allowing pre-defined routes to be given to individuals when they arrive, that is :ref:`process-based routing<process-based>`.

However, the most flexible Network routing object is the generic :code:`ciw.routing.NetworkRouting`. This takes in a list of Node routing objects. Node routing objects are objects that determine routing out of a particular node. A :ref:`full list is given<refs-routing>` in the References section. The following are some of the most basic built-in routers available in Ciw, but importantly, they can also be user defined:

+ :code:`ciw.routing.Direct(to=2)`: Sends the individual directly to another node. For example here, a customer is always send to node 2.
+ :code:`ciw.routing.Leave()`: The individual leaves the system.
+ :code:`ciw.routing.Probabilistic(destinations=[1, 3], probs=[0.1, 0.4])`: Probabilistically sends the individual to either of the destination, according to their corresponding probabilities. In this case, they are send to node 1 with probability 0.1, node 3 with probability 0.4, and leave the system with the rest of the probability, 0.5.


Example
~~~~~~~

Consider a four node system:
  + At the node 1 customers are send directly to node 2;
  + At node 2 customers can be send to either nodes 1, 3 or 4 with probabilities 0.1, 0.5, and 0.4;
  + At node 3 customers can either repeat service there with probability 0.25, or leave the system;
  + At node 4, all customers leave the system.

We can construct a network routing object for this by choosing a set of node routing obejects from the list above. We place them in a list and use the :code:`routers` keyword to create the network object. In this case, the network object would be::

    >>> import ciw
    >>> R = ciw.routing.NetworkRouting(
    ...     routers=[
    ...         ciw.routing.Direct(to=2),
    ...         ciw.routing.Probabilistic(destinations=[1, 3, 4], probs=[0.1, 0.5, 0.4]),
    ...         ciw.routing.Probabilistic(destinations=[3], probs=[0.25]),
    ...         ciw.routing.Leave()
    ...     ]
    ... )

This network object can then be used to create a network::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=1), ciw.dists.Exponential(rate=1), ciw.dists.Exponential(rate=1), ciw.dists.Exponential(rate=1)],
    ...     service_distributions=[ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2)],
    ...     number_of_servers=[1, 2, 3, 1],
    ...     routing=R
    ... )


Notes
~~~~~

+ Note that a the :code:`routing` keywork when creating a network object requires a network routing object, *not* a node routing object. This is true even when there is only one node in the network.
+ Note also that, similar to the use of most other keywords when creating a network object, that routing can be customer class dependent.

For example, a one node network with two customer classes, both classes having different routing::

    >>> N = ciw.create_network(
    ...     arrival_distributions={
    ...         "Class 0": [ciw.dists.Exponential(rate=1)],
    ...         "Class 1": [ciw.dists.Exponential(rate=3)]
    ...     },
    ...     service_distributions={
    ...         "Class 0": [ciw.dists.Exponential(rate=2)],
    ...         "Class 1": [ciw.dists.Exponential(rate=2)]
    ...     },
    ...     number_of_servers=[2],
    ...     routing={
    ...         "Class 0": ciw.routing.NetworkRouting(routers=[ciw.routing.Leave()]),
    ...         "Class 1": ciw.routing.TransitionMatrix(transition_matrix=[[0.3]])
    ...     }
    ... )


Custom Routing Objects
~~~~~~~~~~~~~~~~~~~~~~

Ciw allows for custom built routing objects. These allow for both time and state dependent routing, allowing flexible and routing logic. A guide is given :ref:`here<custom-routing>`.
