.. _refs-results:

=========================
List of Available Results
=========================

Each time an individual completes service at a service station, a data record of that service is kept.
The records should look something like the table below:

    +--------+-------+------+--------------+-----------+--------------------+--------------+------------------+--------------+-----------+-------+-----------------------+-----------------------+-------------+-------------+
    | I.D    | Class | Node | Arrival Date | Wait Time | Service Start Date | Service Time | Service End Date | Time Blocked | Exit Date | Dest. | Queue Size at Arrival | Queue Size at Depart. | Server I.D. | Record Type |
    +========+=======+======+==============+===========+====================+==============+==================+==============+===========+=======+=======================+=======================+=============+=============+
    | 22759  | 1     | 1    | 245.601      | 0.0       | 245.601            | 0.563        | 246.164          | 0.0          | 246.164   | -1    | 0                     | 2                     | 1           | 'service'   |
    +--------+-------+------+--------------+-----------+--------------------+--------------+------------------+--------------+-----------+-------+-----------------------+-----------------------+-------------+-------------+
    | 41129  | 0     | 1    | 245.633      | 0.531     | 246.164            | 0.608        | 246.772          | 0.0          | 246.772   | -1    | 1                     | 5                     | 1           | 'service'   |
    +--------+-------+------+--------------+-----------+--------------------+--------------+------------------+--------------+-----------+-------+-----------------------+-----------------------+-------------+-------------+
    | 00195  | 0     | 2    | 247.821      | 0.0       | 247.841            | 1.310        | 249.151          | 0.882        | 250.033   | 1     | 0                     | 0                     | 2           | 'service'   |
    +--------+-------+------+--------------+-----------+--------------------+--------------+------------------+--------------+-----------+-------+-----------------------+-----------------------+-------------+-------------+
    | ...    | ...   | ...  | ...          | ...       | ...                | ...          | ...              | ...          | ...       | ...   | ...                   | ...                   | ...         | ...         |
    +--------+-------+------+--------------+-----------+--------------------+--------------+------------------+--------------+-----------+-------+-----------------------+-----------------------+-------------+-------------+

You may access these records as a list of named tuples, using the Simulation's :code:`get_all_records` method::

    >>> recs = Q.get_all_records() # doctest:+SKIP

The data records contained in this list are named tuples with the following variable names:

    - :code:`id_number`
       - The unique identification number for that customer.
    - :code:`customer_class`
       - The number of that customer's customer class. If dynamic customer classes are used, this is the customer's previous class, before a new customer class is sampled after service.
    - :code:`node`
       - The number of the node at which the service took place.
    - :code:`arrival_date`
       - The date of arrival to that node, the date which the customer joined the queue.
    - :code:`waiting_time`
       - The amount of time the customer spent waiting for service at that node.
    - :code:`service_start_date`
       - The date at which service began at that node.
    - :code:`service_time`
       - The amount of time spent in service at that node.
    - :code:`service_end_date`
       - The date which the customer finished their service at that node.
    - :code:`time_blocked`
       - The amount of time spent blocked at that node. That is the time between finishing service at exiting the node.
    - :code:`exit_date`
       - The date which the customer exited the node. This may be immediatly after service if no blocking occured, or after some period of being blocked.
    - :code:`destination`
       - The number of the customer's destination, that is the next node the customer will join after leaving the current node. If the customer leaves the system, this will be -1.
    - :code:`queue_size_at_arrival`
       - The size of the queue at the customer's arrival date. Does not include the individual themselves.
    - :code:`queue_size_at_departure`
       - The size of the queue at the customer's exit date. Does not include the individual themselves.
    - :code:`server_id`
       - The unique identification number of the server that served that customer.
    - :code:`record_type`
       - Indicates if the record describes a service, interrupted service, or a customer reneging.
