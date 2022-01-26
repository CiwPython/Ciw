.. _server-priority:

===================================
How to set a custom server priority
===================================

In Ciw, the default behaviour for choosing which server gets allocated to a new individual, is determined by the server id. 
For example, say we have an :ref:`M/M/3 <kendall-notation>` system.
Whenever a new individual arrives they would be allocated to:

+ server 1, if server 1 is not busy
+ server 2, if server 2 is not busy and server 1 is busy
+ server 3, if server 3 is not busy and server 1 and 2 are busy

If we observe the utilisation of each server we can see that server 1 is far more busy than server 2 and server 3::
	
	>>> import ciw
	>>> N = ciw.create_network(
	...      arrival_distributions={'Class 0': [ciw.dists.Exponential(rate=1)]},
	...      service_distributions={'Class 0': [ciw.dists.Exponential(rate=2)]},
	...      number_of_servers=[3]
	... )
	>>> ciw.seed(0)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_time(1000)
	>>> [srv.busy_time for srv in Q.nodes[1].servers]
	[318.49424402591393, 143.7617661984246, 41.96395909329539]


However, Ciw allows servers to be prioritised according to a custom server priority function. 
We can define a custom server priority function that returns the amount of time a server was busy::

	>>> def server_busy_time(server, ind):
	... 	return server.busy_time

We can now input :code:`server_busy_time` into our simulation which will then use the busy time of each server to determine the server to allocate to a new individual. 
For every individual that needs to be assigned a server, the servers will be sorted based on their busy time::

	>>> import ciw	
	>>> N = ciw.create_network(
	...      arrival_distributions=[ciw.dists.Exponential(rate=1)],
	...      service_distributions=[ciw.dists.Exponential(rate=2)],
	...      number_of_servers=[3],
	...      server_priority_functions=[server_busy_time]
	... )
	>>> ciw.seed(0)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_time(1000)
	>>> [srv.busy_time for srv in Q.nodes[1].servers]
	[167.8461622858889, 168.82711899030474, 167.5466880414403]


Important Notice
----------------

Note here that, when using shifts together with :code:`service_priority_functions`, the function does not take effect immediately after a shift change. 
If a shift change occurs, the function will be called again when the next individual is assigned to a server.

Further example
---------------

Another thing we can do, is use the individual to be served as a way to determine the priority of the servers. 
For example, consider the case where we have 2 classes of individuals and we want to assign each individual to a server based on their class:

+ Assign class 0 individuals to server 1 if not busy, otherwise the least busy server
+ Assign class 1 individuals to server 2 if not busy, otherwise the least busy server

The server priority function for this example would be::
	>>> def custom_server_priority(srv, ind):
	...     if srv.id_number == ind.customer_class + 1:
	...         return -1
	...     return srv.busy_time

Note that where we :code:`return -1`, we could have used any negative number instead, to indicate that the server should be prioritised.
Thus we can input :code:`custom_server_priority` into our simulation which will then use both the individual's :code:`customer_class` and the server's :code:`busy_time` to determine which server to allocate the new individual to:
	>>> N = ciw.create_network(
	...     arrival_distributions={
	...			'Class 0': [ciw.dists.Exponential(0.5)], 
	...			'Class 1': [ciw.dists.Exponential(1)]
	...		},
	...     service_distributions={
	... 		'Class 0': [ciw.dists.Exponential(2)], 
	...			'Class 1': [ciw.dists.Exponential(2)]
	...		},
	...     number_of_servers=[3],
	...     server_priority_functions=[custom_server_priority]
	... )
	>>> ciw.seed(0)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_time(1000)
	>>> [srv.busy_time for srv in Q.nodes[1].servers]
	[244.71115151795217, 354.00422589394697, 171.83474391542848]
