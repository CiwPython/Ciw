.. _process-based:

===================================
How to Define Process-Based Routing
===================================

Ciw has the capability to run simulations with process-based routing. This means a customer's entire route is determined at the start and not determined probablistically as they progress through the network.
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

    >>> inds = Q.nodes[-1].all_individuals # Get's all individuals from exit node
    >>> set([tuple(dr.node for dr in ind.data_records) for ind in inds]) # Get's all unique routes of completed individuals
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

For this we will require two routing functions: :code:`routing_function_Node_1`, :code:`routing_function_Node_2`::

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

As there are no arrivals at Node 3, no customer will need routing assigned here. However, we need to use the placeholder function :code:`ciw.no_routing` to account for this::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=1),
    ...                            ciw.dists.Deterministic(value=1),
    ...                            None],
    ...     service_distributions=[ciw.dists.Exponential(rate=2),
    ...                            ciw.dists.Exponential(rate=2),
    ...                            ciw.dists.Exponential(rate=2)],
    ...     number_of_servers=[1,1,1],
    ...     routing=ciw.routing.ProcessBased(routing_function)
    ... )