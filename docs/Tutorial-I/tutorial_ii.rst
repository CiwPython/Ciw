.. _tutorial-ii:

============================================
Tutorial II: Exploring the Simulation Object
============================================

In the previous tutorial, we defined and simulated our bank for a week::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=0.2)],
    ...     service_distributions=[ciw.dists.Exponential(rate=0.1)],
    ...     number_of_servers=[3]
    ... )
    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(1440)

Let's explore the Simulation object :code:`Q`.
Although our queueing system consisted of one node (the bank), the object :code:`Q` is made up of three, accessed using::

    >>> Q.nodes
    [Arrival Node, Node 1, Exit Node]

+ **The Arrival Node:**
  This is where customers are created. They are spawned here, and can :ref:`baulk <baulking-functions>`, :ref:`be rejected <tutorial-vi>` or sent to a service node. Accessed using::

    >>> Q.nodes[0]
    Arrival Node

+ **Service Node:**
  This is where customers queue up and receive service. This can be thought of as the bank itself. Accessed using::

    >>> Q.nodes[1]
    Node 1

+ **The Exit Node:**
  When customers leave the system, they are collected here. Then, when we wish to find out what happened during the simulation run, we can find the customers here. Accessed using::

    >>> Q.nodes[-1]
    Exit Node

Once the simulation is run, the simulation object remains in exactly the same state as it reached at the end of the simulation run.
Therefore, the simulation object itself can give some information about what went on during the run.
The :code:`Exit Node` contains all customers who had completed service in the bank, in order of when they left the system::

    >>> Q.nodes[-1].all_individuals
    [Individual 2, Individual 3, Individual 1, ..., Individual 300]

The service node will also contain customers, those who were still waiting or still receiving service at the time the simulation run ended.
During this run, there were three customers left in the bank at the end of the day::

    >>> Q.nodes[1].all_individuals
    [Individual 304, Individual 306, Individual 307]

Let's look at the first individual to finish service, :code:`Individual 2`.
Individuals carry data records, that contain information such as arrival date, waiting time, and exit date::

    >>> ind = Q.nodes[-1].all_individuals[0]
    >>> ind
    Individual 2
    >>> len(ind.data_records)
    1

    >>> ind.data_records[0].arrival_date
    7.936299...
    >>> ind.data_records[0].waiting_time
    0.0
    >>> ind.data_records[0].service_start_date
    7.936299...
    >>> ind.data_records[0].service_time
    2.944637...
    >>> ind.data_records[0].service_end_date
    10.88093...
    >>> ind.data_records[0].exit_date
    10.88093...

This isn't a very efficient way to look at results.
In the next tutorial we will look at generating lists of records to gain some summary statistics.