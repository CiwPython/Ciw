.. _refs-params:

==================
List of Parameters
==================

Below is a full list of the parameters that the :code:`create_network` function can take, along with a description of the values required.
If using a parameters file then here are the arguments and values of the required :code:`.yml` file.

arrival_distributions
~~~~~~~~~~~~~~~~~~~~~

*Required*

Describes the inter-arrival distributions for each node and customer class.
This is a dictionary, with keys as customer classes, and values are lists containing the inter-arrival distribution objects for each node.
If only one class of customer is required it is sufficient to simply enter a list of inter-arrival distributions.
For more details on inputting distributions, see :ref:`set-dists`.

An example is shown::

    arrival_distributions={'Class 0': [ciw.dists.Exponential(rate=2.4),
                                       ciw.dists.Uniform(lower=0.3, upper=0.5)],
                           'Class 1': [ciw.dists.Exponential(rate=3.0),
                                       ciw.dists.Deterministic(value=0.8)]}

An example where only one class of customer is required::

    arrival_distributions=[ciw.dists.Exponential(rate=2.4),
                           ciw.dists.Exponential(rate=2.0)]


batching_distributions
~~~~~~~~~~~~~~~~~~~~~~

*Optional*

Describes the discrete distributions of size of the batch arrivals for each node and customer class.
This is a dictionary, with keys as customer classes, and values are lists containing the batch distribution objects for each node.
If only one class of customer is required it is sufficient to simply enter a list of batch distributions.
For more details on batching, see :ref:`batch-arrivals`.

An example is shown::

    batching_distributions={'Class 0': [ciw.dists.Deterministic(value=1),
                                        ciw.dists.Sequential(sequence=[1, 1, 2])],
                            'Class 1': [ciw.dists.Deterministic(value=3),
                                        ciw.dists.Deterministic(value=2)]}

An example where only one class of customer is required::

    batching_distributions=[ciw.dists.Deterministic(value=2),
                            ciw.dists.Deterministic(value=1)]



baulking_functions
~~~~~~~~~~~~~~~~~~

*Optional*

A dictionary of baulking functions for each customer class and each node.
It describes the baulking mechanism of the customers.
For more details see :ref:`baulking-functions`.
If left out, then no baulking occurs.

Example::

    baulking_functions={'Class 0': [probability_of_baulking]}



class_change_matrices
~~~~~~~~~~~~~~~~~~~~~

*Optional*

A dictionary of class change matrices for each node.
For more details see :ref:`dynamic-classes`.

An example for a two node network with two classes of customer::

    class_change_matrices={'Node 0': [[0.3, 0.4, 0.3],
                                      [0.1, 0.9, 0.0],
                                      [0.5, 0.1, 0.4]],
                           'Node 1': [[1.0, 0.0, 0.0],
                                      [0.4, 0.5, 0.1],
                                      [0.2, 0.2, 0.6]]}



number_of_servers
~~~~~~~~~~~~~~~~~

*Required*

A list of the number of parallel servers at each node.
If a server schedule is used, the schedule is given instead of a number.
For more details on server schedules, see :ref:`server-schedule`.
A value of :code:`float('inf')` may be given is infinite servers are required.

Example::

    number_of_servers=[1, 2, float('inf'), 1, [[1, 10], [2, 15]]]


priority_classes
~~~~~~~~~~~~~~~~

*Optional*

A dictionary mapping customer classes to priorities.
For more information see :ref:`priority-custs`.
If left out, no priorities are used, that is all customers have equal priorities.

Example::

    priority_classes={'Class 0': 0,
                      'CLass 1': 1,
                      'Class 2': 1}



queue_capacities
~~~~~~~~~~~~~~~~

*Optional*

A list of maximum queue capacities at each node.
If ommitted, default values of :code:`float('inf')` for every node are given.

Example::

    queue_capacities=[5, float('inf'), float('inf'), 10]



routing
~~~~~~~

*Required for more than 1 node*

*Optional for 1 node*

Describes how each customer class  routes around the system.
This may be a routing matrix for each customer class, or a list routing function for process-based simulations, see :ref:`process-based`.

This is a dictionary, with keys as customer classes, and values are lists of lists (matrices) containing the routing probabilities.
If only one class of customer is required it is sufficient to simply enter single routing matrix (a list of lists).

An example is shown::

    routing={'Class 0': [[0.1, 0.3],
                         [0.0, 0.8]],
             'Class 1': [[0.0, 1.0],
                         [0.0, 0.0]]}

An example where only one class of customer is required::

    routing=[[0.5, 0.3],
             [0.2, 0.6]]

If using only one node, the default value is::

    routing={'Class 0': [[0.0]]}

Otherwise a process-based routing function::

    routing=[routing_function]



service_distributions
~~~~~~~~~~~~~~~~~~~~~

*Required*

Describes the service distributions for each node and customer class.
This is a dictionary, with keys as customer classes, and values are lists containing the service distribution objects for each node.
If only one class of customer is required it is sufficient to simply enter a list of service distributions.
For more details on inputting distributions, see :ref:`set-dists`.

An example is shown::

    service_distributions={'Class 0': [ciw.dists.Exponential(rate=4.4),
                                       ciw.dists.Uniform(lower=0.1, upper=0.9)],
                           'Class 1': [ciw.dists.Exponential(rate=6.0),
                                       ciw.dists.Lognormal(mean=0.5, sd=0.6)]}

An example where only one class of customer is required::

    service_distributions=[ciw.dists.Exponential(rate=4.8),
                           ciw.dists.Exponential(rate=5.2)]

