.. _server-schedule:

===========================
How to Set Server Schedules
===========================

Ciw allows users to assign cyclic work schedules to servers at each service centre.
An example cyclic work schedule is shown in the table below:

    +-------------------+---------+--------+--------+
    |    Shift Times    |    0-10 |  10-30 | 30-100 |
    +-------------------+---------+--------+--------+
    | Number of Servers |       2 |      0 |      1 |
    +-------------------+---------+--------+--------+

This schedule is cyclic, therefore after the last shift (30-100), schedule begins again with the shift (0-10).
The cycle length for this schedule is 100.
This is defines by a list of lists indicating the number of servers that should be on duty during that shift, and the end date of that shift::

    [[2, 10], [0, 30], [1, 100]]

Here we are saying that there will be 2 servers scheduled between times 0 and 10, 0 between 10 and 30, etc.
This fully defines the cyclic work schedule.

To tell Ciw to use this schedule for a given node, in the :code:`number_of_servers` keyword we replace an integer with the schedule::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=5)],
    ...     service_distributions=[ciw.dists.Exponential(rate=10)],
    ...     number_of_servers=[[[2, 10], [0, 30], [1, 100]]]
    ... )

Simulating this system, we'll see that no services begin between dates 10 and 30, nor between dates 110 and 130::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(205.0)
    >>> recs = Q.get_all_records()
    
    >>> [r for r in recs if 10 < r.service_start_date < 30]
    []
    >>> [r for r in recs if 110 < r.service_start_date < 130]
    []

**Note that currently server schedules are incompatible with infinite servers**, and so a schedule cannot include infinite servers.



Pre-emption
-----------

There are a number of options that can be used to pre-emptively interrupt customers when servers go off duty. See the following page:

+ :ref:`Pre-emption options <preemption>`.

.. toctree::
   :maxdepth: 1
   :hidden:

   preemption.rst


Overtime
--------

Non-preemptive schedules allow for the possibility of overtime, that is servers working after their shift has ended in order to complete a customer's service.
The amount of overtime each server works is recorded in the Node object's :code:`overtime` attribute.
Consider the following example::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Deterministic(value=3.0)],
    ...     service_distributions=[ciw.dists.Deterministic(value=5.0)],
    ...     number_of_servers=[[[1, 4.0], [2, 10.0], [0, 100.0]]]
    ... )
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(20.0)

    >>> Q.transitive_nodes[0].overtime
    [4.0, 1.0, 4.0]

Here we see that the first server that went off duty worked 4.0 time units of overtime, the second worked 1.0 time unit of overtime, and the third worked 4.0 time units of overtime.
