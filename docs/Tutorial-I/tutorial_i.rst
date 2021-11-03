.. _tutorial-i:

===========================================
Tutorial I: Defining & Running a Simulation
===========================================

Assume you are a bank manager and would like to know how long customers wait in your bank.
Customers arrive randomly, roughly 12 per hour, regardless of the time of day.
Service time is random, but on average lasts roughly 10 minutes.
The bank is open 24 hours a day, 7 days a week, and has three servers who are always on duty.
If all servers are busy, newly arriving customers form a queue and wait for service.
On average how long do customers wait?

We can use computer simulation to find out.
Here we will simulate this system, that is make the computer pretend customers arrive and get served at the bank.
We can then look at all the virtual customers that passed through the bank, and gain an understanding of how that system would behave if it existed in real life.

This is where Ciw comes in.
Let's import Ciw::

    >>> import ciw

Now we need to tell Ciw what our system looks like and how it behaves.
We do this by creating a Network object.
It takes in keywords containing the following information about the system:

+ Number of servers (:code:`number_of_servers`)
   + How many servers are on duty at the bank.
   + In this case, 3 servers.

+ Distribution of inter-arrival times (:code:`arrival_distributions`)
   + The distribution of times between arrivals.
   + In this case 12 per hour would mean an average of 5 mins between arrivals.

+ Distribution of service times (:code:`service_distributions`)
   + The distribution of times spent in service with a server.
   + In this case an average of 10 mins.

For our bank system, create the Network::

    >>> N = ciw.create_network(
    ...     arrival_distributions=[ciw.dists.Exponential(rate=0.2)],
    ...     service_distributions=[ciw.dists.Exponential(rate=0.1)],
    ...     number_of_servers=[3]
    ... )

This fully defines our bank.
Notice the distributions; :code:`'Exponential'` here means the inter-arrival and service times are derived from an `exponential distribution <https://en.wikipedia.org/wiki/Exponential_distribution>`_.
The parameters :code:`0.2` and :code:`0.1` imply an average of 5 and 10 time units respectively.
Therefore this Network object defines our system in minutes.

First we will :ref:`set a seed <set-seed>`. This is :ref:`good practice <simulation-practice>`, and also ensures your results and our results are identical.

    >>> ciw.seed(1)

Now we can create a :code:`Simulation` object.
This is the engine that will run the simulation:

    >>> Q = ciw.Simulation(N)

Let's run the simulation for a day of bank time (don't worry, this won't take a day of real time!).
As we parametrised the system with time units of minutes, a day will be 1440 time units::

    >>> Q.simulate_until_max_time(1440)

Well done! We've now defined and simulated the bank for a day.
In the next tutorial, we will explore the :code:`Simulation` object some more.