.. _parameters-dict:

=========================
The Parameters Dictionary
=========================

In order to fully define a queueing network simulation, the following need to be defined:

- Number of nodes (service stations)
- Number of customer classes
- Simulation run time

Every node must have the following defined globally (independent of customer class):

- Number of servers
- Queue capacity

Then, for every node and every class the following must be defined:

- Arrival distribution
- Service distribution

And then each customer class requires:

- Transition matrix

A full example of the parameters dictionary for a three node network with two classes of customer is shown below::

    >>> params = {'Arrival_distributions': {'Class 1': [['Exponential', 1.0], ['Exponential', 1.8], ['Exponential', 7.25]],
    ...                             'Class 0': [['Exponential', 6.0], ['Exponential', 4.5], ['Exponential', 2.0]]},
    ...           'Number_of_nodes': 3,
    ...           'Detect_deadlock': False,
    ...           'Simulation_time': 2500,
    ...           'Number_of_servers': [2, 1, 1],
    ...           'Queue_capacities': ['Inf', 'Inf', 10],
    ...           'Number_of_classes': 2,
    ...           'Service_distributions': {'Class 1': [['Exponential', 8.5], ['Triangular', 0.1, 0.8, 0.95], ['Exponential', 3.0]],
    ...                                     'Class 0': [['Exponential', 7.0], ['Exponential', 5.0], ['Gamma', 0.4, 0.6]]},
    ...           'Transition_matrices': {'Class 1': [[0.7, 0.05, 0.05], [0.5, 0.1, 0.4], [0.2, 0.2, 0.2]],
    ...                                   'Class 0': [[0.1, 0.6, 0.2], [0.0, 0.5, 0.5], [0.3, 0.1, 0.1]]}}


Notice that:

- :code:`Queue_capacities` can be set to :code:`"Inf"`.
- When :code:`Queue_capacities` aren't set to :code:`"Inf"` blocking rules apply. Type I (blocked after service) blocking applies here.
- :code:`Number_of_servers` may be set to `"Inf"` also.
- To obtain no arrivals, set :code:`Arrival_distributions` to :code:`'NoArrivals'`.
- There are many service distributions available, see :ref:`service-distributions`.
- The :code:`Transition_matrices` for :code:`Class 0` section represents the following transition matrix::

   [[0.1, 0.6, 0.2],
    [0.0, 0.5, 0.5],
    [0.3, 0.1, 0.1]]

In this transition matrix the `(i,j)` th element corresponds to the probability of transitioning to node `j` after service at node `i`.


There are numerous other features, please see :ref:`features` for more information.

The keys of this dictionary may also be used as keyword arguments when defining a simulation. Ciw features a function that will load in these parameters from a file, please read :ref:`parameters-file`.
