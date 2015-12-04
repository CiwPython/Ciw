.. _parameters-dict:

=========================
The Parameters Dictionary
=========================

ASQ's Simulation object takes in a dictionary of parameters. This takes the same format as the parameters file described in :ref:`parameters-file`.

An example is shown below::

    {'Arrival_rates': {'Class 1': [1.0, 1.8, 7.25],
                       'Class 0': [6.0, 4.5, 2.0]},
     'Number_of_nodes': 3,
     'detect_deadlock': False,
     'Simulation_time': 2500,
     'Number_of_servers': [2, 1, 1],
     'Queue_capacities': ['Inf', 'Inf', 10],
     'Number_of_classes': 2,
     'Service_rates': {'Class 1': [['Exponential', 8.5], ['Triangular', 0.1, 0.8, 0.95], ['Exponential', 3.0]],
                       'Class 0': [['Exponential', 7.0], ['Exponential', 5.0], ['Gamma', 0.4, 0.6]]},
     'Transition_matrices': {'Class 1': [[0.7, 0.05, 0.05], [0.5, 0.1, 0.4], [0.2, 0.2, 0.2]],
                             'Class 0': [[0.1, 0.6, 0.2], [0.0, 0.5, 0.5], [0.3, 0.1, 0.1]]}}

Alternatively, ASQ's :code:`load_parameters` function imports a parameters file as a dictionary. Simply point the function towards directory containing a valid :code:`parameters.yml` file::

    >>> import asq
    >>> params_dict = asq.load_parameters("path/to/parameters/file/")