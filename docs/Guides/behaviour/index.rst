.. _behaviour-nodes:

================================
How to Get More Custom Behaviour
================================

Custom behaviour can be obtained by writing new :code:`Node`, :code:`ArrivalNode`, :code:`Individual`, and/or :code:`Server` classes, that inherit from the original :code:`ciw.Node`, :code:`ciw.ArrivalNode`, :code:`ciw.Individual` and :code:`ciw.Server` classes respectively, that introduce new beahviour into the system.
The classes that can be overwitten are:

- :code:`Node`: the main node class used to represent a service centre.
- :code:`ArrivalNode`: the node class used to generate individuals and route them to a specific :code:`Node`.
- :code:`Individual`: the individual class used to represent the individual entities.
- :code:`Server`: the class used to represent the servers that sit at a service centre.

These new classes can be used with the Simulation class by using the keyword arugments :code:`node_class`, :code:`arrival_node_class`, :code:`individual_class`, and :code:`server_class`.
These arguments take a class (not an instance of a class), to use throughout the whole simulation.
The argument :code:`node_class` can also take a list of classes, indicating which node class to use on each node of the network. This allows for different nodes to exhibit very different behaviours to one another.


Library of Examples
-------------------

Here's a library of examples of this functionality:

.. toctree::
   :maxdepth: 1
   
   custom_routing.rst
   custom_arrivals.rst
   custom_number_servers.rst
   ps_routing.rst
   server_dependent_dist.rst
   hybrid.rst
