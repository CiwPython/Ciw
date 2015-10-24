Running a Simulation via Command Line
=====================================

This page will describe how to set up a parameters file and then how to run the experiment.
Set up a new folder alongside QNetSim that will contain your parameters file::

    .
    ├── my_simulation_instance
    │   └── parameters.yml
    │
    ├── QNetSim

The parameters.yml file is a yaml file containing all the parameters that describe the queueing network you would like to simulate.


The Parameters File
-------------------

In order to full define a queueing network simulation, the following need to be defined:

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
      - Exponential
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
- To obtain no arrivals, set :code:`Arrival_rates` to 0.
- There are many service distributions available, see :ref:`service-distributions`.
- There's a :code:`detect_deadlock` option, see :ref:`deadlock-detection`.
- The :code:`Transition_matrices` for :code:`Class 0` section represents the following transition matrix::

   [[0.1, 0.6, 0.2],
    [0.0, 0.5, 0.5],
    [0.3, 0.1, 0.1]]

In this transition matrix the `(i,j)` th element corresponds to the probability of transitioning to node `j` after service at node `i`.


Running the Simulation
----------------------

To run the simulation go to the directory which contains both :code:`QNetSim` and :code:`my_simultion_instance`.
Then run the following command::

    $ python QNetSim/scripts/run_simulation.py my_simulation_instance/

This will create a :code:`data.csv`, positioned here::

    .
    ├── my_simulation_instance
    │   └── parameters.yml
    │   └── data.csv
    ├── QNetSim

Please see :ref:`output-file` for an explanation of the data contained here.