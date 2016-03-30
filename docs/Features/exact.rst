.. _exact-simulations:

=========
Exactness
=========

Due to the `issues and limitations <https://docs.python.org/2/tutorial/floatingpoint.html>`_ that arise when dealing with floating point numbers, Ciw offers an exactness option. Beware however, that using this option may affect performance, and so should only be used if issues with floating point numbers are affecting your results. This may happen for example while using deterministic distributions and server schedules.

In order to implement arithmetical exactness, add this option to the parameters dictionary::

    Exact: 26

The key :code:`Exact` is used to indicate the precision level.