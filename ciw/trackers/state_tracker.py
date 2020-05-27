from __future__ import division

class StateTracker(object):
    """
    A generic class to record system's state.
    """
    def initialise(self, simulation):
        """
        Initialises the state tracker class.
        """
        self.simulation = simulation
        self.state = None
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node_id, cust_clss):
        """
        Changes the state of the system when a customer is accepted.
        """
        pass

    def change_state_block(self, node_id, destination, cust_clss):
        """
        Changes the state of the system when a customer gets blocked.
        """
        pass

    def change_state_release(self, node_id, destination, cust_clss, blocked):
        """
        Changes the state of the system when a customer is released.
        """
        pass

    def hash_state(self):
        """
        Returns a hashable state.
        """
        return None

    def timestamp(self):
        current_hash_state = self.hash_state()
        if current_hash_state != self.history[-1][1]:
            self.history.append([self.simulation.current_time, current_hash_state])

    def state_probabilities(self, observation_period=(0, float("Inf"))):
        """
        Get the state probabilities from the history

        Input:
            observation_period: tuple
                A tuple given by the user to identify the observation period 
                that the probabilities will be computed on, by default is from
                0 to infinity
            
        Returns:
            Dictionary of states as keys and probabilities as values
        """
        start = observation_period[0]
        end = observation_period[1]
        steady_state_dictionary = {}
        prev_date = self.history[0][0]    
        prev_state = self.history[0][1]

        if start < 0 or end <= start:
            raise ValueError('Observation period need to be a positive interval above zero')

        for event in self.history:
            date = event[0]
            state = event[1]
            if date > end:
                break
            date_diff = self.simulation.nodes[1].increment_time(date, -max(prev_date, start))
            if start < date < end:
                if (prev_state not in steady_state_dictionary): 
                    steady_state_dictionary[prev_state] = date_diff
                else:
                    steady_state_dictionary[prev_state] += date_diff           
            prev_date = date
            prev_state = state

        if end != float("Inf"):
            date_diff = self.simulation.nodes[1].increment_time(end, -prev_date)
        if (prev_state not in steady_state_dictionary): 
            steady_state_dictionary[prev_state] = date_diff
        else:
            steady_state_dictionary[prev_state] += date_diff  

        tot = sum(steady_state_dictionary.values())
        for state in steady_state_dictionary:
            steady_state_dictionary[state] /= tot
            
        return steady_state_dictionary


class SystemPopulation(StateTracker):
    """
    The system population tracker records the number of customers in the
    system, regaerdless of node.

    Example:
        3
        This denotes 3 customers in the whole system.
    """
    def initialise(self, simulation):
        """
        Initialises the state tracker class.
        """
        self.simulation = simulation
        self.state = 0
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node_id, cust_clss):
        """
        Changes the state of the system when a customer is accepted.
        """
        self.state += 1

    def change_state_block(self, node_id, destination, cust_clss):
        """
        Changes the state of the system when a customer gets blocked.
        """
        pass

    def change_state_release(self, node_id, destination, cust_clss, blocked):
        """
        Changes the state of the system when a customer is released.
        """
        self.state -= 1

    def hash_state(self):
        """
        Returns a hashable state.
        """
        return self.state


class NodePopulation(StateTracker):
    """
    The node population tracker records the number of customers at each node.

    Example:
        (3, 1)
        This denotes 3 customers at the first node, and 1 customer at the
        second node.
    """
    def initialise(self, simulation):
        """
        Initialises the state tracker class.
        """
        self.simulation = simulation
        self.state = [0 for i in range(
            self.simulation.network.number_of_nodes)]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node_id, cust_clss):
        """
        Changes the state of the system when a customer is accepted.
        """
        self.state[node_id-1] += 1

    def change_state_block(self, node_id, destination, cust_clss):
        """
        Changes the state of the system when a customer gets blocked.
        """
        pass

    def change_state_release(self, node_id, destination, cust_clss, blocked):
        """
        Changes the state of the system when a customer is released.
        """
        self.state[node_id-1] -= 1

    def hash_state(self):
        """
        Returns a hashable state.
        """
        return tuple(self.state)


class NodePopulationSubset(StateTracker):
    """
    The node population tracker records the number of customers at each node
    from a given set of observed nodes.

    Example:
        (3, 1)
        This denotes 3 customers at the first node, and 1 customer at the
        second node.
    """
    def __init__(self, observed_nodes):
        """
        Pre-initialises the object with keyward `observed_nodes`
        """
        self.observed_nodes = observed_nodes

    def initialise(self, simulation):
        """
        Initialises the state tracker class.
        """
        self.simulation = simulation
        self.state = [0 for i in self.observed_nodes]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node_id, cust_clss):
        """
        Changes the state of the system when a customer is accepted.
        """
        if node_id-1 in self.observed_nodes:
            state_index = self.observed_nodes.index(node_id-1)
            self.state[state_index] += 1

    def change_state_block(self, node_id, destination, cust_clss):
        """
        Changes the state of the system when a customer gets blocked.
        """
        pass

    def change_state_release(self, node_id, destination, cust_clss, blocked):
        """
        Changes the state of the system when a customer is released.
        """
        if node_id-1 in self.observed_nodes:
            state_index = self.observed_nodes.index(node_id-1)
            self.state[state_index] -= 1

    def hash_state(self):
        """
        Returns a hashable state.
        """
        return tuple(self.state)





class NodeClassMatrix(StateTracker):
    """
    The node-class matrix tracker records the number of customers of each
    class at each node.

    Example:
        ((3, 1),
         (0, 1))
        This denotes 4 customers at the first node (3 of Class 0, 1 of
        Class 0), and 1 customer at the second node (0 of Class 0, 1 of
        Class 1).
    """
    def initialise(self, simulation):
        """
        Initialises the state tracker class.
        """
        self.simulation = simulation
        self.state = [[0 for cls in range(
            self.simulation.network.number_of_classes)] for i in range(
            self.simulation.network.number_of_nodes)]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node_id, cust_clss):
        """
        Changes the state of the system when a customer is accepted.
        """
        self.state[node_id-1][cust_clss] += 1

    def change_state_block(self, node_id, destination, cust_clss):
        """
        Changes the state of the system when a customer gets blocked.
        """
        pass

    def change_state_release(self, node_id, destination, cust_clss, blocked):
        """
        Changes the state of the system when a customer is released.
        """
        self.state[node_id-1][cust_clss] -= 1

    def hash_state(self):
        """
        Returns a hashable state.
        """
        return tuple(tuple(obs) for obs in self.state)


class NaiveBlocking(StateTracker):
    """
    The naive blocking tracker records the number of customers at each node,
    and how many of those customers are currently blocked.

    Example:
        ((3, 0), (1, 4))
        This denotes 3 customers at the first node, 0 of which
        are blocked, 5 customers at the second node, 4 of which
        are blocked.
    """
    def initialise(self, simulation):
        """
        Initialises the naive blocking tracker class.
        """
        self.simulation = simulation
        self.state = [[0, 0] for i in range(
            self.simulation.network.number_of_nodes)]
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node_id, cust_clss):
        """
        Changes the state of the system when a customer is accepted.
        """
        self.state[node_id-1][0] += 1

    def change_state_block(self, node_id, destination, cust_clss):
        """
        Changes the state of the system when a customer gets blocked.
        """
        self.state[node_id-1][1] += 1
        self.state[node_id-1][0] -= 1

    def change_state_release(self, node_id, destination, cust_clss, blocked):
        """
        Changes the state of the system when a customer is released.
        """
        if blocked:
            self.state[node_id-1][1] -= 1
        else:
            self.state[node_id-1][0] -= 1

    def hash_state(self):
        """
        Returns a hashable state.
        """
        return tuple(tuple(obs) for obs in self.state)


class MatrixBlocking(StateTracker):
    """
    The matrix blocking tracker records the order and destination of
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
    def initialise(self, simulation):
        """
        Initialises the matrix blocking tracker class.
        """
        self.simulation = simulation
        self.state = [[[[] for i in range(
            self.simulation.network.number_of_nodes)] for i in range(
            self.simulation.network.number_of_nodes)], [0 for i in range(
            self.simulation.network.number_of_nodes)]]
        self.increment = 1
        self.history = [[self.simulation.current_time, self.hash_state()]]

    def change_state_accept(self, node_id, cust_clss):
        """
        Changes the state of the system when a customer is accepted.
        """
        self.state[-1][node_id-1] += 1

    def change_state_block(self, node_id, destination, cust_clss):
        """
        Changes the state of the system when a customer gets blocked.
        """
        self.state[0][node_id-1][destination-1].append(self.increment)
        self.increment += 1

    def change_state_release(self, node_id, destination, cust_clss, blocked):
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
        Finds the position of the next customer to unblock.
        """
        position = self.state[0][node_id-1][destination-1].pop(0)
        return position

    def adjust_positions(self, position):
        """
        Loops through whole matrix, reducing any
        positions > position by 1.
        """
        for r in range(len(self.state[0])):
            for c in range(len(self.state[0][r])):
                for o in range(len(self.state[0][r][c])):
                    if self.state[0][r][c][o] > position:
                        self.state[0][r][c][o] -= 1

    def hash_state(self):
        """
        Returns a hashable state.
        """
        naive = tuple(self.state[-1])
        matrix = tuple(tuple(tuple(obs for obs in col)
            for col in row) for row in self.state[0])
        return (matrix, naive)
