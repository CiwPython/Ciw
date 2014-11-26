"""
A simulation of a Qing networ
"""
from random import random, seed, expovariate

class Individual:
    """
    Class for an individual
    """
    def __init__(self, id_number):
        """
        Initialise an individual

        >>> i = Individual(22)
        >>> i.in_service
        False
        >>> i.end_service_date
        False
        >>> i.id_number
        22
        """
        self.in_service = False
        self.end_service_date = False
        self.id_number = id_number

    def __repr__(self):
        """
        >>> i = Individual(3)
        >>> i
        Individual 3
        """
        return 'Individual %s' % self.id_number

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

        Here is another example::

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> N = Q.transitive_nodes[0]
            >>> N.next_event_time
            50

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
        self.cum_transition_row = cum_transition_row  # Adding zero for countability (represents never going back to arrival node)
        self.simulation = simulation
        if self.simulation:
            self.next_event_time = self.simulation.max_simulation_time


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

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> N = Q.transitive_nodes[0]
            >>> i = Individual(2)
            >>> N.accept(i, 1)
            >>> N.have_event()
        """
        self.individuals.sort(key=lambda x: x.end_service_date)
        next_individual = self.individuals.pop(0)
        next_node = self.next_node()
        next_node.accept(next_individual, self.next_event_time)
        self.update_next_event_date()

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

            >>> seed(1)
            >>> N = Node(5, 10, 1, [.2, .5], 1, False)
            >>> next_individual = Individual(5)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]

            >>> N.next_event_time
            1.014429106410951
            >>> N.accept(Individual(10), 1)
            >>> N.next_event_time
            1.014429106410951
        """
        if len(self.individuals) <= self.c:
            next_individual.end_service_date = current_time + expovariate(self.mu)
        else:
            self.individuals.sort(key=lambda x: x.end_service_date)
            next_individual.end_service_date = self.individuals[-self.c].end_service_date + expovariate(self.mu)
        self.individuals.append(next_individual)
        self.update_next_event_date()

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals
            []
            >>> node.next_event_time
            50
            >>> node.update_next_event_date()
            >>> node.next_event_time
            50
            >>> ind = Individual(10)
            >>> node.accept(ind, 1)
            >>> node.update_next_event_date()
            >>> node.next_event_time
            1.014429106410951
        """
        if len(self.individuals) == 0:
            self.next_event_time = self.simulation.max_simulation_time
        else:
            self.individuals.sort(key=lambda x: x.end_service_date)
            self.next_event_time = self.individuals[0].end_service_date

    def next_node(self):
        """
        Finds the next node according the random distribution.

            >>> seed(6)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.35, .35], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.next_node()
            Exit Node
            >>> node.next_node()
            Exit Node
            >>> node.next_node()
            Node 2
            >>> node.next_node()
            Node 1
            >>> node.next_node()
            Node 1
            >>> node.next_node()
            Node 2
        """
        rnd_num = random()
        for p in range(len(self.cum_transition_row)):
            if rnd_num < self.cum_transition_row[p]:
                return self.simulation.transitive_nodes[p]
        return self.simulation.nodes[-1]

class ArrivalNode:
    """
    Class for the arrival node on our network
    """
    def __init__(self, lmbda, transition_row, simulation):
        """
        Initialise a node.

        Here is an example::

            >>> N = ArrivalNode(5, [.5, .5], False)
            >>> N.lmbda
            5
            >>> N.transition_row
            [0.5, 0.5]
            >>> sum(N.transition_row)
            1.0
            >>> N.next_event_time
            0
            >>> N.number_of_individuals
            0
        """
        self.lmbda = lmbda
        self.transition_row = transition_row
        self.next_event_time = 0
        self.number_of_individuals = 0
        sum_p = 0
        cum_transition_row = []
        for p in self.transition_row:
            sum_p += p
            cum_transition_row.append(sum_p)
        self.cum_transition_row = cum_transition_row
        self.simulation = simulation

    def __repr__(self):
        """
        Representation of a node::

            >>> N = ArrivalNode(5, [.5, .5], False)
            >>> N
            Arrival Node
        """
        return 'Arrival Node'

    def have_event(self):
        """
        Update node when a service happens.

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> N = ArrivalNode(8, [.625, .375], Q)
            >>> N.next_event_time
            0
            >>> N.have_event()
            >>> Q.transitive_nodes[0].individuals
            [Individual 1]
            >>> Q.transitive_nodes[1].individuals
            []
            >>> round(N.next_event_time,5)
            0.18037
        """
        self.number_of_individuals += 1
        next_individual = Individual(self.number_of_individuals)
        next_node = self.next_node()
        next_node.accept(next_individual, self.next_event_time)
        self.update_next_event_date()

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> N = ArrivalNode(8, [.625, .375], Q)
            >>> N.next_event_time
            0
            >>> N.update_next_event_date()
            >>> round(N.next_event_time, 5)
            0.01804
        """
        self.next_event_time += expovariate(self.lmbda)

    def next_node(self):
        """
        Finds the next node according the random distribution.

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> N = ArrivalNode(8, [.625, .375], Q)
            >>> N.next_node()
            Node 1
            >>> N.next_node()
            Node 2
            >>> N.next_node()
            Node 2
        """
        rnd_num = random()
        for p in range(len(self.cum_transition_row)):
            if rnd_num < self.cum_transition_row[p]:
                return self.simulation.transitive_nodes[p]

class ExitNode:
    """
    Class for the exit node on our network
    """
    def __init__(self):
        """
        Initialise a node.

        Here is an example::

            >>> N = ExitNode()
            >>> N.individuals
            []
            >>> N.id_number
            -1
            >>> N.next_event_time
            False
        """
        self.individuals = []
        self.id_number = -1
        self.next_event_time = False


    def __repr__(self):
        """
        Representation of a node::

            >>> N = ExitNode()
            >>> N
            Exit Node
        """
        return 'Exit Node'

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

            >>> N = ExitNode()
            >>> N.individuals
            []
            >>> N.next_event_time
            False
            >>> next_individual = Individual(5)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]
            >>> N.next_event_time
            False
        """
        self.individuals.append(next_individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            >>> N = ExitNode()
            >>> N.next_event_time
            False
            >>> N.update_next_event_date()
            >>> N.next_event_time
            False

        """
        pass


class Simulation:
    """
    Overall simulation class
    """
    def __init__(self, lmbda, mu, c, transition_matrix, max_simulation_time):
        """
        Initialise a queue instance.

        Here is an example::

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> Q.lmbda
            [5, 3]
            >>> Q.mu
            [10, 10]
            >>> Q.c
            [1, 1]
            >>> Q.transition_matrix
            [[0.2, 0.5], [0.4, 0.4]]
            >>> Q.nodes
            [Arrival Node, Node 1, Node 2, Exit Node]
            >>> Q.transitive_nodes
            [Node 1, Node 2]
            >>> Q.max_simulation_time
            50
        """
        self.lmbda = lmbda
        self.mu = mu
        self.c = c
        self.transition_matrix = transition_matrix
        self.max_simulation_time = max_simulation_time
        self.transitive_nodes = [Node(self.lmbda[i], self.mu[i], self.c[i], self.transition_matrix[i], i + 1, self) for i in range(len(self.lmbda))]
        self.nodes = [ArrivalNode(sum(lmbda), [l/sum(lmbda) for l in lmbda], self)] + self.transitive_nodes + [ExitNode()]

    def find_next_active_node(self):
        """
        Return the next active node:

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> i = 0
            >>> for node in Q.nodes:
            ...     node.next_event_time = i
            ...     i += 1
            >>> Q.find_next_active_node()
            Node 1

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> i = 0
            >>> for node in Q.nodes:
            ...     node.next_event_time = i
            ...     i -= 1
            >>> Q.find_next_active_node()
            Node 2
        """
        return min(self.nodes, key=lambda x: x.next_event_time)

    def simulate(self):
        """
        Run the actual simulation.

        NEEDS DOCTESTS OR EVERYTHING WILL BE TERRIBLE.
        """
        next_active_node = find_next_active_node()
        while next_active_node.next_event_time < self.max_simulation_time:
            next_active_node.have_event()
            next_active_node = find_next_active_node()
