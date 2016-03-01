from __future__ import division

class StateTracker:
    """
    A generic class to record system's state
    """
    def __init__(self, simulation):
        """
        Initialises the state tracker class
        """
        self.simulation = simulation
        self.state = None

    def change_state_accept(self, node_id, cust_cls):
        """
        Changes the state of the system when a customer is accepted.
        """
        pass

    def change_state_block(self, node_id, cust_cls):
        """
        Changes the state of the system when a customer gets blocked.
        """
        pass

    def change_state_release(self, node_id, cust_cls, blocked):
        """
        Changes the state of the system when a customer gets blocked.
        """
        pass

    def hash_state(self):
        """
        Returns a hashable state
        """
        return None


class NaiveTracker(StateTracker):
    """
    The naive tracker simple records the number of customers at each
    node, and how many of those customers are currently blocked.

    Example:
        ((3, 0), (1, 4))
        This denotes 3 customers at the first node, 0 of which are blocked,
        5 customers at the second node, 4 of which are blocked.
    """
    def __init__(self, simulation):
        """
        Initialises the naive tracker class
        """
        self.simulation = simulation
        self.state = [[0, 0] for i in xrange(self.simulation.number_of_nodes)]

    def change_state_accept(self, node_id, cust_cls):
        """
        Changes the state of the system when a customer gets blocked.
        """
        self.state[node_id-1][0] += 1

    def change_state_block(self, node_id, cust_cls):
        """
        Changes the state of the system when a customer gets blocked.
        """
        self.state[node_id-1][1] += 1
        self.state[node_id-1][0] -= 1

    def change_state_release(self, node_id, cust_cls, blocked):
        """
        Changes the state of the system when a customer gets blocked.
        """
        if blocked:
            self.state[node_id-1][1] -= 1
        else:
            self.state[node_id-1][0] -= 1

    def hash_state(self):
        """
        Returns a hashable state
        """
        return tuple(tuple(obs) for obs in self.state)
