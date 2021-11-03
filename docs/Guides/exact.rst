.. _exact-arithmetic:

=================================
How to Implement Exact Arithmetic
=================================

Due to the `issues and limitations <https://docs.python.org/2/tutorial/floatingpoint.html>`_ that arise when dealing with floating point numbers, Ciw offers an exact arithmetic option.
Beware however, that using this option may affect performance, and so should only be used if issues with floating point numbers are affecting your results.
This may happen for example while using deterministic distributions with server schedules.

In order to implement exact arithmetic, add this argument when creating the simulation object::

    >>> Q = ciw.Simulation(N, exact=26) # doctest:+SKIP

The argument :code:`exact` is used to indicate the precision level.

Let's look at an example::
    
    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=5)],
    ...     service_distributions=[ciw.dists.Exponential(rate=10)],
    ...     number_of_servers=[1]
    ... )

Without envoking exact arithmetic, we see that floats are used throughout::

    >>> ciw.seed(2)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100.0)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> waits[-1]
    0.060299051779...
    >>> type(waits[-1])
    <class 'float'>

When envoking exact arithmetic, :code:`decimal.Decimal` types are used throughout::

    >>> ciw.seed(2)
    >>> Q = ciw.Simulation(N, exact=12)
    >>> Q.simulate_until_max_time(100.0)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> waits[-1]
    Decimal('0.0602990518')
    >>> type(waits[-1])
    <class 'decimal.Decimal'>