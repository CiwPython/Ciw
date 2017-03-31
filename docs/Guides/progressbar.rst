.. _progress-bar:

===============================
How to Implement a Progress Bar
===============================

For an individual run of a simulation, Ciw can enable a progress bar to appear.
This can help visualise how far through a simulation run currently is.
A progress bar may be implemented when using the methods :code:`simulate_until_max_time` and :code:`simulate_until_max_customers`.
In order to implement this, add the option :code:`progress_bar=True`.

An example when using the :code:`simulate_until_max_time` method::

    >>> Q.simulate_until_max_time(2000.0, progress_bar=True) # doctest:+SKIP

The image below shows an example of the output:

.. image:: ../_static/progress_bar_time.png
   :scale: 100 %
   :alt: Output of progress bar (simulate_until_max_time).
   :align: center

An example when using the :code:`simulate_until_max_customers` method::

    >>> Q.simulate_until_max_customers(20000, progress_bar=True) # doctest:+SKIP

And the image below shows the output:

.. image:: ../_static/progress_bar_customers.png
   :scale: 100 %
   :alt: Output of progress bar (simulate_until_max_customers).
   :align: center