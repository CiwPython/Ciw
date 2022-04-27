.. _baulking-functions:

==================================
How to Simulate Baulking Customers
==================================

Ciw allows customers to baulk (decide not join the queue) upon arrival, according to baulking functions.
These functions take in a parameter :code:`n`, the number of individuals at the node, and returns a probability of baulking.

For example, say we have an :ref:`M/M/1 <kendall-notation>` system where customers:

+ Never baulk if there are less than 3 customers in the system
+ Have probability 0.5 of baulking if there are between 3 and 6 customers in the system
+ Always baulk if there are more than 6 customers in the system

We can define the following baulking function::

    >>> def probability_of_baulking(n):
    ...     if n < 3:
    ...         return 0.0
    ...     if n < 7:
    ...         return 0.5
    ...     return 1.0

When creating the Network object we tell Ciw which node and customer class this function applies to with the :code:`baulking_functions` keyword::
	
	>>> import ciw
	>>> N = ciw.create_network(
	...      arrival_distributions={'Class 0': [ciw.dists.Exponential(rate=5)]},
	...      service_distributions={'Class 0': [ciw.dists.Exponential(rate=10)]},
	...      baulking_functions={'Class 0': [probability_of_baulking]},
	...      number_of_servers=[1]
	... )

When the system is simulated, the baulked customers are recorded in the Simulation object's :code:`baulked_dict`.
This is a dictionary, that maps node numbers to dictionaries.
These dictionaries map customer class numbers to a list of dates at which customers baulked::

	>>> ciw.seed(0)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_time(45.0)
	>>> Q.baulked_dict
	{1: {0: [9.4589..., 12.8633..., 16.3374..., 18.7384..., 37.8363..., 38.2962...]}}

Note that baulking works and behaves differently to simply setting a queue capacity.
Filling a queue's capacity results in arriving customers being *rejected* (and recorded in the :code:`rejection_dict`), and transitioning customers to be blocked.
Baulking on the other hand does not effect transitioning customers, and customer who have baulked are recorded in the :code:`baulked_dict`.
This means that if you set a deterministic baulking threshold of 5, but do not set a queue capacity, then the number of individuals at that node may exceed 5, due to customers transitioning from other nodes ignoring the baulking threshold.
This also means you can use baulking and limited capacities in conjunction with one another.