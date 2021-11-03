.. _from-file:

================================
How to Read & Write to/from File
================================

When running experiments, it may be useful to read in parameters from a file, and to export data records to file.
This can be done easily in Ciw.
Parameter dictionaries can be represented as :code:`.yml` files, and results can be output as :code:`.csv` files.

Parameter Files
~~~~~~~~~~~~~~~

Consider the following Network::


    >>> import ciw
	>>> N = ciw.create_network(
	...     arrival_distributions={'Class 0': [ciw.dists.Exponential(rate=6.0), ciw.dists.Exponential(rate=2.5)]},
	...     service_distributions={'Class 0': [ciw.dists.Exponential(rate=8.5), ciw.dists.Exponential(rate=5.5)]},
	...     routing={'Class 0': [[0.0, 0.2], [0.1, 0.0]]},
	...     number_of_servers=[1, 1],
	...     queue_capacities=[float('inf'), 4]
	... )

This can be represented by the :code:`.yml` file below::

	parameters.yml

	arrival_distributions:
	  Class 0:
	  - - Exponential
	    - 6.0
	  - - Exponential
	    - 2.5
	service_distributions:
	  Class 0:
	  - - Exponential
	    - 8.5
	  - - Exponential
	    - 5.5
	routing:
	  Class 0:
	  - - 0.0
	    - 0.2
	  - - 0.1
	    - 0.0
	number_of_servers:
	- 1
	- 1
	queue_capacities:
	- "Inf"
	- 4

This can then be created into a Network object using the :code:`ciw.create_network_from_yml` function::

	>>> import ciw # doctest:+SKIP
	>>> N = ciw.create_network_from_yml('<path_to_file>') # doctest:+SKIP
	>>> Q = ciw.Simulation(N) # doctest:+SKIP


Exporting Results
~~~~~~~~~~~~~~~~~

Once a simulation has been run, all data records can be exported to file using the :code:`write_records_to_file` method of the Simulation object.
This method writes all results that are obtained by the :code:`get_all_records` method (see :ref:`here <refs-results>` for more information) to a :code:`.csv` file, where each row is an observation ad each column a variable::

	>>> Q.write_records_to_file('<path_to_file>') # doctest:+SKIP

This method also takes the optional keyword argument :code:`header`.
If this is set to :code:`True` then the first row of the :code:`.csv` file will be the variable names.
The default value is :code:`True`, set to :code:`False` is a row of variable names are not needed::

	>>> Q.write_records_to_file('<path_to_file>', headers=True) # doctest:+SKIP
	>>> Q.write_records_to_file('<path_to_file>', headers=False) # doctest:+SKIP
