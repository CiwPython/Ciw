.. _behaviour-nodes:

================================
How to Get More Custom Behaviour
================================

Custom behaviour can be obtained by writing new :code:`Node` and :code:`ArrivalNode` classes, that inherit from the original :code:`ciw.Node` and :code:`ciw.ArrivalNode` classes, that introduce new beahviour into the system.
The classes that can be overwitten are:

- :code:`Node`: the main node class used to represent a service centre.
- :code:`ArrivalNode`: the node class used to generate individuals and route them to a specific :code:`Node`.

These new Node and Arrival Node classes can be used with the Simulation class by using the keyword arugments :code:`node_class` and :code:`arrival_node_class`.

Consider the following two node network, where arrivals only occur at the first node, and there is a queueing capacity of 10.
The second node is redundent in this scenario::

	>>> import ciw
	>>> from collections import Counter

	>>> N = ciw.create_network(
	...     Arrival_distributions=[['Exponential', 6.0], 'NoArrivals'],
	...     Service_distributions=[['Exponential', 5.0], ['Exponential', 5.0]],
	...     Transition_matrices=[[0.0, 0.0], [0.0, 0.0]],
	...     Number_of_servers=[1, 1],
	...     Queue_capacities=[10, 'Inf']
	... )

Now we run the system for 100 time units, and see that we get 484 services at the first node, and none at the second node::

	>>> ciw.seed(1)
	>>> Q = ciw.Simulation(N)
	>>> Q.simulate_until_max_time(100)

	>>> service_nodes = [r.node for r in Q.get_all_records()]
	>>> Counter(service_nodes)
	Counter({1: 484})

We will now create a new :code:`CustomArrivalNode` such that any customers who arrive when the first node has 10 or more customers present will be sent to the second node.
First create the :code:`CustomArrivalNode` that inherits from :code:`ciw.ArrivalNode`, and overwrites the :code:`send_individual` method::

	>>> class CustomArrivalNode(ciw.ArrivalNode):
	...     def send_individual(self, next_node, next_individual):
	...         """
	...         Sends the next_individual to the next_node
	...         """
	...         self.number_accepted_individuals += 1
	...         if len(next_node.all_individuals) <= 10:
	...             next_node.accept(next_individual, self.next_event_date)
	...         else:
	...             self.simulation.nodes[2].accept(next_individual, self.next_event_date)

To run the same system, we need to remove the keyword :code:`'Queue_capacities'` when creating a network, so that customers are not rejected before reaching the :code:`send_individual` method::

	>>> N = ciw.create_network(
	...     Arrival_distributions=[['Exponential', 6.0], 'NoArrivals'],
	...     Service_distributions=[['Exponential', 5.0], ['Exponential', 5.0]],
	...     Transition_matrices=[[0.0, 0.0], [0.0, 0.0]],
	...     Number_of_servers=[1, 1]
	... )

Now rerun the same system, telling Ciw to use the new :code:`arrival_node_class` to use.
We'll see that the same amount of services take place at Node 1, however rejected customers now have services taking place at Node 2::

	>>> ciw.seed(1)
	>>> Q = ciw.Simulation(N, arrival_node_class=CustomArrivalNode)
	>>> Q.simulate_until_max_time(100)

	>>> service_nodes = [r.node for r in Q.get_all_records()]
	>>> Counter(service_nodes)
	Counter({1: 484, 2: 85})
