.. _priority-custs:

===========================
How to Set Priority Classes
===========================

Ciw has the capability to assign priorities to the customer classes.
This is done by mapping customer classes to priority classes, included as a keyword when creating the Network object.
An example is shown::

    priority_classes={'Class 0': 0,
                      'Class 1': 1,
                      'Class 2': 1}

This shows a mapping from three customer classes to two priority classes.
Customers in class 0 have the highest priority and are placed in priority class 0.
Customers in class 1 and class 2 are both placed in priority class 1; they have the same priority as each other but less that those customers in class 0.

Note:

* The lower the priority class number, the higher the priority. Customers in priority class 0 have higher priority than those with in priority class 1, who have higher priority than those in priority class 2, etc.
* Priority classes are essentially Python indices, therefore if there are a total of 5 priority classes, priorities **must** be labelled 0, 1, 2, 3, 4. Skipping a priority class, or naming priority classes anything other than increasing integers from 0 will cause an error.
* The priority discipline used is non-preemptive. Customers always finish their service and are not interrupted by higher priority customers.


To implement this, create the Network object with the :code:`priority_classes` option included with the mapping::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions={'Class 0': [ciw.dists.Exponential(rate=5)],
    ...                            'Class 1': [ciw.dists.Exponential(rate=5)]},
    ...     service_distributions={'Class 0': [ciw.dists.Exponential(rate=10)],
    ...                            'Class 1': [ciw.dists.Exponential(rate=10)]},
    ...     priority_classes={'Class 0': 0, 'Class 1': 1},
    ...     number_of_servers=[1]
    ... )

Now let's run the simulation, comparing the waiting times for Class 0 and Class 1 customers, those with higher priority should have lower average wait than those with lower priority::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100.0)
    >>> recs = Q.get_all_records()

    >>> waits_0 = [r.waiting_time for r in recs if r.customer_class==0]
    >>> sum(waits_0)/len(waits_0)
    0.1866109...

    >>> waits_1 = [r.waiting_time for r in recs if r.customer_class==1]
    >>> sum(waits_1)/len(waits_1)
    7.6103100...


Pre-emption
-----------

There are a number of options that can be used to pre-emptively replace lower priority customers from service. See the following page:

+ :ref:`Pre-emption options <preemption>`.

.. toctree::
   :maxdepth: 1
   :hidden:

   preemption.rst


