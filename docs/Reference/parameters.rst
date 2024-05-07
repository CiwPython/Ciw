.. _refs-params:

==================
List of Parameters
==================

Below is a full list of the parameters that the :code:`create_network` function can take, along with a description of the values required.


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
For more details see :ref:`changeclass-afterservice`.

An example for a two node network with two classes of customer::

    class_change_matrices=[
        {'Class 0': {'Class 0': 0.3, 'Class 1': 0.4, 'Class 2': 0.3},
         'Class 1': {'Class 0': 0.1, 'Class 1': 0.9, 'Class 2': 0.0},
         'Class 2': {'Class 0': 0.5, 'Class 1': 0.1, 'Class 2': 0.4}},
        {'Class 0': {'Class 0': 1.0, 'Class 1': 0.0, 'Class 2': 0.0},
         'Class 1': {'Class 0': 0.4, 'Class 1': 0.5, 'Class 2': 0.1},
         'Class 2': {'Class 0': 0.2, 'Class 1': 0.2, 'Class 2': 0.6}}
    ]



class_change_time_distributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Optional*

A dictionary of distributions representing the time it takes to change from one class into another while waiting. For more details see :ref:`changeclass-whilequeueing`.

An example of a two class network where customers of class 0 change to customers of class 1 according to an exponential distribution::

    class_change_dist_dict = {
        'Class 0': {'Class 1': ciw.dists.Exponential(rate=5)}
    }




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



ps_thresholds
~~~~~~~~~~~~~

A list of thresholds for capacitated processor sharing queues.
For more information see :ref:`processor-sharing`.

Example::

    ps_thresholds=[3]




queue_capacities
~~~~~~~~~~~~~~~~

*Optional*

A list of maximum queue capacities at each node.
If omitted, default values of :code:`float('inf')` for every node are given.
For more details see :ref:`queue-capacities`.

Example::

    queue_capacities=[5, float('inf'), float('inf'), 10]


reneging_destinations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Optional*

A dictionary of lists representing the destination a customer goes to when they renege, or abandon the queue, while waiting. For more details see :ref:`reneging-customers`.

An example of a one node, two class network where customers of class 0 renege to node 2, and customers of class 1 renege and leave the system::

    reneging_destinations = {
        'Class 0': [2],
        'Class 1': [-1]
    }



reneging_time_distributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Optional*

A dictionary of distributions representing the time it takes for a customer to renege, or abandon the queue, while waiting. For more details see :ref:`reneging-customers`.

An example of a one node, two class network where customers of class 0 renege after a 5 time units, and customers of class 1 do not renege::

    reneging_time_distributions = {
        'Class 0': [ciw.dists.Deterministic(value=5)],
        'Class 1': [None]
    }


routing
~~~~~~~

*Required for more than 1 node*

*Optional for 1 node*

Describes how each customer class routes around the system.
This may be a routing matrix for each customer class, or a routing object, see :ref:`routing-objects`.

This is a dictionary, with keys as customer classes, and values are routing objects (or lists of of lists, matrices, containing the routing probabilities).
If only one class of customer is required it is sufficient to simply enter single routing object or matrix.

An example of using a routing object::

    routing = ciw.routing.NetworkRouting(
        routers=[
            ciw.routing.Direct(to=2),
            ciw.routing.Leave()
        ]
    )

And an example of using transition matrices is shown::

    routing={'Class 0': [[0.1, 0.3],
                         [0.0, 0.8]],
             'Class 1': [[0.0, 1.0],
                         [0.0, 0.0]]}


server_priority_functions
~~~~~~~~~~~~~~~~~~~~~~~~~

*Optional*

A function for each node that decides how to choose between multiple servers in the same node.
For more details see :ref:`server-priority`.

Example::

    server_priority_functions=[custom_server_priority]



service_disciplines
~~~~~~~~~~~~~~~~~~~

*Optional*

A list of service discipline functions, that describe the order in which customers are taken from the queue and served.
For more details see :ref:`service-disciplines`.

If omitted, FIFO service disciplines are assumed.

Example of a 3 node network, one using FIFO, one using LIFO, and one using SIRO::

    service_disciplines=[ciw.disciplines.FIFO,
                         ciw.disciplines.LIFO,
                         ciw.disciplines.SIRO]




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




system_capacity
~~~~~~~~~~~~~~~

*Optional*

The maximum queue capacity for the system.
If omitted, a default value of :code:`float('inf')` is given.
For more details see :ref:`system-capacity`.

Example::

    system_capacity=12


