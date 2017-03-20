.. _tutorial-i:

===========================================
Tutorial I: Defining & Running a Simulation
===========================================

Imagine a bank. The bank is open twenty four hours a day, seven days a week. Customers arrive randomly, roughly twelve per hour, regardless of the time of day. Service time is random, but on average lasts roughly ten minutes. The bank is open twenty four hours a day, seven days a week, and has three servers who are always on duty If all servers are busy, newly arriving customers form a queue and wait for service. On average how long to customers wait?

We can use computer simulation to find out. Here we will simulate this system, that is make the computer pretend customer arrive and get served at the bank. We can then look at all the virtual customers that passed through the bank, and gain an understanding of how that system would behave if it existed in real life.

This is where Ciw comes in. Let's import Ciw::

    >>> import ciw

Now we need to tell Ciw what our system looks and behaves like. We do this using a *parameters dictionary*. A paremeters dictionary must contain the following information about the system:

+ Number of servers (:code:`Number_of_servers`)
   + How many servers are on duty at the bank.
   + In this case, 3 servers.

+ Distribution of inter-arrival times (:code:`Arrival_distributions`)
   + The distribution of times between arrivals.
   + In this case 12 per hour would mean an average of 5 mins between arrivals.

+ Distribution of service times (:code:`Service_distributions`)
   + The distribution of times spent in service with a server.
   + In this case an average of 10 mins.

+ A transition matrix (:code:`Transition_matrices`)
   + This will be discussed more in :ref:`Tutorial V <tutorial-v>`.
   + For now, we will input :code:`[[0.0]]`, implying one node with no customers rejoining the queue.

The *parameters dictionary* is a Python dictionary containing this information. For our bank system, write out the dictionary below::

    >>> params = {
    ... 'Arrival_distributions': [['Exponential', 0.2]],
    ... 'Service_distributions': [['Exponential', 0.1]],
    ... 'Transition_matrices': [[0.0]],
    ... 'Number_of_servers': [3]
    ... }

This dictionary fully defines out bank. Notice the distributions; :code:`'Exponential'` here means the inter-arrival and service times are derived from an `exponential distribution <https://en.wikipedia.org/wiki/Exponential_distribution>`_. The parameters 0.2 and 0.1 imply an average of 5 and 10 time units respectively. Therefore this parameters dictionary defines our system in minutes.

First we will :ref:`set a seed <set-seed>`, so that your results and our results are identical.

    >>> ciw.seed(1)

Now we will create a :code:`Network` object. This is Ciw's way of organising the information contained in the parameters dictionary::

    >>> N = ciw.create_network(params)

Once we have a :code:`Network` object, we can create a :code:`Simulation` object. This is the engine that will run the simulation:

    >>> Q = ciw.Simulation(N)

Now we are ready to run the simulation. Let's run the simulation for a day of bank time (don't worry, this won't take a day of real time!). As we parametrised the system with time units of minutes, a day will be 1440 time units::

    >>> Q.simulate_until_max_time(1440)

Well done! We've now defined and simulated the bank for a day. In the next tutorial, we will explore the :code:`Simulation` object some more.