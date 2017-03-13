.. _simulation-methods:

=====================
Methods of Simulating
=====================

There are a number of ways to terminate a simulation:

- :ref:`until_maxtime`
- :ref:`until_maxcustomers`
- :ref:`until_deadlock`

.. _until_maxtime:

-------------------------------
:code:`simulate_until_max_time`
-------------------------------

This method simulates the system from an empty system. The simulation terminates once a certain amount of simulation time has passed. The method takes in a :code:`max_simulation_time`::

    params = {
        'Arrival_distributions': [['Exponential', 1.0]],
        'Service_distributions': [['Exponential', 0.5]],
        'Number_of_servers': [1],
        'Transition_matrices': [[0.0]],
        'Queue_capacities': [3]
    }
    N = ciw.create_network(params)
    Q = ciw.Simulation(N)

    Q.simulate_until_max_time(100)

Keyword arguments:
 - :code:`max_simulation_time`: REQUIRED. Length of simulation time to run the simulation for.
 - :code:`progress_bar`: OPTIONAL. See :ref:`progress-bars`.



.. _until_maxcustomers:

------------------------------------
:code:`simulate_until_max_customers`
------------------------------------

This method simulates the system from an empty system. The simulation terminates once a certain amount of customers passed through. The method takes in a :code:`max_customers`::

    params = {
        'Arrival_distributions': [['Exponential', 1.0]],
        'Service_distributions': [['Exponential', 0.5]],
        'Number_of_servers': [1],
        'Transition_matrices': [[0.0]],
        'Queue_capacities': [3]
    }
    N = ciw.create_network(params)
    Q = ciw.Simulation(N)

    Q.simulate_until_max_customers(20, method='Finish')

There are three methods of simulating for a maximum number of customers, specified by the :code:`method` keyword argument:
 - Finish: Simulates until :code:`max_customers` has reached the Exit Node.
 - Arrive: Simulates until :code:`max_customers` have spawned at the Arrival Node.
 - Accept: Simulates until :code:`max_customers` have been spawned and accepted (not rejected) at the Arrival Node.

Keyword arguments:
 - :code:`max_customers`: REQUIRED. The maximum number of customers.
 - :code:`method`: OPTIONAL. The method which customers are counted. Default method is 'Finish'.
 - :code:`progress_bar`: OPTIONAL. See :ref:`progress-bars`.


.. _until_deadlock:

-------------------------------
:code:`simulate_until_deadlock`
-------------------------------

Simulated until the system reaches deadlock. Please see: :ref:`deadlock-detection`.