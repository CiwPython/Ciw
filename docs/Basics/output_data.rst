.. _output-file:

===============
The Output Data
===============

Once a simulation has been run, the following method may be called to write a data file::

    >>> Q.write_records_to_file(<path_to_file>) # doctest:+SKIP

This file contains does not contain summary statistics, but all the information that happened during the simulation in raw format.
Each time an individual completes service at a service station, a data record of that service is kept.
This file contains all these data records for all services of all customers at all nodes during the simulation run time.

The following table summarises the columns:

    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+-------------+-----------------------+-------------------------+
    | I.D number | Class | Node | Arrival Date | Waiting Time | Service Start Date | Service Time | Service End Date | Time Blocked | Exit Date | Destination | Queue Size at Arrival | Queue Size at Departure |
    +============+=======+======+==============+==============+====================+==============+==================+==============+===========+=============+=======================+=========================+
    | 227592     | 1     | 1    | 245.601      | 0.0          | 245.601            | 0.563        | 246.164          | 0.0          | 246.164   | -1          | 0                     | 2                       |
    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+-------------+-----------------------+-------------------------+
    | 411239     | 0     | 1    | 245.633      | 0.531        | 246.164            | 0.608        | 246.772          | 0.0          | 246.772   | -1          | 1                     | 5                       |
    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+-------------+-----------------------+-------------------------+
    | 001195     | 0     | 2    | 247.821      | 0.0          | 247.841            | 1.310        | 249.151          | 0.882        | 250.033   | 1           | 0                     | 0                       |
    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+-------------+-----------------------+-------------------------+
    | ...        | ...   | ...  | ...          | ...          | ...                | ...          | ...              | ...          | ...       | ...         | ...                   | ...                     |
    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+-------------+-----------------------+-------------------------+

The :code:`write_records_to_file` method writes a header as default. To disable this feature, input :code:`headers=False`::

    >>> Q.write_records_to_file(<path_to_file>, header=False) # doctest:+SKIP

Records may be accessed in Python, using the :code:`Q.get_all_records()` method. This returns a list of named tuples with the following names:

    - :code:`id_number`
    - :code:`customer_class`
    - :code:`node`
    - :code:`arrival_date`
    - :code:`waiting_time`
    - :code:`service_start_date`
    - :code:`service_time`
    - :code:`service_end_date`
    - :code:`time_blocked`
    - :code:`exit_date`
    - :code:`destination`
    - :code:`queue_size_at_arrival`
    - :code:`queue_size_at_departure`

As an example, the 10th record's waiting time may be accessed as follows (Note however that the order of the records is meaningless)::

    >>> recs = Q.get_all_records # doctest:+SKIP
    >>> recs[10].waiting_time # doctest:+SKIP
    0.0


------------------------
The Rejection Dictionary
------------------------

When nodes have a limited queueing capacity, some arriving customers are rejected from the system. Data about these rejected customers is kept in the Simulation object's :code:`rejection_dict`. This is a dictionary of dictionaries, with nodes and customer classes as keys, and a list of arrival dates as values. For example :code:`Q.rejection_dict[1][2]` gives a list of the times that new arriving customers of class 2 were rejected from node 1.