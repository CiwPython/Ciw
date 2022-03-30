.. _tutorial-vii:

==========================================
Tutorial VII: Multiple Classes of Customer
==========================================

Imagine a 24 hour paediatricians clinic:

+ Two types of patient arrive, babies and children.
+ When patients arrive they must register at the reception desk.
+ Registration time is random, but for babies lasts an average of 15 minutes, and for children and average of 10 minutes.
+ After registration the two types of patients go to separate waiting rooms where they wait to be seen by separate specialists.
+ Appointments with specialists take a random amount of time, but on average last one hour.
+ There is one receptionist on duty, two baby specialists on duty, and three children's specialists on duty.
+ Babies arrive randomly at a rate of one per hour, children at a rate two per hour.

In this set-up we have a scenario where two different types of customer are accessing the same resources, but may use them in different ways.
Ciw handles this by assigning **customer classes** to customers.
In this set-up:

+ Babies are assigned customer :code:`'Class 0'`.
+ Children are assigned customer :code:`'Class 1'`.
+ The receptionist's desk is Node 1.
+ The baby specialist clinic is Node 2.
+ The children's specialist clinic is Node 3.

We assign different behaviour for different customer classes by replacing the values of the keywords of the Network object with dictionaries, with customer classes as keys and the required behaviour as values::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions={'Class 0': [ciw.dists.Exponential(rate=1.0),
    ...                                        ciw.dists.NoArrivals(),
    ...                                        ciw.dists.NoArrivals()],
    ...                            'Class 1': [ciw.dists.Exponential(rate=2.0),
    ...                                        ciw.dists.NoArrivals(),
    ...                                        ciw.dists.NoArrivals()]},
    ...     service_distributions={'Class 0': [ciw.dists.Exponential(rate=4.0),
    ...                                        ciw.dists.Exponential(rate=1.0),
    ...                                        ciw.dists.Deterministic(value=0.0)],
    ...                            'Class 1': [ciw.dists.Exponential(rate=6.0),
    ...                                        ciw.dists.Deterministic(value=0.0),
    ...                                        ciw.dists.Exponential(rate=1.0)]},
    ...     routing={'Class 0': [[0.0, 1.0, 0.0],
    ...                          [0.0, 0.0, 0.0],
    ...                          [0.0, 0.0, 0.0]],
    ...              'Class 1': [[0.0, 0.0, 1.0],
    ...                          [0.0, 0.0, 0.0],
    ...                          [0.0, 0.0, 0.0]]}, 
    ...     number_of_servers=[1, 2, 3],
    ... )

Notice that where we know certain customer classes will not require a service (for example babies will never require service at the children's specialist: Class 0 customers will never require service at Node 3) we are still required to input a service distribution. We choose the dummy distribution :code:`ciw.dists.Deterministic(0.0)`.

Let's simulate this clinic for 9 hours::

    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(9)
    >>> recs = Q.get_all_records()

Now we should see that no customer of Class 0 ever reached Node 3; and no customer of Class 1 ever reached Node 2::

    >>> visited_by_babies = {1, 2}
    >>> set([r.node for r in recs if r.customer_class==0]) == visited_by_babies
    True

    >>> visited_by_children = {1, 3}
    >>> set([r.node for r in recs if r.customer_class==1]) == visited_by_children
    True

Now say we'd like to find the average waiting time at the reception, baby specialist's clinic, and children's specialist's clinic. We'll simulate for 24 hours, using 3 hour warm-up and 3 hour cool-down, for 16 trials. Let's collect the average waiting times for each class at each node every time::

    >>> average_waits_1_babies = []
    >>> average_waits_1_children = []
    >>> average_waits_2 = []
    >>> average_waits_3 = []
    >>> for trial in range(16):
    ...     ciw.seed(trial)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(30)
    ...     recs = Q.get_all_records()
    ...     waits1_babies = [r.waiting_time for r in recs if r.node==1 and r.arrival_date > 3 and r.arrival_date < 27 and r.customer_class == 0]
    ...     waits1_children = [r.waiting_time for r in recs if r.node==1 and r.arrival_date > 3 and r.arrival_date < 27 and r.customer_class == 1]
    ...     waits2 = [r.waiting_time for r in recs if r.node==2 and r.arrival_date > 3 and r.arrival_date < 27]
    ...     waits3 = [r.waiting_time for r in recs if r.node==3 and r.arrival_date > 3 and r.arrival_date < 27]
    ...     average_waits_1_babies.append(sum(waits1_babies) / len(waits1_babies))
    ...     average_waits_1_children.append(sum(waits1_children) / len(waits1_children))
    ...     average_waits_2.append(sum(waits2) / len(waits2))
    ...     average_waits_3.append(sum(waits3) / len(waits3))

Now we can find the average wait over the trials::

    >>> sum(average_waits_1_babies) / len(average_waits_1_babies)
    0.298488...

    >>> sum(average_waits_1_children) / len(average_waits_1_children)
    0.261834...

    >>> sum(average_waits_2) / len(average_waits_2)
    0.268752...

    >>> sum(average_waits_3) / len(average_waits_3)
    0.284763...

These results imply that on average babies wait 0.298488 + 0.268752 = 0.567 of an hour, around 34 minutes for an appointment.
This could then be used as a baseline measure against which to compare potential reconfigurations of the clinic.