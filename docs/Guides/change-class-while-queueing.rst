.. _changeclass-whilequeueing:

===========================================
How to Change Customer Class While Queueing
===========================================

Ciw allows customers to change their class while waiting in the queue.
It does this by sampling times that the customer will wait in their current class before changing to other classes.

To do this a matrix of :code:`class_change_time_distributions` is defined. This is an :math:`n \times n` matrix, where :math:`n` is the number of customer classes in the simulation. Each entry is a :ref:`distribution <refs-dists>` object, where the distribution at the :math:`(i, j)^{\text{th}}` entry samples the time that customer of class :math:`i` will wait before changing to class :math:`j`.

This :code:`class_change_time_distributions` matrix is applied to every node in the queueing network.

As an example, consider an M/M/1 queue with three classes of customer. Each class arrives with Exponential inter-arrival rates 2, 4 and 6 respectively; and have Exponential service rates 5, 5, and 4 respectively. Now say that:

 - customers of Class 0 will change to customers of Class 2 if they have waited in the queue for longer than 0.5 time units.
 - customers of Class 1 will change to customers of Class 2 Exponentially at rate 1.

This is input into the simulation as follows::

     >>> import ciw
     >>> N = ciw.create_network(
     ...     arrival_distributions={
     ...         'Class 0': [ciw.dists.Exponential(rate=2)],
     ...         'Class 1': [ciw.dists.Exponential(rate=4)],
     ...         'Class 2': [ciw.dists.Exponential(rate=6)]},
     ...     service_distributions={
     ...         'Class 0': [ciw.dists.Exponential(rate=5)],
     ...         'Class 1': [ciw.dists.Exponential(rate=5)],
     ...         'Class 2': [ciw.dists.Exponential(rate=6)]},
     ...     number_of_servers=[1],
     ...     class_change_time_distributions=[
     ...         [None, None, ciw.dists.Deterministic(value=0.5)],
     ...         [None, None, ciw.dists.Exponential(rate=1)],
     ...         [None, None, None]]
     ... )


As a further example, consider a one node queue with two servers, with two classes of customer. Both arrive with Exponential inter-arrival rate of 5, both Exponential service rates of 6, and Class 0 has priority over Class 1. However customers of Class 1 will change class, and hence change priority, if they have been waiting over 1.5 time units::

    >>> N = ciw.create_network(
    ...     arrival_distributions={
    ...         'Class 0': [ciw.dists.Exponential(5)],
    ...         'Class 1': [ciw.dists.Exponential(5)]},
    ...     service_distributions={
    ...         'Class 0': [ciw.dists.Exponential(6)],
    ...         'Class 1': [ciw.dists.Exponential(6)]},
    ...     number_of_servers=[2],
    ...     priority_classes={
    ...         'Class 0': 0,
    ...         'Class 1': 1},
    ...     class_change_time_distributions=[
    ...         [None, None],
    ...         [ciw.dists.Deterministic(1.5), None]]
    ... )

Running this for a while::

    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(100)
    >>> recs = Q.get_all_records()

We will see than no customer of Class 1 will have a waiting time longer than 1.5 time units, as they will have switched to Class 0 at this point::

    >>> len([r.waiting_time for r in recs if r.customer_class == 1])
    421
    >>> [r for r in recs if r.customer_class == 1 and r.waiting_time >= 1.5]
    []


Under no class changing, we would expect roughly equal amounts of customers of Class 0 and Class 1, as they have the same arrival rates. However, as many Class 1 customers are changing to Class 0 customers, the ratio is now skewed::

    >>> number_of_class0 = len([r for r in recs if r.customer_class == 0])
    >>> number_of_class1 = len([r for r in recs if r.customer_class == 1])
    >>> number_of_class0, number_of_class1
    (563, 421)
