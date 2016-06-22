.. _getting-started:

===============
Getting Started
===============

Consider the following 2 node queueing network:

.. image:: ../_static/2nodes.svg
   :scale: 100 %
   :alt: A 2 node queueing network.
   :align: center

This queueing network contains 2 nodes:

* Node 1 (Bottom)
	- Poisson arrivals at rate 6.0
	- Exponential service rate 8.5
	- Single server
	- Infinite queueing capacity
	- Probability 0.2 of joining Node 2 after service
* Node 2 (Top)
	- Poisson arrivals at rate 2.5
	- Exponential service rate 5.5
	- Single server
	- Maximum queueing capacity of 4
	- Probability 0.1 of joining Node 1 after service

We wish to simulate this system for 1000 time units. This system is defined by the following parameters dictionary::

    >>> params = {
    ... 'Arrival_distributions': {'Class 0': [['Exponential', 6.0], ['Exponential', 2.5]]},
    ... 'Number_of_nodes': 2,
    ... 'Number_of_servers': [1, 1],
    ... 'Queue_capacities': ['Inf', 4],
    ... 'Number_of_classes': 1,
    ... 'Service_distributions': {'Class 0': [['Exponential', 8.5], ['Exponential', 5.5]]},
    ... 'Transition_matrices': {'Class 0': [[0.0, 0.2], [0.1, 0.0]]}
    ... }

Please see :ref:`sim-parameters` for a fuller explaination of this.
Ciw can then create a Network obeject from this parameters dictionary, which is then used to run the simulation::

	>>> import ciw
	>>> N = ciw.create_network(params)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_time(1000)

Once this simulation has been run, :ref:`output-file` can be written to file through::

	>>> Q.write_records_to_file(<path_to_file>)  # doctest:+SKIP
