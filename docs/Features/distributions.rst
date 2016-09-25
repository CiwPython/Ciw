.. _service-distributions:

==========================================
Service & Inter-Arrival Time Distributions
==========================================

Ciw currently allows the following continuous service and inter-arrival time distributions, as well as empirical distributions and inputting your own functions:

- :ref:`uniform_dist`
- :ref:`deterministic_dist`
- :ref:`triangular_dist`
- :ref:`exponential_dist`
- :ref:`gamma_dist`
- :ref:`lognormal_dist`
- :ref:`weibull_dist`
- :ref:`empirical_dist`
- :ref:`own_functions`
- :ref:`no_arrivals`


See :ref:`custom-distributions` for how to define custom discrete service time distributions.
Note that when choosing parameters for these distributions, ensure that no negative numbers may be sampled.

.. _uniform_dist:

------------------------
The Uniform Distribution
------------------------

The uniform distribution samples a random number between two numbers `a` and `b`.
In the parameters dictionary, write a uniform distribution between `4` and `9` as follows::

    ['Uniform', 4.0, 9.0]




.. _deterministic_dist:

------------------------------
The Deterministic Distribution
------------------------------

The deterministic distribution is non-stochastic, and produces the same service time repeatedly.
In the parameters dictionary, write a deterministic distribution that repeatedly gives a value of `18.2` as follows::

    ['Deterministic', 18.2]




.. _triangular_dist:

---------------------------
The Triangular Distribution
---------------------------

The triangular distribution samples a continuous pdf that rises linearly from its minimum value `low` to its mode value `mode`, and then decreases linearly to its highest attainable value `high`.
In the parameters dictionary, write a triangular distribution between `2.1` and `7.6` with mode of `3.4` as follows::

    ['Triangular', 2.1, 7.6, 3.4]





.. _exponential_dist:

----------------------------
The Exponential Distribution
----------------------------

The exponential distribution samples a random number from the negative exponential distribution with `1 / lambda`.
In the parameters dictionary, write an exponential distribution with mean `0.2` as follows::

    ['Exponential', 5]







.. _gamma_dist:

----------------------
The Gamma Distribution
----------------------

The gamma distribution samples a random number from the gamma distribution with shape parameter `alpha` and scale parameter `beta`.
In the parameters dictionary, write a gamma distribution with parameters `alpha = 0.6` and `beta = 1.2` as follows::

    ['Gamma', 0.6, 1.2]







.. _lognormal_dist:

--------------------------
The Lognormal Distribution
--------------------------

The lognormal distribution samples a random number from the log of the normal distribution with mean `mu` and standard deviation `sigma`.
In the parameters dictionary, write a lognomal distribution of the normal distribution with mean `4.5` and standard deviation `2.0` as follows::

    ['Lognormal', 4.5, 2.0]






.. _weibull_dist:

------------------------
The Weibull Distribution
------------------------

The Weibull distribution samples a random number from the Weibull distribution with scale parameter `alpha` and shape parameter `beta`.
In the parameters dictionary, write a Weibull distribution with `alpha = 0.9` and `beta = 0.8` as follows::

    ['Weibull', 0.9, 0.8]





.. _empirical_dist:

-----------------------
Empirical Distributions
-----------------------

There are two methods of defining empirical distributions in Ciw, either through inputting a list of observations, or through giving a path to a :code:`.csv` file containing observations:

Input list of observations::

    ['Empirical', [0.3, 0.3, 0.3, 0.4, 0.5, 0.6, 0.8, 0.9, 1.1, 1.1, 1.1, 1.1]]

Input path to :code:`.csv` file::

    ['Empirical', '<path_to_file>']





.. _own_functions:

-------------------
Inputting Functions
-------------------

Ciw allows users to input their own function to generate service and inter-arrival times. This is done by feeding in a function in the following way::

	['UserDefined', lambda : random.random()]



.. _no_arrivals:

-----------
No Arrivals
-----------

If a node does not have any arrivals of a certain class, then the following may be input into the parameters dictionary::

    'NoArrivals'

Note the lack of square brackets here. Also note that this is only valid for arrivals, and shouldn't be input into the :code:`Service_distributions` option.