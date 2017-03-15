.. _server-schedule:

===========================
How to Set Server Schedules
===========================

Ciw allows users to assign cyclic work schedules to servers at each service centre. An example cyclic work schedule is hown in the table below:

    +-------------------+---------+--------+--------+
    |    Shift Times    |    0-10 |  10-30 | 30-100 |
    +-------------------+---------+--------+--------+
    | Number of Servers |       2 |      0 |      1 |
    +-------------------+---------+--------+--------+

This schedule is cyclic, therefore after the last shift (30-100), schedule begins again with the shift (0-10). The cycle length for this schedule is 100. Let's call this schedule :code:`my_special_schedule_01`. This is defines by a list of lists indicating the end date of that shift, and the number of servers that should be on duty during that shift::

    [[10, 2], [30, 0], [100, 1]]

Here we are saying that there will be 2 servers scheduled between times 0 and 10, 0 between 10 and 30, etc. This fully defines the cyclic work schedule.

To tell Ciw to use this schedule for a given node, in the :code:`Number_of_servers` part of the parameters dictionary replace an integer with the schedule name. Also to include in the parameters dictionary is the schedule itself::

    >>> import ciw
    >>> params = {
    ...     'Arrival_distributions': [['Exponential', 5]],
    ...     'Service_distributions': [['Exponential', 10]],
    ...     'Transition_matrices': [[0.0]],
    ...     'Number_of_servers': ['my_special_schedule'],
    ...     'my_special_schedule': [[10, 2], [30, 0], [100, 1]]
    ... }

Simulating this system, we'll see that no services begin between dates 10 and 30, nor between dates 110 and 130::

    >>> ciw.seed(1)
    >>> N = ciw.create_network(params)
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

When a server is due to go off duty during a customer's service, there are two option of what may happen.

+ During a pre-emptive schedule, that server will immediately stop service and leave. Whenever more servers come on duty, they will prioritise the interrupted customers and continue their service. However those customers' service times are re-sampled. Therefore, a customer beginning service at time 5 who is meant to have a service time of 4, should finish service at time 9. However the server goes off duty at time 7. Another server restarts this customer's service at time 10, and re-samples the service time, this time service should last for 8 time units. Therefore the customer will finish service at time 18. In the records, this will be recorded as a total service time of 13, as service began at 5 and finished at 18.

+ During a non-pre-emptive schedule, customers cannot be interrupted. Therefore servers finish the current customer's service before disappearing. This of course may mean that when new servers arrive the old servers are still there, finishing up their original customers, resulting in a brief time where there are more servers on duty that was scheduled.

In order to implement pre-emptive or non-pre-emptive schedules, put the schedule in a tuple with a True or a False as the second term, indicating pre-emptive or non-pre-emptive interruptions. For example::

    'my_preemptive_schedule': ([[10, 2], [30, 0], [100, 1]], True)

And::

    'my_nonpreemptive_schedule': ([[10, 2], [30, 0], [100, 1]], False)

Ciw defaults to non-pre-emptive schedules, and so the following code implies a non-pre-emptive schedule::

    'my_special_schedule_01': [[10, 2], [30, 0], [100, 1]]

