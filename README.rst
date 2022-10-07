Ciw
===

A discrete event simulation library for queueing networks
---------------------------------------------------------

.. image:: https://github.com/CiwPython/Ciw/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/CiwPython/Ciw/actions/workflows/tests.yml

.. image:: https://img.shields.io/pypi/v/ciw.svg
    :target: https://pypi.python.org/pypi/Ciw

.. image:: https://zenodo.org/badge/47995577.svg
    :target: https://zenodo.org/badge/latestdoi/47995577


.. figure:: https://github.com/CiwPython/Ciw/blob/master/docs/_static/logo_small.png?raw=true
    :width: 150px
    :height: 150px
    :scale: 100%
    :align: center

Ciw is a discrete event simulation library for open queueing networks.
It’s core features include the capability to simulate networks of queues, multiple customer classes, and implementation of Type I blocking for restricted networks.


- `Read the documentation <https://ciw.readthedocs.io>`_
- `Contribution guidelines <https://github.com/CiwPython/Ciw/blob/master/CONTRIBUTING.rst>`_
- `Our great contributors <https://github.com/CiwPython/Ciw/blob/master/AUTHORS.rst>`_

Install with :code:`pip install ciw`.

Current supported version of Python:

- Python 3.7
- Python 3.8
- Python 3.9

Usage
-----

Import Ciw::

    >>> import ciw

To define an M/M/3 queue, with λ = 0.2 and μ = 0.1::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=0.2)],
    ...     service_distributions=[ciw.dists.Exponential(rate=0.1)],
    ...     number_of_servers=[3]
    ... )

Now set a seed, create a Simulation object, and simulate for 1440 time units::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(1440)

Collect results::

    >>> recs = Q.get_all_records()

Manipulate results to get useful statistics, e.g. average waiting time::

    >>> waits = [r.waiting_time for r in recs]
    >>> sum(waits) / len(waits)
    4.2305...


Features
--------

A number of other features are also implemented, including:

+ `Type I blocking <https://ciw.readthedocs.io/en/latest/Tutorial-II/tutorial_vi.html>`_
+ `A large range of sampling distributions <https://ciw.readthedocs.io/en/latest/Reference/distributions.html>`_
+ `Phase-Type distributions <https://ciw.readthedocs.io/en/latest/Guides/phasetype.html>`_
+ `Time-dependent and state-dependent distributions <https://ciw.readthedocs.io/en/latest/Guides/time_dependent.html>`_
+ `Batch arrivals <https://ciw.readthedocs.io/en/latest/Guides/batching.html>`_
+ `Baulking customers <https://ciw.readthedocs.io/en/latest/Guides/baulking.html>`_
+ `Reneging customers <https://ciw.readthedocs.io/en/latest/Guides/reneging.html>`_
+ `Processor sharing <https://ciw.readthedocs.io/en/latest/Guides/processor-sharing.html>`_
+ `Multiple customer classes <https://ciw.readthedocs.io/en/latest/Tutorial-II/tutorial_vii.html>`_
+ `Priorities <https://ciw.readthedocs.io/en/latest/Guides/priority.html>`_
+ `Server priorities <https://ciw.readthedocs.io/en/latest/Guides/server_priority.html>`_
+ `Customers changing classes <https://ciw.readthedocs.io/en/latest/Guides/dynamic_customerclasses.html>`_
+ `Server schedules <https://ciw.readthedocs.io/en/latest/Guides/server_schedule.html>`_
+ `State tracking <https://ciw.readthedocs.io/en/latest/Guides/state_trackers.html>`_
+ `Stopping the simulation after a certain amount of customers <https://ciw.readthedocs.io/en/latest/Guides/sim_numcusts.html>`_
+ `Process-based routing <https://ciw.readthedocs.io/en/latest/Guides/process_based.html>`_
+ `Deadlock detection <https://ciw.readthedocs.io/en/latest/Guides/deadlock.html>`_

