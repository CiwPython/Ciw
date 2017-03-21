.. _tutorial-v:

===============================
Tutorial V: A Network of Queues
===============================

Ciw's real power comes when modelling networks of queues. That is many service nodes, such that when customers finish service, there is a probability of joining another node, rejoining the current node, or leaving the system. These types of systems arise naturally in communications, manufacturing, and service industries.

Imagine a café that sells both hot and cold food. Customer arrive and can take a few routes:

+ Customers only wanting cold food must queue at the cold food counter, and then take their food to the till to pay.
+ Customers only wanting hot food must queue at the hot food counter, and then take their food to the till to pay.
+ Customers wanting both hot and cold food must first queue for cold food, then hot food, and then take both to the till and pay.

In this system there are three nodes: Cold food counter (Node 1), Hot food counter (Node 2), and the till (Node 3). Customer wanting hot food only arrive at a rate of 12 per hour. Customers wanting cold food arrive at a rate of 18 per hour. 30% of all customer who buy cold food also want to buy hot food. On average it takes 1 minute to be served cold food, 2 and a half minutes to be served hot food, and 2 minutes to pay. There is one server at the cold food counter, 2 servers at the hot food counter, and 2 servers at the till.

A diagram of the system is shown below:

.. image:: ../_static/cafe.svg
   :scale: 100 %
   :alt: Diagram of café queueing network.
   :align: center

This system can be described in one parameters dictionary. Arrival and Service distributions are listed in the order of the nodes. So are number of servers. We do however require a *transition matrix*.

A transition matrix is an :math:`n \times n` matrix (where :math:`n` is the number of nodes in the network) such that the :math:`(i,j)\text{th}` element corresponds to the probability of transitioning to node :math:`j` after service at node :math:`i`. In Python, we write this matrix as a list of lists. The transition matrix for the café system looks like this::

    [[0.0, 0.3, 0.7],
     [0.0, 0.0, 1.0],
     [0.0, 0.0, 0.0]]

That is 30% of cold food customers then transition to hot food, while the remaining 70% go to the till, and 100% of hot food customers transition to the till. So, our parameters dictionary for the café looks like this::

    >>> params = {
    ...     'Arrival_distributions': [['Exponential', 0.3],
    ...                               ['Exponential', 0.2],
    ...                               'NoArrivals'],
    ...     'Service_distributions': [['Exponential', 1.0],
    ...                               ['Exponential', 0.4],
    ...                               ['Exponential', 0.5]],
    ...     'Transition_matrices': [[0.0, 0.3, 0.7],
    ...                             [0.0, 0.0, 1.0],
    ...                             [0.0, 0.0, 0.0]],
    ...     'Number_of_servers': [1, 2, 2]
    ... }

Notice the Arrival distributions: 18 cold food arrivals per hour is equivalent to 0.3 per minute; 12 hot food arrivals per hour is equivalent to 0.2 per minute; and we want no arrivals to occur at the Till.

Notice the Service distributions: an average cold food service time of 1 minute is equivalent to a rate of 1/1 = 1 service per minute; an average hot food service time of 2.5 minutes is equivalent to 1/2.5 = 0.4 services per minute; and an average till service time of 2 minutes is equivalent to 0.5 services per minute.

Let's simulate this for one shift of lunchtime of 3 hours (180 mins). At the beginning of lunchtime he café opens, and thus begins from an empty system. Therefore no warmup time is required. We'll use 20 minutes of cooldown time. We'll run 10 trials, to get a resume of the average number of customers that pass through the system. To find the average number of customers that pass through the system, we can count the number of data records that have passed through Node 3 (the Till)::

    >>> import ciw
    >>> completed_custs = []
    >>> for trial in range(10):
    ...     ciw.seed(trial)
    ...     N = ciw.create_network(params)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(200)
    ...     recs = Q.get_all_records()
    ...     num_completed = len([r for r in recs if r.node==3 and r.arrival_date < 180])
    ...     completed_custs.append(num_completed)

We can now get the average number of customers that have passed through the system::

    >>> sum(completed_custs)/len(completed_custs)
    83.0

So we've now used Ciw to find out that this café can serve an average 83 customers in a three hour lunchtime.