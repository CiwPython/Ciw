.. _refs-dists:

===============================
List of Supported Distributions
===============================

Ciw allows a number continuous service and inter-arrival time distributions, as well as empirical, user defined, time dependent, and custom discrete distributions.
Note that when choosing parameters for these distributions, ensure that no negative numbers may be sampled.
The following are currently supported:


- :ref:`uniform_dist`
- :ref:`deterministic_dist`
- :ref:`triangular_dist`
- :ref:`exponential_dist`
- :ref:`gamma_dist`
- :ref:`normal_dist`
- :ref:`lognormal_dist`
- :ref:`weibull_dist`
- :ref:`empirical_dist`
- :ref:`sequential_dist`
- :ref:`custom_pdf`
- :ref:`own_functions`
- :ref:`time_dependent`
- :ref:`no_arrivals`



.. _uniform_dist:

------------------------
The Uniform Distribution
------------------------

The uniform distribution samples a random number between two numbers `a` and `b`.
Write a uniform distribution between `4` and `9` as follows::

    ['Uniform', 4.0, 9.0]





.. _deterministic_dist:

------------------------------
The Deterministic Distribution
------------------------------

The deterministic distribution is non-stochastic, and produces the same service time repeatedly.
Write a deterministic distribution that repeatedly gives a value of `18.2` as follows::

    ['Deterministic', 18.2]





.. _triangular_dist:

---------------------------
The Triangular Distribution
---------------------------

The triangular distribution samples a continuous pdf that rises linearly from its minimum value `low` to its mode value `mode`, and then decreases linearly to its highest attainable value `high`.
Write a triangular distribution between `2.1` and `7.6` with mode of `3.4` as follows::

    ['Triangular', 2.1, 7.6, 3.4]





.. _exponential_dist:

----------------------------
The Exponential Distribution
----------------------------

The exponential distribution samples a random number from the negative exponential distribution with mean :math:`1 / \lambda`.
Write an exponential distribution with mean `0.2` as follows::

    ['Exponential', 5]





.. _gamma_dist:

----------------------
The Gamma Distribution
----------------------

The gamma distribution samples a random number from the gamma distribution with shape parameter :math:`\alpha` and scale parameter :math:`\beta`.
Write a gamma distribution with parameters :math:`\alpha = 0.6` and :math:`\beta = 1.2` as follows::

    ['Gamma', 0.6, 1.2]





.. _normal_dist:

---------------------------------
The Truncated Normal Distribution
---------------------------------

The truncated normal distribution samples a random number from the normal distribution with mean :math:`\mu` and standard deviation :math:`\sigma`.
The distribution is truncated at 0, thus if negative numbers are sampled then that observation is resampled until a positive value is sampled.
Write a normal distribution with parameters :math:`\mu = 0.7` and :math:`\sigma = 0.4` as follows::

    ['Normal', 0.7, 0.4]





.. _lognormal_dist:

--------------------------
The Lognormal Distribution
--------------------------

The lognormal distribution samples a random number from the log of the normal distribution with mean :math:`\mu` and standard deviation :math:`\sigma`.
Write a lognomal distribution, that is a log of the normal distribution with :math:`\mu = 4.5` and :math:`\sigma = 2.0`, as follows::

    ['Lognormal', 4.5, 2.0]





.. _weibull_dist:

------------------------
The Weibull Distribution
------------------------

The Weibull distribution samples a random number from the Weibull distribution with scale parameter :math:`\alpha` and shape parameter :math:`\beta`.
Write a Weibull distribution with :math:`\alpha = 0.9` and :math:`\beta = 0.8` as follows::

    ['Weibull', 0.9, 0.8]





.. _empirical_dist:

-----------------------
Empirical Distributions
-----------------------

There are two methods of defining empirical distributions in Ciw, either by inputting a list of observations, or through giving a path to a :code:`.csv` file containing observations:

Input list of observations::

    ['Empirical', [0.3, 0.3, 0.3, 0.4, 0.5, 0.6, 0.8, 0.9, 1.1, 1.1, 1.1, 1.1]]

Input path to :code:`.csv` file::

    ['Empirical', '<path_to_file>']





.. _sequential_dist:

------------------------
Sequential Distributions
------------------------

The sequential distribution takes a list, and iteratively returns the next observation in that list over time.
The distribution is cyclic, and so once all elements of the list have been sampled, the sequence of sampled values begins again from the beginning of the list::

    ['Sequential', [0.1, 0.1, 0.2, 0.1, 0.3, 0.2]]





.. _custom_pdf:

-----------
Custom PDFs
-----------

Ciw allows users to define their own custom PDFs to sample from.
This distribution samples from a set of values given a probability for each value, that is sampling the value :math:`x` with probability :math:`P(x)`.
For example, if :math:`P(1.4) = 0.2`, :math:`P(1.7) = 0.5`, and :math:`P(1.9) = 0.3`, this is defined in the following way::

    ['Custom', [1.4, 1.7, 1.9], [0.2, 0.5, 0.3]]






.. _own_functions:

--------------------------
User Defined Distributions
--------------------------

Ciw allows users to input their own function to generate service and inter-arrival times.
This is done by feeding in a function in the following way::

	['UserDefined', random.random]





.. _time_dependent:

----------------------------
Time Dependent Distributions
----------------------------

Similar to adding :code:`UserDefined` functions, Ciw allows for time dependent functions.
These are lambda functions that take in a time parameter.
Ciw uses the simulation's current time to sample a new service or inter-arrival time::

    ['TimeDependent', time_dependent_function]





.. _no_arrivals:

-----------
No Arrivals
-----------

If a node does not have any arrivals of a certain class, then the following may be input instead of a distribution::

    'NoArrivals'

Note the lack of square brackets here. Also note that this is only valid for arrivals, and shouldn't be input into the :code:`Service_distributions` option.