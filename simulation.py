"""
A simulation of a Qing networ
"""
from random import random

class Node:
    """
    Class for a node on our network
    """
    def __init__(self, lmbda, mu, c, transition_matrix_row, id_number, simulation):
        """
        Initialise a node.

        Here is an example::

            >>> N = Node(5, 10, 1, [.2, .5], 1, False)
            >>> N.lmbda
            5
            >>> N.mu
            10
            >>> N.c
            1
            >>> N.transition_row
            [0.2, 0.5]
            >>> N.next_event_time
            0
            >>> N.individuals
            []
            >>> N.id_number
            1
        """
        self.lmbda = lmbda
        self.mu = mu
        self.c = c
        self.transition_row = transition_matrix_row
        self.next_event_time = 0
        self.individuals = []
        self.id_number = id_number
        sum_p = 0
        cum_transition_row = []
        for p in self.transition_row:
            sum_p += p
            cum_transition_row.append(sum_p)
        self.cum_transition_row = cum_transition_row


    def __repr__(self):
        """
        Representation of a node::

            >>> N = Node(5, 10, 1, [.2, .5], 1, False)
            >>> N.id_number
            1
        """
        return 'Node %s' % self.id_number

    def have_event(self):
        """
        Update node when a service happens.
        """
        self.individuals.sort(key=lambda x: x.end_service_date)
        next_individual = self.individuals.pop(0)
        next_node = self.next_node()
        next_node.accept(next_individual)
        self.update_next_event_date()

    def accept(self, next_individual):
        """
        Accepts a new customer to the queue

            >>> N = Node(5, 10, 1, [.2, .5], 1, False)
            >>> next_individual = 1
            >>> N.accept(next_individual)
            >>> N.individuals
            [1]
        """
        self.individuals.append(next_individual)

    def update_next_event_date(self):
        pass

    def next_node(self):
        """
        Finds the next node according the random distribution.
        """
        rnd_num = random.random()
        for p in range(len(cum_transition_row)):
            if rnd_num < cum_transition_row[p]:
                return self.simulation.nodes[p]
        return self.simulation.nodes[p]





class Simulation:
    """
    Overall simulation class
    """
    def __init__(self, lmbda, mu, c, transition_matrix):
        """
        Initialise a queue instance.

        Here is an example::

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]])
            >>> Q.lmbda
            [5, 3]
            >>> Q.mu
            [10, 10]
            >>> Q.c
            [1, 1]
            >>> Q.transition_matrix
            [[0.2, 0.5], [0.4, 0.4]]
            >>> Q.nodes
            [Node 1, Node 2]
        """
        self.lmbda = lmbda
        self.mu = mu
        self.c = c
        self.transition_matrix = transition_matrix
        self.nodes = [Node(self.lmbda[i], self.mu[i], self.c[i], self.transition_matrix[i], i + 1, self) for i in range(len(self.lmbda))]

    def find_next_active_node(self):
        """
        Return the next active node:

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]])
            >>> i = 0
            >>> for node in Q.nodes:
            ...     node.next_active_time = i
            ...     i += 1
            >>> Q.find_next_active_node()
            Node 1

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]])
            >>> i = 0
            >>> for node in Q.nodes:
            ...     node.next_active_time = i
            ...     i -= 1
            >>> Q.find_next_active_node()
            Node 2
        """
        return min(self.nodes, key=lambda x: x.next_active_time)

    def simulate(self, max_simulation_time):
        """
        Run the actual simulation.

        NEEDS DOCTESTS OR EVERYTHING WILL BE TERRIBLE.
        """
        next_active_node = find_next_active_node()
        while next_active_node.next_event_time < max_simulation_time:
            next_active_node.have_event()
            next_active_node = find_next_active_node()
