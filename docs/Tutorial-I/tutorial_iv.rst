.. _tutorial-iv:

========================================
Tutorial IV: Trials, Warm-up & Cool-down
========================================

In Tutorials I-III we investigated one run of a simulation of a bank.
Before we draw any conclusions about the behaviour of the bank, there are three things we should consider:

1. Our original description of the bank described it as open 24/7. This means the bank would never start from an empty state, as our simulation does.
2. Those customers left inside the system at the end of the run: their records were not collected, despite spending time in the system during the observation period.
3. Does that single run of our simulation really reflect reality? Were our results simply a fluke? An extreme case?

These three concerns can be addressed with warm-up, cool-down, and trials respectively.
A full explanation of these can be found :ref:`here <simulation-practice>`.

1. **Warm-up:** Simulate the system for some time before the beginning of the observation period, such that the system is non-empty and 'in the swing of it' by the time the observation period begins. Only collect results from the beginning of the observation period.
2. **Cool-down:** Simulate the system for some time after the end of the observation period, such that no concerned customers are stuck in the simulation when results collection happens. Only collect results until the end of the observation period.
3. **Trials:** Simulate the system many times with different random number streams (different :ref:`seeds <set-seed>`). Keep all interested results from all trials, so that we may take averages and confidence intervals.

Let's define our bank by creating our Network object::

    >>> import ciw
    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=0.2)],
    ...     service_distributions=[ciw.dists.Exponential(rate=0.1)],
    ...     number_of_servers=[3]
    ... )

For simplicity, we will be concerned with finding the mean waiting time only.
We'll run 10 simulations in a loop, and take a warm-up time and a cool-down time of 100 time units.
Therefore each trial we will run for 1 day + 200 minutes (1640 minutes)::

    >>> average_waits = []
    >>> for trial in range(10):
    ...     ciw.seed(trial)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(1640)
    ...     recs = Q.get_all_records()
    ...     waits = [r.waiting_time for r in recs if r.arrival_date > 100 and r.arrival_date < 1540]
    ...     mean_wait = sum(waits) / len(waits)
    ...     average_waits.append(mean_wait)

The list :code:`average_waits` will now contain ten numbers, the mean waiting time from each of the trials.
Notice that we set a different seed every time, so each trial will yield different results::

    >>> average_waits
    [3.91950..., 4.34163..., 4.61779..., 5.33537..., 5.06224..., 2.90274..., 4.93209..., 17.95093128538666, 4.06136..., 3.14126...]

We can see that the range of waits are quite high, between 1.6 and 7.5.
This shows that running a single trial wouldn't have given us a very confident answer.
We can take the mean result over the trials to get a more confident answer::

    >>> sum(average_waits) / len(average_waits)
    5.62649...

Using Ciw, we have found that on average customers wait 5.62 minutes in the queue at the bank.
What would happen if we added an extra server?
Let's repeat the analysis with 4 servers::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=0.2)],
    ...     service_distributions=[ciw.dists.Exponential(rate=0.1)],
    ...     number_of_servers=[4]
    ... )

    >>> average_waits = []
    >>> for trial in range(10):
    ...     ciw.seed(trial)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(1640)
    ...     recs = Q.get_all_records()
    ...     waits = [r.waiting_time for r in recs if r.arrival_date > 100 and r.arrival_date < 1540]
    ...     mean_wait = sum(waits) / len(waits)
    ...     average_waits.append(mean_wait)

    >>> sum(average_waits) / len(average_waits)
    0.79868...

By adding an extra server, we can reduce waits from an average 5.62 minutes to 0.79 minutes!
Well done, you have just run your first what-if scenario!
What-if scenarios allow us to use simulation to see if expensive changes to the system are beneficial, without actually implementing those expensive changes.
