.. _collect-results:

======================
How to Collect Results
======================

Once a simulation has been run, results can be collected. Results take the form of a data record. Certain events in a simulation's run cause data records to be created that describe those events. Those results are:

+ Services
+ :ref:`Pre-empted services<preemption>`
+ :ref:`Baulking customers<baulking-functions>`
+ :ref:`Reneging customers<reneging-customers>`
+ :ref:`Rejected customers<queue-capacities>`

In order to collect all data records, we use the :code:`get_all_records()` method of the Simulation object.

For example, in an M/M/3 queue::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=1)],
    ...     service_distributions=[ciw.dists.Exponential(rate=2)],
    ...     number_of_servers=[1]
    ... )
    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100)

To collect a list of all data records::

    >>> recs = Q.get_all_records()

This gives a list of :code:`DataRecord` objects, which are named tuples with a number of fields with useful information about the event in question::

    >>> r = recs[14]
    >>> r
    Record(id_number=15, customer_class='Customer', original_customer_class='Customer', node=1, arrival_date=16.58266..., waiting_time=0.0, service_start_date=16.58266..., service_time=1.69969..., service_end_date=18.28236..., time_blocked=0.0, exit_date=18.28236..., destination=-1, queue_size_at_arrival=0, queue_size_at_departure=1, server_id=1, record_type='service')

These data records have a number of useful fields, set out in detail :ref:`here<refs-results>`. Importantly, fields can be accessed as attributes::

    >>> r.service_start_date
    16.58266884119802

And so relevant data can be gathered using list comprehension::

    >>> waiting_times = [r.waiting_time for r in recs]
    >>> sum(waiting_times) / len(waiting_times)
    0.3989747...

For easier manipulation, use in conjuction with `Pandas <https://pandas.pydata.org/>`_ is recommended, allowing for easier filtering, grouping, and summary statistics calculations. Lists of data records convert to Pandas data frames smoothly:

    >>> import pandas as pd
    >>> recs_pd = pd.DataFrame(recs)
    >>> recs_pd  # doctest: +SKIP

.. image:: ../../_static/recs_pandas.png
   :scale: 30 %
   :alt: A Pandas data frame of Ciw data records.
   :align: center



Types of Records
~~~~~~~~~~~~~~~~

One particular field of note is the :code:`record_type` field, which indicates which of the five events caused that data record to be created.

+ Services: gives :code:`record_type="service"`
+ Pre-empted services gives :code:`record_type="interrupted service"`
+ Baulking customers gives :code:`record_type="baulk"`
+ Reneging customers gives :code:`record_type="renege"`
+ Rejected customers gives :code:`record_type="rejection"`

It is only by understanding the record types that we can understand the other data record fields. More information is given on the relevant Guide pages for each feature.

When a simulation can produce multiple types of data record, it is sometimes useful to be able to only collect data records of a give type or types. we can do this with the optional keyword argument :code:`only`, which takes a list of the record types we are interested in::

    >>> lost_customer_recs = Q.get_all_records(only=["rejection", "baulk", "renege"])
    >>> service_recs = Q.get_all_records(only=["service"])

