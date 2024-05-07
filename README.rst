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

- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

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

+ `Type I blocking <https://ciw.readthedocs.io/en/latest/Guides/Queues/queue_capacities.html>`_
+ `A large range of sampling distributions <https://ciw.readthedocs.io/en/latest/Reference/distributions.html>`_
+ `Phase-Type distributions <https://ciw.readthedocs.io/en/latest/Guides/Distributions/phasetype.html>`_
+ `Time-dependent and state-dependent distributions <https://ciw.readthedocs.io/en/latest/Guides/Distributions/time_dependent.html>`_
+ `Batch arrivals <https://ciw.readthedocs.io/en/latest/Guides/Arrivals/batching.html>`_
+ `Baulking customers <https://ciw.readthedocs.io/en/latest/Guides/CustomerBehaviour/baulking.html>`_
+ `Reneging customers <https://ciw.readthedocs.io/en/latest/Guides/CustomerBehaviour/reneging.html>`_
+ `Processor sharing <https://ciw.readthedocs.io/en/latest/Guides/Services/processor-sharing.html>`_
+ `Multiple customer classes <https://ciw.readthedocs.io/en/latest/Guides/CustomerClasses/customer-classes.html>`_
+ `Priorities <https://ciw.readthedocs.io/en/latest/Guides/CustomerClasses/priority.html>`_
+ `Server priorities <https://ciw.readthedocs.io/en/latest/Guides/Services/server_priority.html>`_
+ `Service disciplines <https://ciw.readthedocs.io/en/latest/Guides/Services/service_disciplines.html>`_
+ `Customers changing classes while queueing <https://ciw.readthedocs.io/en/latest/Guides/CustomerClasses/change-class-while-queueing.html>`_
+ `Customers changing classes after service <https://ciw.readthedocs.io/en/latest/Guides/CustomerClasses/change-class-after-service.html>`_
+ `Server schedules <https://ciw.readthedocs.io/en/latest/Guides/Services/server_schedule.html>`_
+ `Slotted services <https://ciw.readthedocs.io/en/latest/Guides/Services/slotted.html>`_
+ `State tracking <https://ciw.readthedocs.io/en/latest/Guides/System/state_trackers.html>`_
+ `Stopping the simulation after a certain amount of customers <https://ciw.readthedocs.io/en/latest/Guides/Simulation/sim_numcusts.html>`_
+ `Process-based routing <https://ciw.readthedocs.io/en/latest/Guides/Routing/process_based.html>`_
+ `Logical routing <https://ciw.readthedocs.io/en/latest/Guides/Reference/routers.html>`_
+ `Deadlock detection <https://ciw.readthedocs.io/en/latest/Guides/System/deadlock.html>`_

