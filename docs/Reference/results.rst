.. _refs-results:

=========================
List of Available Results
=========================

Each time an individual completes service at a service station, a data record of that service is kept.
Data records are Named Tuples with the following attributes:

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   * - Attribute
     - Description
   * - :code:`id_number`
     - The unique identification number for that customer.
   * - :code:`customer_class`
     - The number of that customer's customer class. If dynamic customer classes are used, this is the customer's class that they were when they received service at that node.
   * - :code:`original_customer_class`
     - The number of the customer's class when they arrived at the node.
   * - :code:`node`
     - The number of the node at which the service took place.
   * - :code:`arrival_date`
     - The date of arrival to that node, the date which the customer joined the queue.
   * - :code:`waiting_time`
     - The amount of time the customer spent waiting for service at that node.
   * - :code:`service_start_date`
     - The date at which service began at that node.
   * - :code:`service_time`
     - The amount of time spent in service at that node.
   * - :code:`service_end_date`
     - The date which the customer finished their service at that node.
   * - :code:`time_blocked`
     - The amount of time spent blocked at that node. That is the time between finishing service at exiting the node.
   * - :code:`exit_date`
     - The date which the customer exited the node. This may be immediately after service if no blocking occured, or after some period of being blocked.
   * - :code:`destination`
     - The number of the customer's destination, that is the next node the customer will join after leaving the current node. If the customer leaves the system, this will be -1.
   * - :code:`queue_size_at_arrival`
     - The size of the queue at the customer's arrival date. Does not include the individual themselves.
   * - :code:`queue_size_at_departure`
     - The size of the queue at the customer's exit date. Does not include the individual themselves.
   * - :code:`server_id`
     - The unique identification number of the server that served that customer.
   * - :code:`record_type`
     - Indicates what type of data record this is. See below.


The attribute :code:`record_type` can be one of:
    - :code:`"service"`: a completed service
    - :code:`"interrupted service"`: an interrupted service
    - :code:`"renege"`: the waiting time while a customer waited before reneging
    - :code:`"baulk"`: the record of a customer baulking
    - :code:`"rejection"`: the record of a customer being rejected due to the queue being full



You may access these records as a list of named tuples, using the Simulation's :code:`get_all_records` method::

    >>> recs = Q.get_all_records() # doctest:+SKIP

By default, all record types are included. However, we may only want some of the record types, and these can be filtered by passing a list of desired record types to the :code:`only` keyword argument. For example, to only receive service and reneging customers, we can use::

    >>> recs = Q.get_all_records(only=["service", "renege"]) # doctest:+SKIP

