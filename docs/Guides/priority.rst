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

When a highler priority customer arrives while a lower priority customer is in service, there are two options of what may happen.

+ During pre-emptive priorities, the higher priority customer will begin service immediately and replace the lower priority customer. That lower priority customer will immediately stop service and re-enter the beginning of their priority queue. However that customer's service time will be re-sampled when they eventually begin service.

+ During non-pre-emptive priorities, customers cannot be interrupted. Therefore the lower priority customers finish their service before the higher priority customer begins their service.

In order to implement pre-emptive or non-pre-emptive priorities, put the priority class mapping in a tuple with a list of :code:`True` or a :code:`False` as the second term, indicating pre-emptive or non-pre-emptive interruptions at each node of the network. For example::

    priority_classes=({'Class 0': 0, 'Class 1': 1}, [True, True, False])

This indicates that pre-emptive priorities will be used at the first two nodes, and non-pre-emptive priorities will be used at the third node.

Ciw defaults to non-pre-emptive priorities, and so the following code implies non-pre-emptive priorities::

    priority_classes={'Class 0': 0, 'Class 1': 1} # non-preemptive

