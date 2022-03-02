.. _pause-restart:

=======================================
How to Pause and Restart the Simulation
=======================================

Ciw has the capability to pause and restart the simulation. This is done by
running the simulation for an initial period of time, and then rerunning it with
the remaining amount of time. The following code runs the simulation for 5 time
units::

    >>> import ciw
    >>> N = ciw.create_network(
    ...      arrival_distributions=[ciw.dists.Exponential(rate=1)],
    ...      service_distributions=[ciw.dists.Exponential(rate=2)],
    ...      number_of_servers=[1]
    ... )
    >>> ciw.seed(0)
    >>> Q = ciw.Simulation(N)
    >>> Q.simulate_until_max_time(5)

We can now inspect the simulation at this point, observing the records of the simulation for the first 5 time units::

    >>> import pandas as pd
    >>> columns = ["id_number", "arrival_date", "waiting_time"]
    >>> recs = Q.get_all_records()
    >>> df = pd.DataFrame(recs)
    >>> df[columns]
       id_number  arrival_date  waiting_time
    0          1      1.860607      0.000000
    1          2      2.406320      0.163601
    2          3      2.705963      0.221936
    3          4      3.225046      0.468626

We can now resume the simulation and observe the records for a further 4 time
units. Notice we have already reached time 5, therefore we simulate until 
5 + 4 = 9 time units::

    >>> Q.simulate_until_max_time(9)
    >>> recs = Q.get_all_records()
    >>> df = pd.DataFrame(recs)
    >>> df[columns]
       id_number  arrival_date  waiting_time
    0          1      1.860607      0.000000
    1          2      2.406320      0.163601
    2          3      2.705963      0.221936
    3          4      3.225046      0.468626
    4          5      3.586464      0.545000
    5          6      4.233868      1.091194
    6          7      4.936433      0.870279
    7          8      5.267493      0.683398
    8          9      6.677278      0.476178

Notice that the first four records are exactly the same. That is because they 
are the very same records, they have not been re-simulated.