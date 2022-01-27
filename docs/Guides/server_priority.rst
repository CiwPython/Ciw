.. _server-priority:

============================
How to Set Server Priorities
============================

When there is more than one free server at a node, there is a choice of which server an individual should begin their service with. By default this selection is prioritised by the arbitrary server ID number. However this can lead to an uneven workload balance amongst servers at the same node. Ciw does allow custom priorities to be set with the :code:`server_priority_functions` keyword.

For example, consider an :ref:`M/M/3 <kendall-notation>` system.
By default, whenever a new individual arrives they would be allocated to:

+ server 1, if server 1 is not busy;
+ server 2, if server 2 is not busy and server 1 is busy;
+ server 3, if server 3 is not busy and server 1 and 2 are busy.

Observing the utilisation of each server we can see that server 1 is far more busy than server 2 and server 3::
    
    >>> import ciw
    >>> N = ciw.create_network(
    ...      arrival_distributions=[ciw.dists.Exponential(rate=1)],
    ...      service_distributions=[ciw.dists.Exponential(rate=2)],
    ...      number_of_servers=[3]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(1000)

    >>> [srv.utilisation for srv in Q.nodes[1].servers]
    [0.3184942440259139, 0.1437617661984246, 0.04196395909329539]


Ciw allows servers to be prioritised according to a custom server priority function. 
We can define a custom server priority function that returns the cumulative amount of time a server was busy::

    >>> def server_busy_time(server, ind):
    ...     return server.busy_time

Using this as a server priority function will priorities servers by their cumulative busy time. Note that custom server priority functions must have this structure, they must take both the :code:`server` and the current individual :code:`ind`, and must return a value that will be prioritised by sorting this in ascending order. In this case the server with the least amount of cumulative busy time will be prioritised first.

The :code:`server_priority_functions` keyword takes a list of server priority functions to use at each node of the network. Now we can see than the server utilisations are more even::

    >>> N = ciw.create_network(
    ...      arrival_distributions=[ciw.dists.Exponential(rate=1)],
    ...      service_distributions=[ciw.dists.Exponential(rate=2)],
    ...      number_of_servers=[3],
    ...      server_priority_functions=[server_busy_time]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(1000)

    >>> [srv.utilisation for srv in Q.nodes[1].servers]
    [0.16784616228588892, 0.16882711899030475, 0.1675466880414403]



Prioritising Using the Individual
---------------------------------

It is also possible to use the individual to be served as a way to determine the priority of the servers. 
For example, consider the case where we have two classes of individuals and we want to assign each individual to a server based on their class:

+ for individuals of class 0, prioritise server 1, then 3, then 2;
+ for individuals of class 1, prioritise server 2, then 3, then 1.

The server priority function for this example would be::

    >>> def custom_server_priority(srv, ind):
    ...     if ind.customer_class == 0:
    ...         priorities = {1: 0, 2: 2, 3: 1}
    ...         return priorities[srv.id_number]
    ...     if ind.customer_class == 1:
    ...         priorities = {1: 2, 2: 0, 3: 1}
    ...         return priorities[srv.id_number]


Now let's see this in action when we have equal numbers of individuals of class 0 and of class 1::

    >>> N = ciw.create_network(
    ...     arrival_distributions={
    ...         'Class 0': [ciw.dists.Exponential(1)],
    ...         'Class 1': [ciw.dists.Exponential(1)]
    ...     },
    ...     service_distributions={
    ...         'Class 0': [ciw.dists.Exponential(2)],
    ...         'Class 1': [ciw.dists.Exponential(2)]
    ...     },
    ...     number_of_servers=[3],
    ...     server_priority_functions=[custom_server_priority]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(1000)
    >>> [srv.utilisation for srv in Q.nodes[1].servers]
    [0.36132860028585134, 0.3667939476202799, 0.2580202674603771]

Utilisation is fairly even between the first two servers, with the third server picking up any slack. Now let's see what happens when there is three times as many individuals of class 0 entering the system as there are of class 1::

    >>> N = ciw.create_network(
    ...     arrival_distributions={
    ...         'Class 0': [ciw.dists.Exponential(1.5)],
    ...         'Class 1': [ciw.dists.Exponential(0.5)]
    ...     },
    ...     service_distributions={
    ...         'Class 0': [ciw.dists.Exponential(2)],
    ...         'Class 1': [ciw.dists.Exponential(2)]
    ...     },
    ...     number_of_servers=[3],
    ...     server_priority_functions=[custom_server_priority]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(1000)
    >>> [srv.utilisation for srv in Q.nodes[1].servers]
    [0.447650059165907, 0.2678754897968868, 0.29112382084389343]

Now the first server is much busier than the others.


Important Notice
----------------

Currently when using :ref:`server schedules <server-schedule>` and server priority functions the priorities do not take effect immediately after a shift change, as *all* servers are replaced.
