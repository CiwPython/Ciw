.. _priority-queues:

===============
Priority Queues
===============

Ciw has the capability to assign priorities to the customer classes. This is done simply by mapping customer classes to priority classes, included in the parameters dictionary. An example is shown::

    >>> params = {
    ...     'Arrival_distributions': {'Class 0': [['Exponential', 2.0]],
    ...                               'Class 1': [['Exponential', 2.0]],
    ...                               'Class 2': [['Exponential', 1.0]]},
    ...     'Service_distributions': {'Class 0': [['Exponential', 5.0]],
    ...                               'Class 1': [['Exponential', 5.0]],
    ...                               'Class 2': [['Exponential', 4.0]]},
    ...     'Transition_matrices': {'Class 0': [[0.0]],
    ...                             'Class 1': [[0.0]],
    ...                             'Class 2': [[0.0]]},
    ...     'Number_of_servers': [1],
    ...     'Priority_classes': {'Class 0': 0,
    ...                          'CLass 1': 1,
    ...                          'Class 2': 1}
    ... }

This shows an M/M/1 system with three customer classes, mapped to two priority classes. Customers in class 0 have the highest priority and are placed in priority class 0. Customers in class 1 and class 2 are both placed in priority class 1; they have the same priority as each other but less that those customers in class 0.

Note:

* The lower the priority class, the higher the priority. Customers in priority class 0 have higher priority than those with in priority class 1, who have higher priority than those in priority class 2, etc.
* Priority classes are essentially Python indices, therefore if there are a total of 5 priority classes, priorities MUST be labelled 0, 1, 2, 3, 4. Skipping a priority class, of naming priority classes anything other that increasing integers from 0 is forbidden.
* The priority discipline used is non-preemptive. Customers always finish their service and are not interrupted by higher priority customers.