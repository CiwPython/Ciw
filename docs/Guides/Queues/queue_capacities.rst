.. _queue-capacities:

====================================
How to Set Maximium Queue Capacities
====================================

A maximum queueing capacity can be set for each node. This means that once the number of people waiting at that node reaches the capacity, then that node cannot receive any more customers until some individuals leave the node. This affects newly arriving customers and customers transitioning from another node differently:

+ Newly arriving customers who wish to enter the node once capacity is reached are *rejected*. They instead leave the system immediately, and have a data record written that records this rejection (:ref:`see below<rejection-records>`).
+ Customers wishing to transition to the node after finishing service at another node are blocked (:ref:`see below<blocking-mechanism>`). This means thet remain at their original node, with a server whi is unable to begin another customer's service, until space becomes available.

In order to implement this, we use the :code:`queue_capacities` keyworks when creating the network::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=2),
    ...                            ciw.dists.Exponential(rate=1)],
    ...     service_distributions=[ciw.dists.Exponential(rate=1),
    ...                            ciw.dists.Exponential(rate=1)],
    ...     routing=[[0.0, 0.5],
    ...              [0.0, 0.0]],
    ...     number_of_servers=[3, 2],
    ...     queue_capacities=[float('inf'), 10]
    ... )

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100)

In the example above, the second node has 2 servers and a queueing capacity of 10, and so once there are 12 customers present, it will not accept any more customers. In the first node, there is infinite queueing capacity, and so no blocking or rejection will occur here.

If the :code:`queue_capacities` keyword is omitted, then infinite capacities are assumed, that is an uncapacitated system.

.. _rejection-records:

Rejection Records
~~~~~~~~~~~~~~~~~

Any customer that is rejected and leaves the system will be recorded by producing a data record of the rejection. This will look like this::

    >>> recs = Q.get_all_records(only=['rejection'])
    >>> dr = recs[0]
    >>> dr
    Record(id_number=283, customer_class='Customer', original_customer_class='Customer', node=2, arrival_date=86.79600309018552, waiting_time=nan, service_start_date=nan, service_time=nan, service_end_date=nan, time_blocked=nan, exit_date=86.79600309018552, destination=nan, queue_size_at_arrival=12, queue_size_at_departure=nan, server_id=nan, record_type='rejection')

These records will have field :code:`record_type` as the string :code:`'rejection'`; will have information about the customer such as their ID number, and customer class; will have the :code:`node` they were rejected from; they will have equal :code:`arrival_date` and :code:`exit_date` representing the date they arrived and got rejected; and they will have a `queue_size_at_arrival` showing the number of people at the queue when they got rejected. All other fields will have :code:`nan` values.


.. _blocking-mechanism:

Blocking Mechanism
~~~~~~~~~~~~~~~~~~

In Ciw, Type I blocking (blocking after service) is implemented for restricted networks.

After service, a customer's next destination is sampled from the transition matrix.
If there is space at the destination node, that customer will join the queue there.
Else if the destination node's queueing capacity is full, then that customer will be blocked.
That customer remains at that node, with its server, until space becomes available at the destination.
This means the server that was serving that customer remains attached to that customer, being unable to serve anyone else until that customer is unblocked.

At the time of blockage, information about this customer is added to the destination node's :code:`blocked_queue`, a virtual queue containing information about all the customers blocked to that node, and *the order in which they became blocked*. Therefore, when space becomes available, the customer to be unblocked will be the customer who was blocked first. That is, the sequence of unblockages happen in the order which customers were blocked.

Circular blockages can lead to :ref:`deadlock <detect-deadlock>`.

Information about blockages are visible in the service data records::

    >>> recs = Q.get_all_records(only=['service'])
    >>> dr = recs[381]
    >>> dr
    Record(id_number=281, customer_class='Customer', original_customer_class='Customer', node=1, arrival_date=86.47159..., waiting_time=0.23440..., service_start_date=86.70600..., service_time=0.60807..., service_end_date=87.31407..., time_blocked=0.75070..., exit_date=88.06478..., destination=2, queue_size_at_arrival=4, queue_size_at_departure=2, server_id=3, record_type='service')

In the case above, the customer ended service at date :code:`87.31407...`, but didn't exit until date :code:`88.06478...`, giving a :code:`time_blocked` of :code:`0.75070...`.

