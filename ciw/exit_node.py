from __future__ import division

class ExitNode(object):
    """
    Class for the exit node on our network
    """
    def __init__(self):
        """
        Initialise a node.
        """
        self.all_individuals = []
        self.id_number = -1
        self.next_event_date = float("Inf")
        self.node_capacity = float("Inf")

    def __repr__(self):
        """
        Representation of a node.
        """
        return 'Exit Node'

    def accept(self, next_individual, current_time):
        """
        Adds customer to the list of completed customers
        """
        self.all_individuals.append(next_individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node
        Just passes as next_event_date always set to
        the max_simulation_time
        """
        pass
