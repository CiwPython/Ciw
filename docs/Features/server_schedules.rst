.. _server-schedules:

=================================
Assign Work Schedules for Servers
=================================

Ciw allows users to assign cyclic work schedules to servers at each service centre.
An example cyclic work schedule may look like this:

	+-------------------+---------+---------+---------+---------+---------+---------+
	|    Shift Times    |    0-40 |  40-100 | 100-120 | 120-180 | 180-220 | 220-250 |
	+-------------------+---------+---------+---------+---------+---------+---------+
	| Number of Servers |       2 |       3 |       1 |       2 |       4 |       0 | 
	+-------------------+---------+---------+---------+---------+---------+---------+

This schedule is cyclic, therefore after the last shift (220-250), schedule begins again with the shift (0-40). The cycle length for this schedule is 250.

In order to define this work schedule, it must be given a name.
Let's call it :code:`my_special_schedule_01`.

In the :code:`parameters.yml` file, under :code:`Number_of_servers`, for the given node enter the name of the schedule.
An example is shown::

    Number_of_servers:
      - 'my_special_schedule_01'
      - 3

The equivalent way to add this to the parameters dictionary::

    'Number_of_servers':['my_special_schedule_01', 3]

This tells Ciw that at Node 1 the number of servers will vary over time according to the work schedule :code:`my_special_schedule_01`.
This schedule hasn't been defined yet.
To define the work schedule, add the following lines to the end of the :code:`parameters.yml` file::

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

And equivalently, adding the following to the parameters dictionary::

    'my_special_schedule_01':[[40, 2], [100, 3], [120, 1], [180, 2], [220, 4], [250, 0]]

Here we are saying that there will be 2 servers scheduled between times 0 and 40, 3 between 40 and 100, etc.
This fully defines the cyclic work schedule.