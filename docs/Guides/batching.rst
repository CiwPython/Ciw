.. _batch-arrivals:

=========================
How to Set Batch Arrivals
=========================

Ciw allows batch arrivals, that is more than one customer arriving at the same time.
This is implemented using the :code:`Batching_distributions`.
Similar to :code:`Arrival_distributions` and :code:`Service_distributions`, this takes in distributions for each node and customer class that will sample the size of the batch.
Only discrete distributions are allowed, that is distributions that sample integers.

Let's show an example::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     Arrival_distributions=[['Deterministic', 18.5]],
    ...     Service_distributions=[['Deterministic', 3.0]],
    ...     Batching_distributions=[['Deterministic', 3]],
    ...     Number_of_servers=[1]
    ... )

If this system is simulated for 30 time units, only one arrival event will occur.
However, 3 customers will arrive at that node simultaneously.
As there is only one server, two of those customers will have to wait::

    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(30.0)
    >>> recs = Q.get_all_records()

    >>> [r.arrival_date for r in recs]
    [18.5, 18.5, 18.5]
    >>> [r.waiting_time for r in recs]
    [0.0, 3.0, 6.0]

Just like arrival and service distributions, batching distributions can be defined for multiple nodes and multiple customer classes, using lists and dictionaries::

    Batching_distributions={
        'Class 0': [['Deterministic', 3],
                    ['Deterministic', 1]],
        'Class 1': [['Deterministic', 2],
                    ['Deterministic', 2]]},

Note:
  + *Only discrete distributions may be used,* currently implemented are:
     + :code:`Deterministic`
     + :code:`Empirical`
     + :code:`Custom`
     + :code:`Sequential`
     + :code:`TimeDependent`
  + If the keyword :code:`Batching_distributions` is omitted, then no batching is assumed. That is only one customer arrives at a time. Equivalent to :code:`['Deterministic', 1]`.
  + If some nodes/customer classes require no batching, but others do, please use :code:`['Deterministic', 1]`.
  + Batch arrivals may lead to :ref:`simultaneous events <simultaneous_events>`, please take care.