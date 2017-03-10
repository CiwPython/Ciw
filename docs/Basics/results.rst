.. _results-data:

=======
Results
=======

There are a number of ways of accessing simulation results:

- :ref:`sim_recs`
- :ref:`count_losses`
- :ref:`access_nodes`

First, say we have a two node blockage system, and run for 1.5 time units:

    >>> import ciw
    
    >>> params = {
    ... 'Arrival_distributions': [['Exponential', 6.0],
    ...                           ['Exponential', 2.5]],
    ... 'Service_distributions': [['Exponential', 8.5],
    ...                           ['Exponential', 5.5]],
    ... 'Transition_matrices': [[0.0, 1.0],
    ...                         [0.0, 0.0]],
    ... 'Number_of_servers': [2, 1],
    ... 'Queue_capacities': [3, 4]
    ... }

    >>> ciw.seed(1)
    >>> N = ciw.create_network(params)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(1.5)

.. _sim_recs:

------------------
Simulation Records
------------------

Each time an individual completes service at a service station, a data record of that service is kept. The records should look something like the table below:

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

You may access these records as a list of named tuples, using the Simulation's :code:`get_all_records` method:

    >>> recs = Q.get_all_records()

The data records contained in this list are named tuples with the following variable names:

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

From here, we can use list comprehension to access certain performance measures. For example if we want to analyse the waiting times that occurred at Node 2:

    >>> waits2 = [r.waiting_time for r in recs if r.node == 2]
    >>> waits2
    [0.0, 0.252..., 0.242..., 0.366..., 0.278..., 0.064..., 0.540..., 0.455..., 0.474...]
    >>> sum(waits2) / len(waits2)
    0.29721841186163034

We may wish to see the service times of all customers passing through Node 1:

    >>> service1 = [r.service_time for r in recs if r.node == 1]
    >>> service1
    [0.040..., 0.213..., 0.080..., 0.011..., 0.169..., 0.0305..., 0.212..., 0.0287..., 0.067...]


.. _count_losses:

---------------
Counting Losses
---------------

Nodes with finite queueing capacity will turn away newly arriving customers if they arrive when the node is full. These losses are recorded in a :code:`rejection_dict`. This is a dictionary of dictionaries, with nodes and customer classes as keys, and a list of arrival dates as values.

    >>> Q.rejection_dict
    {1: {0: []}, 2: {0: [1.1902..., 1.3520...]}}

Here we see that there was a loss of a customer from Class 0 at Node 2 at dates 0.796, 1.770, 1.195, and 1.252.
If we want the number of losses of Class 0 customers at Node 2:

    >>> number_of_losses_class0_node2 = len(Q.rejection_dict[2][0])
    >>> number_of_losses_class0_node2
    2

For overall number of losses, we can simply sum over all nodes and classes:

    >>> number_of_losses = sum(
    ...     [len(Q.rejection_dict[nd][cls]) for nd in
    ...     range(1, N.number_of_nodes + 1) for cls in
    ...     range(N.number_of_classes)])
    >>> number_of_losses
    2


.. _access_nodes:

---------------
Accessing Nodes
---------------

After the simulation run has ended, the Simulation object :code:`Q` remains in the exact state that it was in at the end of the simulation run. Each node therefore still contains any customers that were waiting or in service at those nodes at that time. This can be revealing, especially the Exit Node.

First, let's look at the nodes themselves:

    >>> Q.nodes
    [Arrival Node, Node 1, Node 2, Exit Node]

The Exit Node contains all individuals who have left the system:

    >>> Q.nodes[-1].all_individuals
    [Individual 2, Individual 3, Individual 1, Individual 5, Individual 4, Individual 6, Individual 7, Individual 8, Individual 9]

This tells us that 4 individuals have completed all their services and have left the system. We can also look at the individuals who are still at the service nodes:

    >>> Q.nodes[1].all_individuals
    [Individual 12, Individual 15]
    
    >>> Q.nodes[2].all_individuals
    [Individual 10, Individual 11]

Combine this with the information gained from the :code:`rejection_dict`, we now know all individuals who have entered the system:

- Individuals 1 to 9 have completed all services.
- Individuals 10 to 11 managed to get to Node 2, but got no further.
- Individuals 12 and 15 entered Node 1, but got no further.
- 2 Individuals were lost, thus Individuals 13 and 14 were rejected.