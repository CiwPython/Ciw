.. _changeclass-whilequeueing:

===========================================
How to Change Customer Class While Queueing
===========================================

Ciw allows customers to change their class while waiting in the queue.
It does this by sampling times that the customer will wait in their current class before changing to other classes.

To do this a dictionary of :code:`class_change_time_distributions` is defined. This is a dictionary of dictionaries, mapping pairs of customer classes to :ref:`distribution <refs-dists>` objects::
    
    >>> import ciw
    >>> class_change_dist_dict = {
    ...     'Class 0': {'Class 1': ciw.dists.Exponential(rate=5)}
    ... }

In the above example, the time a customer of class :code:`'Class 0'` will wait before becoming a customer of class :code:`'Class 1'` will be samples from an Exponential distribution with rate 5. Any other pairs of classes are assumed not to change into one another if they are not present in the dictionary.

This :code:`class_change_time_distributions` matrix is applied to every node in the queueing network.

As an example, consider an M/M/1 queue with three classes of customer, :code:`C0`, :code:`C1` and :code:`C2`. Each class arrives with Exponential inter-arrival rates 2, 4 and 6 respectively; and have Exponential service rates 5, 5, and 4 respectively. Now say that:

 - :code:`C0` customers will change to :code:`C2` customers if they have waited in the queue for longer than 0.5 time units.
 - :code:`C1` customers will change to :code:`C2` customers Exponentially at rate 1.

This is input into the simulation as follows::

     >>> import ciw
     >>> N = ciw.create_network(
     ...     arrival_distributions={
     ...         'C0': [ciw.dists.Exponential(rate=2)],
     ...         'C1': [ciw.dists.Exponential(rate=4)],
     ...         'C2': [ciw.dists.Exponential(rate=6)]},
     ...     service_distributions={
     ...         'C0': [ciw.dists.Exponential(rate=5)],
     ...         'C1': [ciw.dists.Exponential(rate=5)],
     ...         'C2': [ciw.dists.Exponential(rate=6)]},
     ...     number_of_servers=[1],
     ...     class_change_time_distributions={
     ...         'C0': {'C2': ciw.dists.Deterministic(value=0.5)},
     ...         'C1': {'C2': ciw.dists.Exponential(rate=1)}
     ...     }
     ... )


As a further example, consider a one node queue with two servers, with two classes of customer, :code:`P0` and :code:`P1`. Both arrive with Exponential inter-arrival rate of 5, both Exponential service rates of 6, and :code:`P1` has priority over :code:`P1`. However :code:`P1` customers will change class, and hence change priority, if they have been waiting over 1.5 time units::

    >>> N = ciw.create_network(
    ...     arrival_distributions={
    ...         'P0': [ciw.dists.Exponential(5)],
    ...         'P1': [ciw.dists.Exponential(5)]},
    ...     service_distributions={
    ...         'P0': [ciw.dists.Exponential(6)],
    ...         'P1': [ciw.dists.Exponential(6)]},
    ...     number_of_servers=[2],
    ...     priority_classes={
    ...         'P0': 0,
    ...         'P1': 1},
    ...     class_change_time_distributions={
    ...         'P1': {'P0': ciw.dists.Deterministic(1.5)}
    ...     }
    ... )

Running this for a while::

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100)
    >>> recs = Q.get_all_records()

We will see than no :code:`P1` customer will have a waiting time longer than 1.5 time units, as they will have switched to :code:`P0` at this point::

    >>> len([r.waiting_time for r in recs if r.customer_class == 'P1'])
    421
    >>> [r for r in recs if r.customer_class == 'P1' and r.waiting_time >= 1.5]
    []


Under no class changing, we would expect roughly equal amounts of customers of Class 0 and Class 1, as they have the same arrival rates. However, as many Class 1 customers are changing to Class 0 customers, the ratio is now skewed::

    >>> number_P0 = len([r for r in recs if r.customer_class == 'P0'])
    >>> number_P1 = len([r for r in recs if r.customer_class == 'P1'])
    >>> number_P0, number_P1
    (563, 421)
