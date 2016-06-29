.. _new_nodes:

=========================================
Example - Modelling behaviour using nodes
=========================================

As an example of the flexibility of Ciw, you can modify the routing of
individuals by creating new nodes:

- :code:`Node`: the main node class used to represent a service centre.
- :code:`ArrivalNode`: the node class used to generate individuals and route
  them to :code:`Node` s.

Let us consider a situation where individuals will only join and/or rejoin a
single server queue if there are less than a given :code:`threshold` of
individuals already there::

    >>> import ciw
    >>> threshold = 10
    >>> class ThresholdNode(ciw.Node):
    ...    def next_node(self, customer_class):
    ...        """Overwriting the next node method"""
    ...        if self.simulation.nodes[1].number_of_individuals < threshold:
    ...            return self.simulation.nodes[1]
    ...        return self.simulation.nodes[-1]

    >>> class ThresholdArrivalNode(ciw.ArrivalNode):
    ...     def release_individual(self, next_node, next_individual):
    ...         """Overwriting the release individual method"""
    ...         if self.simulation.nodes[1].number_of_individuals < threshold:
    ...             self.send_individual(next_node, next_individual)
    ...         else:
    ...             self.record_rejection(next_node)

We can use these new nodes to build our simulation::

    >>> params = {
    ...  'Arrival_distributions': [['Exponential', 5.0]],
    ...  'Service_distributions': [['Exponential', 10.0]],
    ...  'Transition_matrices': [[0.5]],
    ...  'Number_of_servers': [1]
    ...  }

Let us compare the maximum number of individuals in the queue at any given
point in time for a simulation using these nodes and one using the default ones::

    >>> network = ciw.create_network(params)

    >>> default_Q = ciw.Simulation(network)
    >>> default_Q.simulate_until_max_time(1000)
    >>> default_recs = default_Q.get_all_records()
    >>> default_max_length = max([row.queue_size_at_arrival for row in default_recs] +
    ...                          [row.queue_size_at_departure for row in default_recs])
    >>> default_max_length  # doctest: +SKIP
    108


    >>> threshold_Q = ciw.Simulation(network,
    ...                              node_class=ThresholdNode,
    ...                              arrival_node_class=ThresholdArrivalNode)
    >>> threshold_Q.simulate_until_max_time(1000)
    >>> threshold_recs = threshold_Q.get_all_records()
    >>> threshold_max_length = max([row.queue_size_at_arrival for row in threshold_recs] +
    ...                            [row.queue_size_at_departure for row in threshold_recs])
    >>> threshold_max_length
    9

    >>> threshold_max_length <= default_max_length
    True
