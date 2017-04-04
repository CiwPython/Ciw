Ciw
===

A discrete event simulation library for queueing networks
---------------------------------------------------------


.. image:: https://travis-ci.org/CiwPython/Ciw.svg?branch=master
    :target: https://travis-ci.org/CiwPython/Ciw

.. image:: https://img.shields.io/pypi/v/ciw.svg
    :target: https://pypi.python.org/pypi/Ciw

.. image:: https://coveralls.io/repos/github/CiwPython/Ciw/badge.svg?branch=master
    :target: https://coveralls.io/github/CiwPython/Ciw?branch=master

.. image:: https://badges.gitter.im/Join%20Chat.svg
    :target: https://gitter.im/geraintpalmer/Ciw?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://zenodo.org/badge/47995577.svg
    :target: https://zenodo.org/badge/latestdoi/47995577


.. figure:: https://github.com/CiwPython/Ciw/blob/master/docs/_static/logo_small.png?raw=true
    :width: 150px
    :height: 150px
    :scale: 100%
    :align: center

Ciw is a discrete event simulation library for open queueing networks.
It’s core features include the capability to simulate networks of queues, multiple customer classes, and implementation of Type I blocking for restricted networks.
A number of other features are also implemented, including priorities, baulking, schedules, and deadlock detection.


- `Read the documentation <https://ciw.readthedocs.io>`_
- `Example Jupyter Notebooks <https://github.com/CiwPython/Ciw-notebooks>`_
- `Contribution guidelines <https://github.com/CiwPython/Ciw/blob/master/CONTRIBUTING.rst>`_
- `Our great contributors <https://github.com/CiwPython/Ciw/blob/master/AUTHORS.rst>`_
- Install with :code:`pip install ciw`


Usage
-----

Import Ciw::

    >>> import ciw

To define an M/M/3 queue, with λ = 0.2 and μ = 0.1::

    >>> N = ciw.create_network(
    ...     Arrival_distributions=[['Exponential', 0.2]],
    ...     Service_distributions=[['Exponential', 0.1]],
    ...     Number_of_servers=[3]
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
    1.6885...