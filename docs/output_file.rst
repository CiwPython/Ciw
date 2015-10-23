.. _output-file:

===============
The Output Data
===============

When a simulation is run via the command line, a :code:`data.csv` file is created.
This file contains does not contain summary statistics, but all the information that happened during the simulation in raw format.
Each time an individual completes service at a service station, a data record of that service is kept.
This file contains all these data records for all services of all customers at all nodes during the simulation run time.

The following table summarises the columns::

    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+
    | I.D number | Class | Node | Arrival Date | Waiting Time | Service Start Date | Service Time | Service End Date | Time Blocked | Exit Date |
    +============+=======+======+==============+==============+====================+==============+==================+==============+===========+
    | 227592     | 1     | 0    | 245.601      | 0.0          | 245.601            | 0.563        | 246.164          | 0.0          | 246.164   |
    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+
    | 411239     | 0     | 0    | 245.633      | 0.531        | 246.164            | 0.608        | 246.772          | 0.0          | 246.772   |
    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+
    | 001195     | 0     | 2    | 247.821      | 0.0          | 247.841            | 1.310        | 249.151          | 0.882        | 250.033   |
    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+
    | ...        | ...   | ...  | ...          | ...          | ...                | ...          | ...              | ...          | ...       |
    +------------+-------+------+--------------+--------------+--------------------+--------------+------------------+--------------+-----------+
