"""
A simulation of a Qing networ
"""
from __future__ import division
from random import random, seed, expovariate
from numpy import mean

class DataRecord:
    """
    A class for a data record
    """
    def __init__(self, arrival_date, service_time, exit_date, node):
        """

            >>> r = DataRecord(2, 3, 5, 3)
            >>> r.arrival_date
            2
            >>> r.wait
            0
            >>> r.service_date
            2
            >>> r.service_time
            3
            >>> r.exit_date
            5
        """
        self.arrival_date = arrival_date
        self.service_time = service_time
        self.exit_date = exit_date
        self.service_date = exit_date - service_time
        self.wait = self.service_date - arrival_date
        self.node = node

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
        >>> i.data_records
        {}
        """
        self.in_service = False
        self.end_service_date = False
        self.id_number = id_number
        self.data_records = {}

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
            >>> N.cum_transition_row
            [0.2, 0.7]
            >>> N.simulation
            False

        Here is another example::

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> N = Q.transitive_nodes[0]
            >>> N.next_event_time
            50
            >>> N.cum_transition_row
            [0.2, 0.7]
            >>> N.simulation.max_simulation_time
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
            >>> i.arrival_date
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'arrival_date'
            >>> i.service_time
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'service_time'
            >>> N.accept(i, 1)
            >>> i.arrival_date
            1
            >>> round(i.service_time, 5)
            0.01443
            >>> i.data_records[N.id_number]
            Traceback (most recent call last):
            ...
            KeyError: 1
            >>> i.exit_date
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'exit_date'
            >>> N.have_event()
            >>> round(i.exit_date, 5)
            1.01443
            >>> i.data_records[N.id_number][0].wait
            0.0
        """
        self.individuals.sort(key=lambda x: x.end_service_date)
        next_individual = self.individuals.pop(0)

        next_individual.exit_date = self.next_event_time
        self.write_individual_record(next_individual)

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

            >>> next_individual.arrival_date
            1
            >>> round(next_individual.service_time, 5)
            0.01443

            >>> round(N.next_event_time, 5)
            1.01443
            >>> N.accept(Individual(10), 1)
            >>> round(N.next_event_time, 5)
            1.01443
        """
        next_individual.arrival_date = current_time
        next_individual.service_time = expovariate(self.mu)

        if len(self.individuals) < self.c:
            next_individual.end_service_date = current_time + next_individual.service_time
        else:
            self.individuals.sort(key=lambda x: x.end_service_date)
            next_individual.end_service_date = self.individuals[-self.c].end_service_date + next_individual.service_time

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
            >>> round(node.next_event_time, 5)
            1.01443
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

    def write_individual_record(self, individual):
        """
        Write a data record for an individual:

        - Arrival date
        - Wait
        - Service date
        - Service time
        - Exit date

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.35, .35], [.4, .4]], 50)
            >>> N = Q.transitive_nodes[0]
            >>> ind = Individual(6)
            >>> N.accept(ind, 3)
            >>> N.write_individual_record(ind)
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'exit_date'
            >>> ind.exit_date = 7
            >>> N.write_individual_record(ind)
            >>> ind.data_records[1][0].arrival_date
            3
            >>> round(ind.data_records[1][0].wait, 5)
            3.81198
            >>> round(ind.data_records[1][0].service_date, 5)
            6.81198
            >>> round(ind.data_records[1][0].service_time, 5)
            0.18802
            >>> ind.data_records[1][0].exit_date
            7
            >>> ind.data_records[1][0].node
            1

        """
        record = DataRecord(individual.arrival_date, individual.service_time, individual.exit_date, self.id_number)
        if self.id_number in individual.data_records:
            individual.data_records[self.id_number].append(record)
        else:
            individual.data_records[self.id_number] = [record]



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
            >>> N.cum_transition_row
            [0.5, 1.0]
            >>> N.simulation
            False
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
    def __init__(self, max_simulation_time):
        """
        Initialise a node.

        Here is an example::

            >>> N = ExitNode(100)
            >>> N.individuals
            []
            >>> N.id_number
            -1
            >>> N.next_event_time
            100
        """
        self.individuals = []
        self.id_number = -1
        self.next_event_time = max_simulation_time


    def __repr__(self):
        """
        Representation of a node::

            >>> N = ExitNode(500)
            >>> N
            Exit Node
        """
        return 'Exit Node'

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

            >>> N = ExitNode(200)
            >>> N.individuals
            []
            >>> N.next_event_time
            200
            >>> next_individual = Individual(5)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]
            >>> N.next_event_time
            200
        """
        self.individuals.append(next_individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            >>> N = ExitNode(25)
            >>> N.next_event_time
            25
            >>> N.update_next_event_date()
            >>> N.next_event_time
            25

        """
        pass


class Simulation:
    """
    Overall simulation class
    """
    def __init__(self, lmbda, mu, c, transition_matrix, max_simulation_time, warm_up=0):
        """
        Initialise a queue instance.

        Here is an example::

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50, 10)
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
            >>> Q.warm_up
            10
        """
        self.lmbda = lmbda
        self.mu = mu
        self.c = c
        self.transition_matrix = transition_matrix
        self.max_simulation_time = max_simulation_time
        self.warm_up = warm_up
        self.transitive_nodes = [Node(self.lmbda[i], self.mu[i], self.c[i], self.transition_matrix[i], i + 1, self) for i in range(len(self.lmbda))]
        self.nodes = [ArrivalNode(sum(lmbda), [l/sum(lmbda) for l in lmbda], self)] + self.transitive_nodes + [ExitNode(self.max_simulation_time)]

    def find_next_active_node(self):
        """
        Return the next active node:

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> i = 0
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i += 1
            >>> Q.find_next_active_node()
            Arrival Node

            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> i = 10
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i -= 1
            >>> Q.find_next_active_node()
            Node 2
        """
        return min(self.nodes, key=lambda x: x.next_event_time)

    def simulate(self):
        """
        Run the actual simulation.
        """
        next_active_node = self.find_next_active_node()
        while next_active_node.next_event_time < self.max_simulation_time:
            next_active_node.have_event()
            next_active_node = self.find_next_active_node()

    def mean_waits(self):
        """
        A method to return the mean wait in the system (after simulation has been run)
        """
        all_individuals = [individual for node in self.nodes[1:] for individual in node.individuals]
        mean_waits = [round(r.wait,10) for individual in all_individuals for r in individual.data_records[1]]
        #mean_waits = {node : mean([record.wait for individual in all_individuals for record in individual.data_records[node.id_number] if record.arrival_date > self.warm_up and node in individual.data_records]) for node in self.transitive_nodes}
        return mean_waits

    def records(self):
        """
        Return all records
        """
        all_individuals = sorted([individual for node in self.nodes[1:] for individual in node.individuals], key=lambda x:x.id_number)
        for ind in all_individuals:
            if 1 in ind.data_records:
                record = ind.data_records[1][0]
                print ind.id_number, record.arrival_date, record.wait, record.service_date, record.service_time, record.exit_date, record.node



if __name__ == '__main__':
    Q = Simulation([1], [2], [1], [[0]], 100, 0)
    Q.simulate()
    Q.records()
