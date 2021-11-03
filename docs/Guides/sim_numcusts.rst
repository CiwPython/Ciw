.. _until-numcusts:

=================================================
How to Simulate For a Certain Number of Customers
=================================================

A simulation run may be terminated once a certain number of customers have passed through.
This can be done using the :code:`simulate_until_max_customers` method.
The method takes in a variable :code:`max_customers`.
There are three methods of counting customers:

 - :code:`'Finish'`: Simulates until :code:`max_customers` has reached the Exit Node.
 - :code:`'Arrive'`: Simulates until :code:`max_customers` have spawned at the Arrival Node.
 - :code:`'Accept'`: Simulates until :code:`max_customers` have been spawned and accepted (not rejected) at the Arrival Node.

The method of counting customers is specified with the optional keyword argument :code:`method`. The default value is is :code:`'Finish'`.

Consider an :ref:`M/M/1/3 <kendall-notation>` queue::

	>>> import ciw
	>>> N = ciw.create_network(
	...     arrival_distributions=[ciw.dists.Exponential(rate=10)],
	...     service_distributions=[ciw.dists.Exponential(rate=5)],
	...     number_of_servers=[1],
	...     queue_capacities=[3]
	... )

To simulate until 30 customers have finished service::

	>>> ciw.seed(1)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_customers(30, method='Finish')
	>>> len(Q.nodes[-1].all_individuals)
	30

To simulate until 30 customers have arrived::

	>>> ciw.seed(1)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_customers(30, method='Arrive')
	>>> len(Q.nodes[-1].all_individuals), len(Q.nodes[1].all_individuals), len(Q.rejection_dict[1][0])
	(13, 4, 13)

To simulate until 30 customers have been accepted::

	>>> ciw.seed(1)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_customers(30, method='Accept')
	>>> len(Q.nodes[-1].all_individuals), len(Q.nodes[1].all_individuals)
	(27, 3)