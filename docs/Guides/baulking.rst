.. _baulking-functions:

==================================
How to Simulate Baulking Customers
==================================

Ciw allows customer's to baulk (decide not join the queue) upon arrival, according to baulking functions. These functions take in a parameter :code:`n`, the number of individuals at the node, and returns a probability of baulking.

For example, say we have an M/M/1 system where customers never baulk if there are less than 3 customers in the system, probability 0.5 of baulking if there are between 3 and 6 customers in the system, and always baulk if there are more than 6 customers in the system. We can define the following baulking function::

    >>> def my_baulking_function(n):
    ...     if n < 3:
    ...         return 0.0
    ...     if n < 7:
    ...         return 0.5
    ...     return 1.0

In the parameter's dictionary we tell Ciw which node and customer class this function applies to with the :code:`Baulking_functions` key::
	
	>>> import ciw
	>>> params = {
	...     'Arrival_distributions': {'Class 0': [['Exponential', 5]]},
	...     'Service_distributions': {'Class 0': [['Exponential', 10]]},
	...     'Transition_matrices': {'Class 0': [[0.0]]},
	...     'Baulking_functions': {'Class 0': [my_baulking_function]},
	...     'Number_of_servers': [1]
	... }

When the system is simulated, the baulked customers are recorded in the Simulation object's :code:`baulked_dict`. This is a dictionary of dictionaries, with nodes and customer classes as keys, and a list of arrival dates as values::

	>>> ciw.seed(1)
	>>> N = ciw.create_network(params)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_time(45.0)
	>>> Q.baulked_dict
	{1: {0: [21.1040..., 42.2023..., 43.7558..., 43.7837..., 44.2266...]}}

Note that baulking works and behaves differently to simply setting a queue capacity. Filling a queue's capacity results in arriving customers begin *rejected* (and recorded in the :code:`rejection_dict`), and transitioning customers to be blocked. Baulking on the other hand does not effect transitioning customers, and customer who have baulked are recorded in the :code:`baulked_dict`. This means that if you set a deterministic baulking threshold of 5, but do not set a queue capacity, then the number of individuals at that node may exceed 5, due to customers transitioning from other nodes ignoring the baulking threshold.