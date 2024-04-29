.. _custom-routing:

====================================
How to Define Custom Logical Routing
====================================

In the guide on :ref:`routing objects<routing-objects>` we saw that node routing objects determine the where customers are routed to the next node. Custom routing objects can be created and used in Ciw, in order to define any logical routing that we wish.

In order to define a routing object, they must inherit from Ciw'r :code:`ciw/routing.NodeRouting` object. We then need to define the :code:`next_node` method, that takes in the individual to route, and returns a node of the network that is that individual's next destination. If required, we can also re-write the object's :code:`__init__` method. Note that we will have access to some useful attributes:

    + :code:`self.simulation`: the simulation object itself, with access to its nodes, and the current time.
    + :code:`self.node`: the node associated with this routing object.

As an example, the built-in :code:`ciw.routing.Direct` router would look like this::

    >>> import ciw
    >>> class Direct(ciw.routing.NodeRouting):
    ...     """
    ...     A router that sends the individual directly to another node.
    ...     """
    ...     def __init__(self, to):
    ...         """
    ...         Initialises the routing object.
    ... 
    ...         Takes:
    ...             - to: a the node index to send to.
    ...         """
    ...         self.to = to
    ... 
    ...     def next_node(self, ind):
    ...         """
    ...         Chooses the node 'to' with probability 1.
    ...         """
    ...         return self.simulation.nodes[self.to]


Example
-------

Imagine we have a four node network. Nodes 2, 3, and 4 all route customers out of the system. Node 1 however has some logical routing - before time 50 it will route to node 2 if it is empty, and node 3 otherwise; after time 50 it always routes to node 4. This is defined by::
    
    >>> class CustomRouting(ciw.routing.NodeRouting):
    ...     def next_node(self, ind):
    ...         """
    ...         Chooses node 2 if it is empty and it is before date 50,
    ...         Chooses node 3 if node 2 is not empty and it is before date 50
    ...         Chooses node 4 is the date is after 50.
    ...         """
    ...         if self.node.now >= 50:
    ...             return self.simulation.nodes[4]
    ...         if self.simulation.nodes[2].number_of_individuals == 0:
    ...             return self.simulation.nodes[2]
    ...         return self.simulation.nodes[3]

Now if the only arrivals are to node 1, and we run this for 100 time units, we should observe that: services at node 2 had no waiting time; services at node 4 occurred after date 50; services at nodes 2 and 3 occurred before date 50::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[
    ...         ciw.dists.Exponential(rate=1),
    ...         None,
    ...         None,
    ...         None
    ...     ],
    ...     service_distributions=[
    ...         ciw.dists.Deterministic(value=0.2),
    ...         ciw.dists.Deterministic(value=0.2),
    ...         ciw.dists.Deterministic(value=0.2),
    ...         ciw.dists.Deterministic(value=0.2)
    ...     ],
    ...     number_of_servers=[3, 1, 1, 1],
    ...     routing=ciw.routing.NetworkRouting(
    ...         routers=[
    ...             CustomRouting(),
    ...             ciw.routing.Leave(),
    ...             ciw.routing.Leave(),
    ...             ciw.routing.Leave()
    ...         ]
    ...     )
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100)
    >>> recs = Q.get_all_records()

    >>> all(r.service_start_date >= 50 for r in recs if r.node == 4)
    True
    >>> all(r.service_start_date <= 50 for r in recs if r.node in [2, 3])
    True
    >>> all(r.queue_size_at_arrival == 0 for r in recs if r.node == 2)
    True



.. _custom-rerouting:

Custom Pre-emptive Re-routing
-----------------------------

Custom routing objects can be used to use different routing logic for when a customer finishes service, to when a customer has a service interrupted and must be re-routed. In order to do this, we need to create a custom routing object, and re-write the :code:`next_node_for_rerouting` method, which is called when deciding which node the customer will be re-routed to after pre-emption. By default, this calls the object's :code:`next_node` method, and so identical logic occurs. But we can rewrite this to use different logic when rerouting customers.

Consider, for example, a two node system where customers always arrive to Node 1, and immediately leave the system. However, if they have service interrupted at Node 1, they are re-routed to Node 2::

    >>> class CustomRerouting(ciw.routing.NodeRouting):
    ...     def next_node(self, ind):
    ...         """
    ...         Always leaves the system.
    ...         """
    ...         return self.simulation.nodes[-1]
    ... 
    ...     def next_node_for_rerouting(self, ind):
    ...         """
    ...         Always sends to Node 2.
    ...         """
    ...         return self.simulation.nodes[2]


**Note that re-routing customers ignores queue capacities.** That means that interrupted customers can be re-routed to nodes that already have full queues, nodes that would otherwise reject or block other arriving individuals; and so that node would be temporarily over-capacity.
