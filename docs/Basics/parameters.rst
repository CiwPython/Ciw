.. _parameters-file:

===================
The Parameters File
===================

In order to fully define a queueing network simulation, the following need to be defined:

- Number of nodes (service stations)
- Number of customer classes
- Simulation run time

Every node must have the following defined globally (independent of customer class):

- Number of servers
- Queue capacity

Then, for every node and every class the following must be defined:

- Arrival rate
- Service distribution

And then each customer class requires:

- Transition matrix

A full example of the parameters file for a three node network with two classes of customer is shown below::

    Arrival_rates:
      Class 0:
      - 6.0
      - 4.5
      - 2.0
      Class 1:
      - 1.0
      - 1.8
      - 7.25
    detect_deadlock: False
    Number_of_classes: 2
    Number_of_nodes: 3
    Number_of_servers:
    - 2
    - 1
    - 1
    Queue_capacities:
    - "Inf"
    - "Inf"
    - 10
    Service_rates:
      Class 0:
      - - Exponential
        - 7.0
      - - Exponential
        - 5.0
      - - Gamma
        - 0.4
        - 0.6
      Class 1:
      - - Exponential
        - 8.5
      - - Triangular
        - 0.1
        - 0.8
        - 0.95
      - - Exponential
        - 3.0
    Simulation_time: 2500
    Transition_matrices:
      Class 0:
      - - 0.1
        - 0.6
        - 0.2
      - - 0.0
        - 0.5
        - 0.5
      - - 0.3
        - 0.1
        - 0.1
      Class 1:
      - - 0.7
        - 0.05
        - 0.05
      - - 0.5
        - 0.1
        - 0.4
      - - 0.2
        - 0.2
        - 0.2

The variable names and format of the :code:`.yml` file are very important.
Notice that:

- :code:`Queue_capacities` can be set to :code:`"Inf"`.
- When :code:`Queue_capacities` aren't set to :code:`"Inf"` blocking rules apply. Type I (blocked after service) blocking applies here.
- :code:`Number_of_servers` may be set to `"Inf"` also.
- To obtain no arrivals, set :code:`Arrival_rates` to 0.
- There are many service distributions available, see :ref:`service-distributions`.
- There are numerous other features, please see :ref:`features` for more information.
- The :code:`Transition_matrices` for :code:`Class 0` section represents the following transition matrix::

   [[0.1, 0.6, 0.2],
    [0.0, 0.5, 0.5],
    [0.3, 0.1, 0.1]]

In this transition matrix the `(i,j)` th element corresponds to the probability of transitioning to node `j` after service at node `i`.

When not using the command line tool, ASQ takes in a parameters dictionary, please read :ref:`parameters-dict`.
