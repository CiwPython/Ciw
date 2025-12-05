.. _dist-stats:

===============================================
How to Access Distributions' Summary Statistics
===============================================

Every distribution object in Ciw has attributes giving summary statisics for the distributions. These are:

+ Mean
+ Median
+ Variance
+ Standard deviation
+ Upper limit
+ Lower limit

They can be accessed as follows::

    >>> import ciw
    >>> D = ciw.dists.Exponential(rate=5)
    >>> D.mean
    0.2
    >>> D.median
    0.1386294361...
    >>> D.variance
    0.04
    >>> D.sd
    0.2
    >>> D.upper_limit
    inf
    >>> D.lower_limit
    0


In some cases where a closed from expression does not exist, the attribute will return :code:`nan`. For example::

    >>> G = ciw.dists.Gamma(shape=0.6, scale=1.2)
    >>> G.median
    nan


And where possible, summary statistics are calculated for :ref:`combined distributions <combine-dists>`. For example::


    >>> D1 = ciw.dists.Uniform(lower=2, upper=6)
    >>> D2 = ciw.dists.Uniform(lower=3, upper=9)
    >>> D = D1 + D2
    >>> D1.mean, D2.mean, D.mean
    (4.0, 6.0, 10.0)
    >>> D1.sd, D2.sd, D.sd
    (1.154..., 1.732..., 2.081...)
    >>> D1.lower_limit, D2.lower_limit, D.lower_limit
    (2, 3, 5)
    >>> D1.upper_limit, D2.upper_limit, D.upper_limit
    (6, 9, 15)

and :ref:`mixture distributions <combine-dists>`::

    >>> D1 = ciw.dists.Uniform(lower=2, upper=6)
    >>> D2 = ciw.dists.Uniform(lower=3, upper=9)
    >>> D = ciw.dists.MixtureDistribution(
    ...     dists=[D1, D2],
    ...     probs=[0.5, 0.5]
    ... )
    >>> D.mean
    5.0
    >>> D.sd
    1.7795...
    >>> D.upper_limit
    9
    >>> D.lower_limit
    2




