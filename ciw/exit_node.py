from __future__ import division

class ExitNode(object):
    """
    Class for the exit node on our network.
    """
    def __init__(self):
        """
        Initialise the exit node.
        """
        self.all_individuals = []
        self.number_of_individuals = 0
        self.id_number = -1
        self.next_event_date = float("Inf")
        self.node_capacity = float("Inf")

    def __repr__(self):
        """
        Representation of the exit node.
        """
        return 'Exit Node'

    def accept(self, next_individual):
        """
        Adds individual to the list of completed individuals.
        """
        self.all_individuals.append(next_individual)
        self.number_of_individuals += 1

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node
        Just passes as next_event_date always set to
        the max_simulation_time
        """
        pass
