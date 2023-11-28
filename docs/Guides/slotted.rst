.. _slotted-services:

===========================
How to Set Slotted Services
===========================

Slotted services are a schedule services that happen at specific times, and specific times only. They differ from server schedules, as between the defined 'slots', no services can begin.

They are defined similarly to server schedules. Consider the slotted schedule below:

    +----------------+------+------+------+
    |   Slot Times   |  1.5 |  2.3 |  2.8 |
    +----------------+------+------+------+
    |   Slot Sizes   |    2 |    5 |    3 |
    +----------------+------+------+------+

Here 2 customers can be served at time 1.5, 5 can be served at time 2.3, and 3 can be served at time 3. Between these times no services can occur. If customers arrive between two slots, they wait for the next slot. Like server schedules, these repeat, e.g.:

    +----------------+------+------+------+------+------+------+------+------+
    |   Slot Times   |  1.5 |  2.3 |  2.8 |  4.3 |  5.1 |  5.6 |  7.1 |  ... |
    +----------------+------+------+------+------+------+------+------+------+
    |   Slot Sizes   |    2 |    5 |    3 |    2 |    5 |    3 |    2 |  ... |
    +----------------+------+------+------+------+------+------+------+------+

In Ciw, they are defined with a :code:`ciw.Slotted` object, like so::


    ciw.Slotted(slots=[1.5, 2.3, 2.8], slot_sizes=[2, 5, 3])

To tell Ciw to use this slotted schedule for a given node, in the :code:`number_of_servers` keyword we replace an integer with the schedule::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=5)],
    ...     service_distributions=[ciw.dists.Deterministic(value=0.2)],
    ...     number_of_servers=[ciw.Slotted(slots=[1.5, 2.3, 2.8], slot_sizes=[2, 5, 3])]
    ... )

Simulating this system, we'll see that services only begin between during the slots::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(7)
    >>> recs = Q.get_all_records()
    
    >>> set([r.service_start_date for r in recs])
    {1.5, 2.3, 2.8, 4.3, 5.1, 5.6}
