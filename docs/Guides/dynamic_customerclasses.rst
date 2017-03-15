.. _dynamic-classes:

===================================
How to Set Dynamic Customer Classes
===================================

Ciw allows customers to probabilistically change their class after service. That is after service at node `k` a customer of class `i` will become class `j` with probability :math:`P(J=j | I=i, K=k)`. These probabilities are input into the system through the :code:`Class_change_matrices` option.

Consider a one node system with three classes of customer. After service (at Node 1) customers always change customer class, equally likely between the two other customer classes. The :code:`Class_change_matrices` for this system are shown below:
    
    +-----------------+
    | Node 1          |
    +=====+=====+=====+
    | 0.0 | 0.5 | 0.5 |
    +-----+-----+-----+
    | 0.5 | 0.0 | 0.5 |
    +-----+-----+-----+
    | 0.5 | 0.5 | 0.0 |
    +-----+-----+-----+


This is input into the simulation model by including :code:`Class_change_matrices` in the parameters dictionary::
    
    >>> params = {
    ...     'Arrival_distributions': {'Class 0': [['Exponential', 5]],
    ...                               'Class 1': ['NoArrivals'],
    ...                               'Class 2': ['NoArrivals']},
    ...     'Service_distributions': {'Class 0': [['Exponential', 10]],
    ...                               'Class 1': [['Exponential', 10]],
    ...                               'Class 2': [['Exponential', 10]]},
    ...     'Transition_matrices': {'Class 0': [[1.0]],
    ...                             'Class 1': [[1.0]],
    ...                             'Class 2': [[1.0]]},
    ...     'Class_change_matrices': {'Node 1': [[0.0, 0.5, 0.5],
    ...                                          [0.5, 0.0, 0.5],
    ...                                          [0.5, 0.5, 0.0]]},
    ...     'Number_of_servers': [1]
    ... }

Notice in this parameters dictionary only arrivals from Class 0 customer occur. Running this system, we'll see that the count of the number of records with customer classes 1 and 2 more than zero, as some Class 0 customers have changed class after service::

    >>> import ciw
    >>> from collections import Counter

    >>> ciw.seed(1)
    >>> N = ciw.create_network(params)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(50.0)
    >>> recs = Q.get_all_records()
    >>> Counter([r.customer_class for r in recs])
    Counter({0: 255, 1: 105, 2: 125})
