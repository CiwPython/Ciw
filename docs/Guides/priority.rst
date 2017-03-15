.. _priority-custs:

===========================
How to Set Priority Classes
===========================

Ciw has the capability to assign priorities to the customer classes. This is done simply by mapping customer classes to priority classes, included in the parameters dictionary. An example is shown::

    'Priority_classes': {'Class 0': 0,
                         'CLass 1': 1,
                         'Class 2': 1}

This shows a mapping from three customer classes to two priority classes. Customers in class 0 have the highest priority and are placed in priority class 0. Customers in class 1 and class 2 are both placed in priority class 1; they have the same priority as each other but less that those customers in class 0.

Note:

* The lower the priority class number, the higher the priority. Customers in priority class 0 have higher priority than those with in priority class 1, who have higher priority than those in priority class 2, etc.
* Priority classes are essentially Python indices, therefore if there are a total of 5 priority classes, priorities **must** be labelled 0, 1, 2, 3, 4. Skipping a priority class, or naming priority classes anything other that increasing integers from 0 is forbidden.
* The priority discipline used is non-preemptive. Customers always finish their service and are not interrupted by higher priority customers.


To implement this, define the parameters dictionary with the :code:`Priority_classes` option included with the mapping::

    >>> params = {
    ...     'Arrival_distributions': {'Class 0': [['Exponential', 5]],
    ...                               'Class 1': [['Exponential', 5]]},
    ...     'Service_distributions': {'Class 0': [['Exponential', 10]],
    ...                               'Class 1': [['Exponential', 10]]},
    ...     'Transition_matrices': {'Class 0': [[0.0]],
    ...                             'Class 1': [[0.0]]},
    ...     'Priority_classes': {'Class 0': 0, 'Class 1': 1},
    ...     'Number_of_servers': [1]
    ... }

Now let's run the simulation, comparing the waiting times for Class 0 and Class 1 customers, those with higher priority should have lower average wait than those with lower priority::

    >>> ciw.seed(1)
    >>> N = ciw.create_network(params)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100.0)
    >>> recs = Q.get_all_records()

    >>> waits_0 = [r.waiting_time for r in recs if r.customer_class==0]
    >>> sum(waits_0)/len(waits_0)
    0.1529189...

    >>> waits_1 = [r.waiting_time for r in recs if r.customer_class==1]
    >>> sum(waits_1)/len(waits_1)
    3.5065047...