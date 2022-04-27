.. _preemption:

Pre-emption
===========

When a highler priority customer arrives while a lower priority customer is in service, there are a number of options of what may happen.

+ During non-pre-emptive priorities, customers cannot be interrupted. Therefore the lower priority customers finish their service before the higher priority customer begins their service (:code:`False`).

+ During pre-emptive priorities, the higher priority customer will begin service immediately and replace the lower priority customer. That lower priority customer will immediately stop service and re-enter the beginning of their priority queue. Upon re-entering service the previously displaced customer can either:
    
    + Have their service resampled (:code:`"resample"`);
    + Restart the exact same service (:code:`"restart"`);
    + Continue the original service from where they left off (:code:`"continue"`).


In order to implement pre-emptive or non-pre-emptive priorities, put the priority class mapping in a tuple with a list of the chosen pre-emption options for each node in the network. For example::

    priority_classes=({'Class 0': 0, 'Class 1': 1}, [False, "resample", "restart", "continue"])

This indicates that non-pre-emptive priorities will be used at the first node, and pre-emptive priorities will be used at the second, third and fourth nodes. Interrupted individuals will have their services resampled at the second node, they will restart their original service time at the third node, and they will continue where they left off at the fourth node.

Ciw defaults to non-pre-emptive priorities, and so the following code implies non-pre-emptive priorities::

    priority_classes={'Class 0': 0, 'Class 1': 1} # non-preemptive

**Note**: If there are more than one lowest priority customers in service to pre-empt, then the customer who started service last will be pre-empted.

Unfinished pre-empted services are recorded as :code:`DataRecords` and so are collected along with service records with the :code:`get_all_records` method. They are distinguished by the :code:`record_type` field (services have :code:`service` record type, while pre-empted services have :code:`pre-empted service` record types).