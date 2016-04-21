Going Deeper
============

In :ref:`getting-started` you saw how to run a simple simulation. This page lets you access the simulation by exploring its attributes and methods.
First, set up a parameters file as described in :ref:`sim-parameters`.

Now importing Ciw and the parameters file as a dictionary is simple::

    >>> import ciw
    >>> params = ciw.load_parameters(<path_to_file>) # doctest:+SKIP
    >>> params["Number_of_servers"] # doctest:+SKIP
    [2, 1, 1] # doctest:+SKIP

Set up a Network and Simulation objects, from which all parameters can also be accessed::

    >>> N = ciw.create_network(params) # doctest:+SKIP
    >>> Q = ciw.Simulation(N) # doctest:+SKIP

A full list of Ciw's objects and attributes can be found here: :ref:`objects-attributes`
Now to run a simulation simply run the following method::

    >>> Q.simulate_until_max_time(1000) # doctest:+SKIP

Individuals' data records can be accessed directly using the following methods::

    >>> all_individuals = Q.get_all_individuals()    # Creates a list of all individuals in the system # doctest:+SKIP
    >>> all_individuals[0] # doctest:+SKIP
    Individual 13 # doctest:+SKIP
    >>> all_individuals[0].data_records.values()[0][0].wait    # Time Individual 13 was waiting for this instance of service # doctest:+SKIP
    0.39586652218275364 # doctest:+SKIP
    >>> all_individuals[0].data_records.values()[0][0].arrival_date # Time Individual 13 arrived for this instance of service # doctest:+SKIP
    0.5736475797750542 # doctest:+SKIP

A full list of data records can be obtained, with or without headers::
    
    >>> records = Q.get_all_records(headers=True) # doctest:+SKIP
    >>> records[:3] # doctest:+SKIP
    [['I.D. Number', 'Customer Class', 'Node', 'Arrival Date', 'Waiting Time', 'Service Start Date', 'Service Time', 'Service End Date', 'Time Blocked', 'Exit Date', 'Destination', 'Queue Size at Arrival', 'Queue Size at Departure'],
    [87963, 1, 3, 2499.3093833546704, 0.0, 2499.3093833546704, 0.3418038435924479, 2499.651187198263, 0.0, 2499.651187198263, 1, 6, 3],
    [87958, 0, 2, 2499.442870003776, 0.12156349515498732, 2499.564433498931, 0.051149145815214084, 2499.615582644746, 0.0, 2499.615582644746, 2, 13, 10]] # doctest:+SKIP


The full list data records can be written to a csv file::

    >>> Q.write_records_to_file(<path_to_file>) # doctest:+SKIP

Please see :ref:`output-file` for an explanation of the data contained here.
