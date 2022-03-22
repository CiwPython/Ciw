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

