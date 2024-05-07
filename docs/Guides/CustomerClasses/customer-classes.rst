.. _customer-classes:

=======================================
How to Set Multiple Classes of Customer
=======================================

Ciw allows us to define different system parameters for different sets of customers sharing the same system infrastructure. These sets of customers are called different customers classes. This is defined by inserting dictionaries of parameters for the keywords in :code:`ciw.create_network`; these dictionaries will have keys of strings representing customer class names, and values corresponding to the parameters themselves.

For example, consider an M/M/3 queue::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=5)],
    ...     service_distributions=[ciw.dists.Exponential(rate=7)],
    ...     number_of_servers=[2]
    ... )

Now imagine we had two different types of customer: 40% of customers are Adults, while 60% of customers are children. Children twice as long to process than adults, and so will have a different service time distribution. In this case, Children and Adults will also have different arrival distributions: remember that arrival distributions define the distribution of inter-arrival times, and the inter-arrival times are defined as the inter-arrival times between two customers of the same class.

Hence we would get::

    >>> N = ciw.create_network(
    ...     arrival_distributions={
    ...         "Adult": [ciw.dists.Exponential(rate=5 * 0.4)],
    ...         "Child": [ciw.dists.Exponential(rate=5 * 0.6)]
    ...     },
    ...     service_distributions={
    ...         "Adult": [ciw.dists.Exponential(rate=7)],
    ...         "Child": [ciw.dists.Exponential(rate=3.5)]
    ...     },
    ...     number_of_servers=[2]
    ... )

The decomposition of the arrival rates is due to `thinning of Poisson processes <(https://galton.uchicago.edu/~lalley/Courses/312/PoissonProcesses.pdf>`_. However, in general, think of arrival distributions as the distribution of inter-arrival times between customers of the same class.

It is important that the keys of these parameter dictionaries are the same throughout. If splitting one keyword by customer class, then *all* keywords that can be split by customer class need to be split by customer class.

When collecting results, the class of the customer associated with each service is also recorded::

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(50)
    >>> recs = Q.get_all_records()
    >>> recs[0].customer_class
    'Child'

    >>> from collections import Counter
    >>> Counter([r.customer_class for r in recs])
    Counter({'Child': 138, 'Adult': 89})

Nearly all parameters of :code:`ciw.create_network` can be split by customer class, unless they describe the architecture of the network itself. Those that can and cannot be split by customer class are listed below:

Can be split by customer class:
    + :code:`arrival_distributions`,
    + :code:`baulking_functions`,
    + :code:`class_change_matrices`,
    + :code:`class_change_time_distributions`,
    + :code:`service_distributions`,
    + :code:`routing`,
    + :code:`batching_distributions`,
    + :code:`reneging_time_distributions`,
    + :code:`reneging_destinations`,

Cannot be split by customer class:
    + :code:`number_of_servers`,
    + :code:`priority_classes`,
    + :code:`queue_capacities`,
    + :code:`ps_thresholds`,
    + :code:`server_priority_functions`,
    + :code:`service_disciplines`,
    + :code:`system_capacity`
