Going Deeper
============

In :ref:`getting-started` you saw how to run a simple simulation. This page lets you access the simulation by exploring its attributed and methods.
First, set up a parameters file as described in :ref:`parameters-file`.

Now importing ASQ and the parameters file as a dictionary is simple::

    >>> import asq
    >>> params = asq.load_parameters("path/to/parameters/file/")
    >>> params["Number_of_servers"]
    [2, 1, 1]

Set up a Simulation object, from which all parameters can also be accessed::

    >>> Q = asq.Simulation(params)
    >>> Q.number_of_nodes
    3
    >>> Q.queue_capacities
    ['Inf', 'Inf', 10]
    >>> Q.lmbda    # The arrival rates of the system
    [[1.0, 1.8, 7.25], [6.0, 4.5, 2.0]]
    >>> Q.lmbda[0]    # Arrival rates of the 0th class
    [1.0, 1.8, 7.2]

A full list of ASQ's objects and attributes can be found here: :ref:`objects-attributes`
Now to run a simulation simply run the following method::

    >>> Q.simulate_until_max_time()

Individuals' data records can be accessed directly using the following methods::

    >>> all_individuals = Q.get_all_individuals()    # Creates a list of all individuals in the system
    >>> all_individuals[0]
    Individual 13
    >>> all_individuals[0].data_records.values()[0][0].wait    # Time Individual 13 was waiting for this instance of service
    0.39586652218275364
    >>> all_individuals[0].data_records.values()[0][0].arrival_date # Time Individual 13 arrived for this instance of service
    0.5736475797750542

The full list data records can be written to a csv file::

    >>> Q.write_records_to_file(<path_to_file>)

Please see :ref:`output-file` for an explanation of the data contained here.