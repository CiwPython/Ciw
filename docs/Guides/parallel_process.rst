.. _parallel_process:

=========================
How to Parallelise Trials
=========================

It is possible to repeat a simulation in parallel using the cores available on a
given computer. This can lead to decreases in computational time as instead of
running each successive simulation :ref:`one after the other <tutorial-iv>` they
can be run at the same time.

As an example consider the following simulation network::

    >>> import ciw
    >>> N = ciw.create_network(
    ...    arrival_distributions=[ciw.dists.Exponential(rate=0.2)],
    ...    service_distributions=[ciw.dists.Exponential(rate=0.1)],
    ...    number_of_servers=[3]
    ... )

The following function will return the mean wait time::

    >>> def get_mean_wait(network, seed=0, max_time=10000):
    ...     """Return the mean waiting time for a given network"""
    ...     ciw.seed(seed)
    ...     Q = ciw.Simulation(network)
    ...     Q.simulate_until_max_time(max_simulation_time=max_time)
    ...     recs = Q.get_all_records()
    ...     waits = [r.waiting_time for r in recs]
    ...     mean_wait = sum(waits) / len(waits)
    ...     return mean_wait
    >>> get_mean_wait(network=N)
    3.386690...

To be able to better approximate the average wait, the above function will be
repeated and the average taken::

    >>> max_time = 500
    >>> repetitions = 200
    >>> mean_waits = [get_mean_wait(network=N, max_time=max_time, seed=seed) for seed in range(repetitions)]
    >>> sum(mean_waits) / repetitions
    3.762233...

To obtain the above by running 2 simulations at the same time (assuming that 2
cores are available), the :code:`multiprocessing` library can be used. In which
case the following :download:`main.py
<../_static/script_for_parallel_processing/main.py>` script gives a working
example:

.. literalinclude:: ../_static/script_for_parallel_processing/main.py

It is possible to use :code:`multiprocessing.cpu_count()` to obtain the number
of available cores.

Note that the conditional :code:`if __name__ == '__main__':` is needed to ensure
that :code:`get_mean_wait` can be pickled. This is necessary to ensure that it
can be used by the parallel processing pool.

The :code:`multiprocessing` library is part of the Python standard library so no
further dependencies are required. However other options are available, one
example of which is `dask <https://www.dask.org>`_.
