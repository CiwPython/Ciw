.. _parameters-list:

=======================
Full List of Parameters
=======================

Below is a full list of the parameters that a parameter dictionary can take, along with a description of the values required. If using a parameters file then here are the arguments and values of the required :code:`.yml` file.

Arrival_distributions
~~~~~~~~~~~~~~~~~~~~~

*Required*

Describes the inter-arrival distributions for each node and customer class.
This is a dictionary, with keys as customer classes, and values are lists describing the inter-arrival distributions for each node. If only one class of customer is required it is sufficient to simply enter a list of inter-arrival distributions. For more details on inputting distributions, see :ref:`service-distributions`.

An example is shown::

    'Arrival_distributions': {'Class 0': [['Exponential', 2.4],
                                          ['Uniform', 0.3, 0.5]],
                              'Class 1': [['Exponential', 3.0],
                                          ['Deterministic', 0.8]]}

An example where only one class of customer is required::

    'Arrival_distributions': [['Exponential', 2.4],
                              ['Exponential', 2.0]]


Class_change_matrices
~~~~~~~~~~~~~~~~~~~~~

*Optional*

A dictionary of class change matrices for each node. For more details see :ref:`dynamic-classes`.

An example for a two node network with two classes of customer::

    'Class_change_matrices': {'Node 0': [[0.3, 0.4, 0.3],
                                         [0.1, 0.9, 0.0],
                                         [0.5, 0.1, 0.4]],
                              'Node 1': [[1.0, 0.0, 0.0],
                                         [0.4, 0.5, 0.1],
                                         [0.2, 0.2, 0.6]]}


Number_of_classes
~~~~~~~~~~~~~~~~~

*Optional*

Denotes the number of customer classes in the simulation. If not included, Ciw works this out from the :code:`Arrival_distributions` argument.

Example::
    'Number_of_classes': 3


Number_of_nodes
~~~~~~~~~~~~~~~

*Optional*

Denotes the number of nodes in the queueing network. If not included, Ciw works this out from the :code:`Number_of_servers` argument.

Example::
    'Number_of_nodes': 6


Number_of_servers
~~~~~~~~~~~~~~~~~

*Required*

A list of the number of parallel servers at each node. If a server schedule is used, the name of the schedule is given instead of a number. For more details on server schedules, see :ref:`server-schedules`. A value of 'Inf' may be given is infinite servers are required.

Example::

    'Number_of_servers': [1, 2, 'Inf', 1, 'my_server_schedule']


Queue_capacities
~~~~~~~~~~~~~~~~

*Optional*

A list of maximum queue capacities at each node. If ommitted, default values of 'Inf' for every node are given.

Example::

    'Queue_capacities': [5, 'Inf', 'Inf', 10]


Service_distributions
~~~~~~~~~~~~~~~~~~~~~

*Required*

Describes the service distributions for each node and customer class.
This is a dictionary, with keys as customer classes, and values are lists describing the service distributions for each node. If only one class of customer is required it is sufficient to simply enter a list of service distributions. For more details on inputting distributions, see :ref:`service-distributions`.

An example is shown::

    'Service_distributions': {'Class 0': [['Exponential', 4.4],
                                        ['Uniform', 0.1, 0.9]],
                            'Class 1': [['Exponential', 6.0],
                                        ['Lognormal', 0.5, 0.6]]}

An example where only one class of customer is required::

    'Service_distributions': [['Exponential', 4.8],
                            ['Exponential', 5.2]]



Transition_matrices
~~~~~~~~~~~~~~~~~~~

*Required*

Describes the transition matrix for each customer class.
This is a dictionary, with keys as customer classes, and values are lists of lists (matrices) containing the transition probabilities. If only one class of customer is required it is sufficient to simply enter single transition matrix (a list of lists).

An example is shown::

    'Transition_matrices': {'Class 0': [[0.1, 0.3],
                                        [0.0, 0.8]],
                            'Class 1': [[0.0, 1.0],
                                        [0.0, 0.0]]}

An example where only one class of customer is required::

    'Transition_matrices': [[0.5, 0.3],
                            [0.2, 0.6]]

An example of a single node network with only one class of customer::

    'Transition_matrices': [[0.0]]