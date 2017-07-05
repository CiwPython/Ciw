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

To tell Ciw to use this schedule for a given node, in the :code:`Number_of_servers` keyword we replace an integer with the schedule::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     Arrival_distributions=[['Exponential', 5]],
    ...     Service_distributions=[['Exponential', 10]],
    ...     Number_of_servers=[[[2, 10], [0, 30], [1, 100]]]
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

When a server is due to go off duty during a customer's service, there are two options of what may happen.

+ During a pre-emptive schedule, that server will immediately stop service and leave. Whenever more servers come on duty, they will prioritise the interrupted customers and continue their service. However those customers' service times are re-sampled.

+ During a non-pre-emptive schedule, customers cannot be interrupted. Therefore servers finish the current customer's service before disappearing. This of course may mean that when new servers arrive the old servers are still there.

In order to implement pre-emptive or non-pre-emptive schedules, put the schedule in a tuple with a :code:`True` or a :code:`False` as the second term, indicating pre-emptive or non-pre-emptive interruptions. For example::

    Number_of_servers=[([[2, 10], [0, 30], [1, 100]], True)] # preemptive

And::

    Number_of_servers=[([[2, 10], [0, 30], [1, 100]], False)] # non-preemptive

Ciw defaults to non-pre-emptive schedules, and so the following code implies a non-pre-emptive schedule::

    Number_of_servers=[[[2, 10], [0, 30], [1, 100]]] # non-preemptive



Overtime
--------

Non-preemptive schedules allow for the possibility of overtime, that is servers working after their shift has ended in order to complete a customer's service.
The amount of overtime each server works is recorded in the Node object's :code:`overtime` attribute.
Consider the following example::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     Arrival_distributions=[['Deterministic', 3.0]],
    ...     Service_distributions=[['Deterministic', 5.0]],
    ...     Number_of_servers=[[[1, 4.0], [2, 10.0], [0, 100.0]]]
    ... )
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(20.0)

    >>> Q.transitive_nodes[0].overtime
    [4.0, 1.0, 4.0]

Here we see that the first server that went off duty worked 4.0 time units of overtime, the second worked 1.0 time unit of overtime, and the third worked 4.0 time units of overtime.
