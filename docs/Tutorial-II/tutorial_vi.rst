.. _tutorial-vi:

================================
Tutorial VI: Restricted Networks
================================

Imagine a manufacturing plant that produces stools:

+ Every 4 seconds a seat arrives on a conveyor-belt.
+ The belt contains three workstations.
+ At the each workstation a leg is connected.
+ Connecting a leg takes a random amount of time between 3 seconds and 5 seconds.
+ Between workstations (and before the first workstation) the conveyor-belt is only long enough to hold 3 stools.
+ If the belt before the first workstation is full then new stools fall to the floor and break.
+ If a stool finishes 'service' at a workstation, but there is no space on the conveyor-belt, that stool must remain at the workstation until room becomes available on the conveyor-belt. While this blockage happens, that workstation cannot begin assembling any more stools. (Full details on blocking available :ref:`here <ciw-mechanisms>`.)

Each broken stool costs the factory 10p in wasted wood.
We wish to know how many stools will fall to the floor and break per hour of operation, and thus the average cost per hour.
First let's define the Network.
A restricted network such as this is represented by nearly the same Network object as an unrestricted network, but we now include the keyword :code:`Queue_capacities`::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Deterministic(value=4.0),
    ...                            ciw.dists.NoArrivals(),
    ...                            ciw.dists.NoArrivals()],
    ...     service_distributions=[ciw.dists.Uniform(lower=3, upper=5),
    ...                            ciw.dists.Uniform(lower=3, upper=5),
    ...                            ciw.dists.Uniform(lower=3, upper=5)],
    ...     routing=[[0.0, 1.0, 0.0],
    ...              [0.0, 0.0, 1.0],
    ...              [0.0, 0.0, 0.0]],
    ...     number_of_servers=[1, 1, 1],
    ...     queue_capacities=[3, 3, 3]
    ... )

The time taken to attach a leg to the stool (service time) is sampled using the uniform distribution.
This samples values equally likely between an upper and lower limit.
Note the time units here are in seconds.

If we simulate this, we have access to information about the blockages, for example the amount of time a stool was spent blocked at each node.
To illustrate, let's simulate for 20 minutes::

    >>> ciw.seed(1)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(1200)
    >>> recs = Q.get_all_records()

    >>> blockages = [r.time_blocked for r in recs]
    >>> max(blockages)
    1.402303...

Here we see that in 20 minutes the maximum time a stool was blocked at a workstation for was 1.4 seconds.

We can get information about the stools that fell off the conveyor-belt using the Simulation's :code:`rejection_dict` attribute.
This is a dictionary, that maps node numbers to dictionaries.
These dictionaries map customer class numbers to a list of dates at which customers where rejected::

    >>> Q.rejection_dict
    {1: {0: [1020.0, 1184.0]}, 2: {0: []}, 3: {0: []}}

In this run 2 stools were rejected (fell to the floor as there was no room on the conveyor-belt) at Node 1, at times 1020 and 1184.
To get the number of stools rejected, take the length of this list::

    >>> len(Q.rejection_dict[1][0])
    2

Now we'll run 8 trials, and get the average number of rejections in an hour.
We will take a warm-up time of 10 minutes.
A cool-down will be unnecessary as we are recording rejections, which happen at the time of arrival::

    >>> broken_stools = []
    >>> for trial in range(8):
    ...     ciw.seed(trial)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(4200)
    ...     num_broken = len([r for r in Q.rejection_dict[1][0] if r > 600])
    ...     broken_stools.append(num_broken)

    >>> broken_stools
    [9, 10, 6, 9, 4, 7, 10, 3]

    >>> sum(broken_stools) / len(broken_stools)
    7.25

On average the system gets 7.25 broken stools per hour; costing and average of 72.5p per hour of operation.

A new stool assembly system, costing £2500, can reduce the variance in the leg assembly time, such that it takes between 3.5 and 4.5 seconds to attach a leg.
How many hours of operation will the manufacturing plant need to run for so that the new system has saved the plant as much money as it costed?

First, under the new system how many broken stools per hour do we expect?::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Deterministic(value=4.0),
    ...                            ciw.dists.NoArrivals(),
    ...                            ciw.dists.NoArrivals()],
    ...     service_distributions=[ciw.dists.Uniform(lower=3.5, upper=4.5),
    ...                            ciw.dists.Uniform(lower=3.5, upper=4.5),
    ...                            ciw.dists.Uniform(lower=3.5, upper=4.5)],
    ...     routing=[[0.0, 1.0, 0.0],
    ...              [0.0, 0.0, 1.0],
    ...              [0.0, 0.0, 0.0]],
    ...     number_of_servers=[1, 1, 1],
    ...     queue_capacities=[3, 3, 3]
    ... )

    >>> broken_stools = []
    >>> for trial in range(8):
    ...     ciw.seed(trial)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(4200)
    ...     num_broken = len([r for r in Q.rejection_dict[1][0] if r > 600])
    ...     broken_stools.append(num_broken)

    >>> sum(broken_stools) / len(broken_stools)
    0.875

Thus the new system saves an average of 6.375 stools per hour, around 63.75p per hour.
Therefore it would take :math:`2500/0.6375 \approx 3921.57` hours of operation for the system to begin paying off.
