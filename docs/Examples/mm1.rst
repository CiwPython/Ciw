.. _m-m-1:

==============================
Example - Simulate M/M/1 Queue
==============================

Here, an example of an M/M/1 queue will be given, and results compared to to those obtained using standard queueing theory.
This will walk through an example of an M/M/1 queue with Poisson arrivals of rate 3 and Exponential service times of rate 5.

Standard queueing theory gives the expected wait in an M/M/1 queue as :math:`\mathbb{E}[W] = \frac{\rho}{\mu(1-\rho)}`. With arrival rate :math:`\lambda = 3` and service rate :math:`\mu = 5`, we get traffic intensity :math:`\rho = \frac{\lambda}{\mu} = 0.6`, and so :math:`\mathbb{E}[W] = 0.3`.

We set up the parameters in Ciw::

    >>> params_dict = {'Arrival_distributions': {'Class 0': [['Exponential', 3.0]]},
    ...                'Service_distributions': {'Class 0': [['Exponential', 5.0]]},
    ...                'Transition_matrices': {'Class 0': [[0.0]]},
    ...                'Number_of_servers': [1]
    ...                }

The following code repeats the experiment 100 times, only recording waits for those that arrived after a warm-up time of 50.
It then returns the average wait in the system::
    
    >>> import ciw
    >>> def iteration(warmup):
    ...     N = ciw.create_network(params_dict)
    ...     Q = ciw.Simulation(N)
    ...     Q.simulate_until_max_time(250)
    ...     records = Q.get_all_records()
    ...     waits = [row.waiting_time for row in records if row.arrival_date > warmup]
    ...     return sum(waits)/len(waits)
    
    >>> ciw.seed(27)
    >>> ws = []
    >>> for i in range(100):
    ...     ws.append(iteration(50))
    
    >>> average_waits = sum(ws)/len(ws)
    >>> print(round(average_waits, 10))
    0.3030117024

We see that the results of the simulation are in agreement with those of standard queueing theory.
