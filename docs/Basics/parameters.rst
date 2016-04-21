.. _sim-parameters:

=========================
The Simulation Parameters
=========================

In order to fully define a queueing network simulation, the following need to be defined:

- Number of nodes (service stations)
- Number of customer classes

Every node must have the following defined globally (independent of customer class):

- Number of servers
- Queue capacity

Then, for every node and every class the following must be defined:

- Arrival distribution
- Service distribution

And then each customer class requires:

- Transition matrix


A full list of the parameters that a parameters dictionary needs can be seen here: :ref:`parameters-list`.
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

There are two ways to imput parameters into the Simulation object:

* :ref:`params_dict`
* :ref:`params_file`


.. _params_dict:

-----------------------
A Parameters Dictionary
-----------------------

The Simulation object can take a dictionary containing all the kwars as keys. An example is shown::

    >>> import ciw
    >>> params = {
    ... 'Arrival_distributions': {'Class 0': [['Exponential', 6.0], ['Exponential', 2.5]]},
    ... 'Number_of_nodes': 2,
    ... 'Number_of_servers': [1, 1],
    ... 'Queue_capacities': ['Inf', 4],
    ... 'Number_of_classes': 1,
    ... 'Service_distributions': {'Class 0': [['Exponential', 8.5], ['Exponential', 5.5]]},
    ... 'Transition_matrices': {'Class 0': [[0.0, 0.2], [0.1, 0.0]]}
    ... }
    >>> N = ciw.create_network(params)
    >>> Q = ciw.Simulation(N)


.. _params_file:

-----------------
A Parameters File
-----------------

Ciw features a :code:`load_parameters` function that imports a parameters file as a dictionary. This file take is in :code:`.yml` format. An example is shown::

    parameters.yml
    
    Arrival_distributions:
      Class 0:
      - - Exponential
        - 6.0
      - - Exponential
        - 2.5
    Number_of_classes: 1
    Number_of_nodes: 2
    Number_of_servers:
    - 1
    - 1
    Queue_capacities:
    - "Inf"
    - 4
    Service_distributions:
      Class 0:
      - - Exponential
        - 8.5
      - - Exponential
        - 5.5
    Transition_matrices:
      Class 0:
      - - 0.0
        - 0.2
      - - 0.1
        - 0.0

And then to load them in::

    >>> import ciw
    >>> N = ciw.create_network('parameters.yml') # doctest:+SKIP
    >>> Q = ciw.Simulation(N) # doctest:+SKIP

The variable names are identical to the keys of the parameters dictionary.