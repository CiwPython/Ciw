.. _server-schedules:

================
Server Schedules
================

Ciw allows users to assign cyclic work schedules to servers at each service centre.
An example cyclic work schedule may look like this:

  +-------------------+---------+---------+---------+---------+---------+---------+
  |    Shift Times    |    0-40 |  40-100 | 100-120 | 120-180 | 180-220 | 220-250 |
  +-------------------+---------+---------+---------+---------+---------+---------+
  | Number of Servers |       2 |       3 |       1 |       2 |       4 |       0 | 
  +-------------------+---------+---------+---------+---------+---------+---------+

This schedule is cyclic, therefore after the last shift (220-250), schedule begins again with the shift (0-40). The cycle length for this schedule is 250. Let's call this schedule :code:`my_special_schedule_01`. We define this schedule in the parameters dictionary as follows::

    'my_special_schedule_01': [[40, 2], [100, 3], [120, 1], [180, 2], [220, 4], [250, 0]]

Here we are saying that there will be 2 servers scheduled between times 0 and 40, 3 between 40 and 100, etc.
This fully defines the cyclic work schedule.

We then need to tell Ciw which node is using this schedule. This come under the :code:`Number_of_servers` part of the parameters dictionary. Simply add the name of the schedule instead of the usual integer value. The example below shows a two node network, the first node using the above schedule, and the second node with 3 static servers::

    'Number_of_servers': ['my_special_schedule_01', 3]

**Note that currently server schedules are incompatible with infinite servers**, and so a schedule cannot include infinite servers.

The equivalent way of inputting schedules into a parameters file is as follows::

    Number_of_servers:
      - 'my_special_schedule_01'
      - 3
    my_special_schedule_01:
      - - 40
        - 2
      - - 100
        - 3
      - - 120
        - 1
      - - 180
        - 2
      - - 220
        - 4
      - - 250
        - 0



Pre-emption
-----------

When a server is due to go off duty during a customer's service, there are two option of what may happen.

+ During a pre-emptive schedule, that server will immediately stop service and leave. Whenever more servers come on duty, they will prioritise the interrupted customers and continue their service. However those customers' service times are re-sampled. Therefore, a customer beginning service at time 5 who is meant to have a service time of 4, should finish service at time 9. However the server goes off duty at time 7. Another server restarts this customer's service at time 10, and re-samples the service time, this time service should last for 8 time units. Therefore the customer will finish service at time 18. In the records, this will be recorded as a total service time of 13, as service began at 5 and finished at 18.

+ During a non-pre-emptive schedule, customers cannot be interrupted. Therefore servers finish the current customer's service before disappearing. This of course may mean that when new servers arrive the old servers are still there, finishing up their original customers, resulting in a brief time where there are more servers on duty that was scheduled.

In order to implement pre-emptive or non-pre-emptive schedules, put the schedule in a tuple with a True or a False as the second term, indicating pre-emptive or non-pre-emptive interruptions. For example::

    'my_preemptive_schedule': ([[40, 2], [100, 3], [120, 1], [180, 2], [220, 4], [250, 0]], True)

And::

    'my_nonpreemptive_schedule': ([[40, 2], [100, 3], [120, 1], [180, 2], [220, 4], [250, 0]], False)

Ciw defaults to non-pre-emptive schedules, and so the following code implies a non-pre-emptive schedule::

    'my_special_schedule_01': [[40, 2], [100, 3], [120, 1], [180, 2], [220, 4], [250, 0]]

