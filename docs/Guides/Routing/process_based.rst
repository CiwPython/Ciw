.. _process-based:

===================================
How to Define Process-Based Routing
===================================

Ciw has the capability to run simulations with process-based routing. This means a customer's entire route is determined at the start and not determined probabilistically as they progress through the network.
This allows routes to account for an individuals history, for example, repeating nodes a certain number of times.

A customer's entire route is determined at the start, generated from a routing function, that takes in an individual and returns a route, which is a list containing the order of the nodes they are to visit. The function should also take in the simulation itself, allowing time and state-dependent routing. For example::

    >>> def routing_function(ind, simulation):
    ...     return [2, 2, 1]

This takes in an individual and assigns it the route [2, 2, 1]. Whichever node this individual arrives to (determined by the arrival distributions), after service there they are sent to Node 2, then back Node 2, then back to Node 1, before exiting the system. Ensuring the exact repetition of these nodes would not be possible in a purely probabilistic system. 

In order to utilise this, we use a :code:`ProcessBased` routing object, that takes in this routing function. For example::

    >>> import ciw
    
    >>> def repeating_route(ind, simulation):
    ...     return [1, 1]

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=1)],
    ...     service_distributions=[ciw.dists.Exponential(rate=2)],
    ...     number_of_servers=[1], 
    ...     routing=ciw.routing.ProcessBased(repeating_route)
    ... )

Here, customers arrive at Node 1, and have service there and then repeat this two more times before exiting the system. 

Let's run this and look at the routes of those that have left the system. 

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100.0)

    >>> inds = Q.nodes[-1].all_individuals # Gets all individuals from exit node
    >>> set([tuple(dr.node for dr in ind.data_records) for ind in inds]) # Gets all unique routes of completed individuals
    {(1, 1, 1)}

Now we can see that all individuals who have left the system, that is they have completed their route, repeated service at Node 1 three times. 


Further example
---------------

The routing functions can be as complicated as necessary. They take in an individual, and therefore can take in any attribute of an individual when determining the route (including their :code:`customer_class`).

Lets make a network with three nodes with the following routes:

+ For customers arriving at Node 1:
  + if individual has an even :code:`id_number`, repeat Node 1 twice, then exit.
  + otherwise route from Node 1 to Node 2, to Node 3, and then exit.
+ Arrivals at Node 2:
  + have 50% chance of routing to Node 3, and then exit.
  + have 50% chance of routing to Node 1, and then exit.
+ There are no arrivals at Node 3.

For this we will require a routing function that returns different things depending on the individual's starting node::

    >>> import random
    >>> def routing_function(ind, simulation):
    ...     if ind.starting_node == 1:
    ...         if ind.id_number % 2 == 0:
    ...             return [1, 1, 1]
    ...         return [1, 2, 3]
    ...     if ind.starting_node == 2:
    ...         if random.random() <= 0.5:
    ...             return [2, 3]
    ...         return [2, 1]

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=1),
    ...                            ciw.dists.Deterministic(value=1),
    ...                            None],
    ...     service_distributions=[ciw.dists.Exponential(rate=2),
    ...                            ciw.dists.Exponential(rate=2),
    ...                            ciw.dists.Exponential(rate=2)],
    ...     number_of_servers=[1, 1, 1],
    ...     routing=ciw.routing.ProcessBased(routing_function)
    ... )



Flexible Process Based Routing
------------------------------

In the examples above, once a route was sampled, the customer's entire journey was set out before them. However, with a :code:`FlexibleProcessBased` object, we can define sequences of sets of nodes that must be visited in order. Within a set of nodes, either the individual must visit at least one node here, or must visit all nodes here, but the order is irrelevant. This is defined with the :code:`rule` keyword.

Consider for example the following sequence of sets of destinations::

    [[1, 2, 3], [4], [5, 6]]

There are three sets of nodes in the sequence, the set :code:`[1, 2, 3]`, followed by the set :code:`[4]`, followed by the set :code:`[5, 6]`. Routes are then determined by the :code:`rule` keyword:

+ :code:`rule='any'`: this means that at just one node from each set should be visited, in the order of the sets. The choice of which node is chosen from each set is set with the :code:`choice` keyword. Valid routes include (1, 4, 5), (2, 4, 5), and (3, 4, 6), amongst others.
+ :code:`rule='all'`: this means that every node in a set must be visited before moving on to the next set. The order at which a node is visited in a set is set with the :code:`choice` keyword. Valid routes include (1, 2, 3, 4, 5, 6), (3, 2, 1, 4, 6, 5), and (3, 1, 2, 4, 5, 6), amongst others.

The current options for choices are:
 - :code:`'random'`: randomly chooses a node from the set.
 - :code:`'jsq'`: chooses the node with the smallest queue from the set (like the :ref:`join-shortest-queue<jsq>` router).
 - :code:`'lb'`: chooses the node with the least number of customers present from the set (like the :ref:`load-balancing<load_balancing>` router).

When all nodes in a set must be visited, these rules apply to choosing the next node from the set minus the nodes already visited, applied at the current time when the choice is made.

Example::

    >>> def routing_function(ind, simulation):
    ...     return [[1, 2], [3], [1, 2]]

A route where the first and third sets include nodes 1 and 2, and the second set only includes node 3. All customers arrive to node 4. Let's compare the :code:`'any'` and :code:`'all'` rules. First with :code:`'any'`::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[
    ...         None,
    ...         None,
    ...         None,
    ...         ciw.dists.Exponential(rate=1)
    ...     ],
    ...     service_distributions=[
    ...         ciw.dists.Exponential(rate=2),
    ...         ciw.dists.Exponential(rate=2),
    ...         ciw.dists.Exponential(rate=2),
    ...         ciw.dists.Exponential(rate=2),
    ...     ],
    ...     number_of_servers=[1, 1, 1, 1],
    ...     routing=ciw.routing.FlexibleProcessBased(
    ...         route_function=routing_function,
    ...         rule='any',
    ...         choice='random'
    ...     )
    ... )
    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_customers(6)
    >>> routes = [[dr.node for dr in ind.data_records] for ind in Q.nodes[-1].all_individuals]
    >>> for route in routes:
    ...     print(route)
    [4, 2, 3, 2]
    [4, 1, 3, 1]
    [4, 1, 3, 1]
    [4, 1, 3, 1]
    [4, 2, 3, 1]
    [4, 2, 3, 1]

We see that all customers that completed their journey arrived at node 4, took either node 1 or 2 first, then node 3, then either node 1 or 2.

Now compare with :code:`'all'`::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[
    ...         None,
    ...         None,
    ...         None,
    ...         ciw.dists.Exponential(rate=1)
    ...     ],
    ...     service_distributions=[
    ...         ciw.dists.Exponential(rate=2),
    ...         ciw.dists.Exponential(rate=2),
    ...         ciw.dists.Exponential(rate=2),
    ...         ciw.dists.Exponential(rate=2),
    ...     ],
    ...     number_of_servers=[1, 1, 1, 1],
    ...     routing=ciw.routing.FlexibleProcessBased(
    ...         route_function=routing_function,
    ...         rule='all',
    ...         choice='random'
    ...     )
    ... )
    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_customers(6)
    >>> routes = [[dr.node for dr in ind.data_records] for ind in Q.nodes[-1].all_individuals]
    >>> for route in routes:
    ...     print(route)
    [4, 2, 1, 3, 2, 1]
    [4, 1, 2, 3, 2, 1]
    [4, 2, 1, 3, 2, 1]
    [4, 1, 2, 3, 2, 1]
    [4, 1, 2, 3, 1, 2]
    [4, 1, 2, 3, 2, 1]

We see that all customers that completed their journey arrived at node 4, took both node 1 or 2 in either order, then node 3, then both node 1 or 2 in either order.

