.. _transition-matrix:

==============================================
How to Define Routing with a Transition Matrix
==============================================

There are a number of methods of defining how customers are routed from one node to another after service. This is done with the :code:`routing` keyword when creating a network.

One common method is by defining a transition matrix, common when defining Jackson networks [JJ57]_.
A transition matrix is an :math:`n \times n` matrix (where :math:`n` is the number of nodes in the network) such that the :math:`(i,j)\text{th}` element corresponds to the probability of transitioning to node :math:`j` after service at node :math:`i`.

For example, in a three node network, a transition matrix might look like:

.. math::

    \begin{pmatrix}
    0.0 & 0.3 & 0.7 \\
    0.0 & 0.0 & 1.0 \\
    0.0 & 0.0 & 0.2 \\
    \end{pmatrix}

This represents that:
  + customers finishing service at node 1 enter node 2 with probability 0.3, and envet node 3 with probability 0.7;
  + customers finishing service at node 2 are certain to enter node 3;
  + customers finishing service at node 3 re-enter node 3 with probability 0.2, and with probability 0.8 leave the system.

In Ciw there are two ways to define this, with a list of lists, or a :ref:`routing object<routing-objects>`.


List of Lists
~~~~~~~~~~~~~

To define this with a list of lists, we can use::
    
    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[
    ...         ciw.dists.Exponential(1),
    ...         ciw.dists.Exponential(1),
    ...         ciw.dists.Exponential(1)
    ...     ],
    ...     service_distributions=[
    ...         ciw.dists.Exponential(2),
    ...         ciw.dists.Exponential(2),
    ...         ciw.dists.Exponential(2)
    ...     ],
    ...     number_of_servers=[3, 3, 3],
    ...     routing=[
    ...         [0.0, 0.3, 0.7],
    ...         [0.0, 0.0, 0.1],
    ...         [0.0, 0.0, 0.2]
    ...     ]
    ... )


Routing Object
~~~~~~~~~~~~~~

To define with with a routing object we can make use of the built-in :code:`TransitionMatrix` routing object, and give it the list of lists above::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[
    ...         ciw.dists.Exponential(1),
    ...         ciw.dists.Exponential(1),
    ...         ciw.dists.Exponential(1)
    ...     ],
    ...     service_distributions=[
    ...         ciw.dists.Exponential(2),
    ...         ciw.dists.Exponential(2),
    ...         ciw.dists.Exponential(2)
    ...     ],
    ...     number_of_servers=[3, 3, 3],
    ...     routing=ciw.routing.TransitionMatrix(
    ...         transition_matrix=[
    ...             [0.0, 0.3, 0.7],
    ...             [0.0, 0.0, 0.1],
    ...             [0.0, 0.0, 0.2]
    ...         ]
    ...     )
    ... )

Routing objects can be much more flexible that this, allowing logic based routing in addition to probabilistic based routing. More information can be found :ref:`here<routing-objects>`.

