from __future__ import division

class ExitNode:
    """
    Class for the exit node on our network
    """
    def __init__(self, max_simulation_time):
        """
        Initialise a node.
        """
        self.individuals = []
        self.id_number = -1
        self.next_event_date = max_simulation_time
        self.node_capacity = "Inf"

    def __repr__(self):
        """
        Representation of a node::
        """
        return 'Exit Node'

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue
        """
        self.individuals.append(next_individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node
        """
        pass