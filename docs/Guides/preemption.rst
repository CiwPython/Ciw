.. _preemption:

Pre-emptive Interruptions & Options for Resuming Service
========================================================

Pre-emptive interruptions can happen in a number of settings. In Ciw they may happen when using customer priorities, that is when a higher priority customer arrives while a lower priority customer is in service, the lower priority customer is displaced from service. They may also happen when using server schedules, when servers go off duty during a customer's service they are displaced.

Resuming Service
----------------

There are a number of options of what may happen when an interrupted individual resumes service.
In Ciw they can either:
    
+ Have their service resampled (:code:`"resample"`);
+ Restart the exact same service (:code:`"restart"`);
+ Continue the original service from where they left off (:code:`"continue"`).



Pre-emption & Priorities
------------------------

During non-pre-emptive priorities, customers cannot be interrupted. Therefore the lower priority customers finish their service before the higher priority customer begins their service (:code:`False`).

In order to implement pre-emptive or non-pre-emptive priorities, put the priority class mapping in a tuple with a list of the chosen pre-emption options for each node in the network. For example::

    priority_classes=({'Class 0': 0, 'Class 1': 1}, [False, "resample", "restart", "continue"])

This indicates that non-pre-emptive priorities will be used at the first node, and pre-emptive priorities will be used at the second, third and fourth nodes. Interrupted individuals will have their services resampled at the second node, they will restart their original service time at the third node, and they will continue where they left off at the fourth node.

Ciw defaults to non-pre-emptive priorities, and so the following code implies non-pre-emptive priorities::

    priority_classes={'Class 0': 0, 'Class 1': 1} # non-preemptive

**Note**: If there are more than one lowest priority customers in service to pre-empt, then the customer who started service last will be pre-empted.

Unfinished pre-empted services are recorded as :code:`DataRecords` and so are collected along with service records with the :code:`get_all_records` method. They are distinguished by the :code:`record_type` field (services have :code:`service` record type, while pre-empted services have :code:`pre-empted service` record types).


Pre-emption & Server Schedules
------------------------------

During a non-pre-emptive schedule, customers cannot be interrupted. Therefore servers finish the current customer's service before disappearing. This of course may mean that when new servers arrive the old servers are still there.
During a pre-emptive schedule, that server will immediately stop service and leave. Whenever more servers come on duty, they will prioritise the interrupted customers and continue their service.

In order to implement pre-emptive or non-pre-emptive schedules, put the schedule in a tuple with the pre-emption option. For example::

    number_of_servers=[
        ([[2, 10], [0, 30], [1, 100]], False)      # non-preemptive
        ([[2, 10], [0, 30], [1, 100]], "resample") # preemptive and resamples service time
        ([[2, 10], [0, 30], [1, 100]], "restart")  # preemptive and restarts origional service time
        ([[2, 10], [0, 30], [1, 100]], "continue") # preemptive continutes services where left off
    ]

Ciw defaults to non-pre-emptive schedules, and so the following code implies a non-pre-emptive schedule::

    number_of_servers=[[[2, 10], [0, 30], [1, 100]]] # non-preemptive


Records of Interrupted Services
-------------------------------

Interrupted services are recorded as :code:`DataRecords` and so are collected along with completed service records with the :code:`get_all_records` method. They are distinguished by the :code:`record_type` field (services have :code:`service` record type, while interrupted services have :code:`interrupted service` record types).

**Note:** For data records of the type :code:`interrupted service`, the :code:`service_time` field corresponds to the originally intended service time for that service, not the amount of time that the customer spent in service before being interrupted. The difference between the :code:`exit_date` and :code:`arrival_date` fields give the amount of time that customer spent in service before being interrupted.

**Note:** In both :code:`service` and :code:`interrupted service` record types, the :code:`waiting_time` field corresponds to the total time between the :code:`arrival_date` and the :code:`service_start_date`. Therefore this includes all previous interrupted services that customer may have experienced before this particular record's service start date.
