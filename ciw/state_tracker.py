from __future__ import division

class StateTracker(object):
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

    def change_state_block(self, node_id, destination, cust_cls):
        """
        Changes the state of the system when a customer gets blocked.
        """
        pass

    def change_state_release(self, node_id, destination,
        cust_cls, blocked):
        """
        Changes the state of the system when a customer is released.
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
        This denotes 3 customers at the first node, 0 of which
        are blocked, 5 customers at the second node, 4 of which
        are blocked.
    """
    def __init__(self, simulation):
        """
        Initialises the naive tracker class
        """
        self.simulation = simulation
        self.state = [[0, 0] for i in range(
            self.simulation.network.number_of_nodes)]

    def change_state_accept(self, node_id, cust_cls):
        """
        Changes the state of the system when a customer is accepted.
        """
        self.state[node_id-1][0] += 1

    def change_state_block(self, node_id, destination, cust_cls):
        """
        Changes the state of the system when a customer gets blocked.
        """
        self.state[node_id-1][1] += 1
        self.state[node_id-1][0] -= 1

    def change_state_release(self, node_id, destination,
        cust_cls, blocked):
        """
        Changes the state of the system when a customer is released.
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


class MatrixTracker(StateTracker):
    """
    The matrix tracker records the order and destination of
    blockages in the form of a matrix. Alongside this the number
    of customers at each node is tracked.

    Example:
        ((((1, 4), (2)),
           (3),    ())),
           (5, 8))
        This denotes 5 customers at the first node 8 customer at
        the second; 2 customer blocked from the first node to the
        first, one from the first node to the second, and on from
        the second node to the first. The numbers denote the order
        at which they became blocked.
    """
    def __init__(self, simulation):
        """
        Initialises the naive tracker class
        """
        self.simulation = simulation
        self.state = [[[[] for i in range(
            self.simulation.network.number_of_nodes)] for i in range(
            self.simulation.network.number_of_nodes)], [0 for i in range(
            self.simulation.network.number_of_nodes)]]
        self.increment = 1

    def change_state_accept(self, node_id, cust_cls):
        """
        Changes the state of the system when a customer is accepted.
        """
        self.state[-1][node_id-1] += 1

    def change_state_block(self, node_id, destination, cust_cls):
        """
        Changes the state of the system when a customer gets blocked.
        """
        self.state[0][node_id-1][destination-1].append(self.increment)
        self.increment += 1

    def change_state_release(self, node_id, destination,
        cust_cls, blocked):
        """
        Changes the state of the system when a customer is released.
        """
        if blocked:
            self.state[-1][node_id-1] -= 1
            self.increment -= 1
            position = self.find_blocked_position_and_pop(
                node_id, destination)
            self.adjust_positions(position)
        else:
            self.state[-1][node_id-1] -= 1

    def find_blocked_position_and_pop(self, node_id, destination):
        """
        Finds the position of the next customer to unblock
        """
        position = self.state[0][node_id-1][destination-1].pop(0)
        return position

    def adjust_positions(self, position):
        """
        Loops through whole matrix, reducing any
        positions > position by 1
        """
        for r in range(len(self.state[0])):
            for c in range(len(self.state[0][r])):
                for o in range(len(self.state[0][r][c])):
                    if self.state[0][r][c][o] > position:
                        self.state[0][r][c][o] -= 1

    def hash_state(self):
        """
        Returns a hashable state
        """
        naive = tuple(self.state[-1])
        matrix = tuple(tuple(tuple(obs for obs in col)
            for col in row) for row in self.state[0])
        return (matrix, naive)
