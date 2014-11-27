"""
A simulation of a Qing network
"""
from __future__ import division
from random import random, seed, expovariate
from numpy import mean as np_mean

def mean(lst):
    """
    A function to find the mean of a list, returns false if empty

        TESTS 1
        >>> AList = [6, 6, 4, 6, 8]
        >>> mean(AList)
        6.0

        TESTS 2
        >>> AnotherList = []
        >>> mean(AnotherList)
        False

    """

    if len(lst) == 0:
        return False
    return np_mean(lst)

class DataRecord:
    """
    A class for a data record
    """
    def __init__(self, arrival_date, service_time, exit_date, node):
        """
            TESTS 1
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
            >>> r.node
            3

            TESTS 2
            >>> r = DataRecord(5.7, 2.1, 8.2, 1)
            >>> r.arrival_date
            5.7
            >>> round(r.wait, 5)
            0.4
            >>> r.service_date
            6.1
            >>> r.service_time
            2.1
            >>> r.exit_date
            8.2
            >>> r.node
            1

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> r = DataRecord(4, 2.5, 3, -3)
            >>> r.arrival_date
            4
            >>> r.wait
            -3.5
            >>> r.service_date
            0.5
            >>> r.service_time
            2.5
            >>> r.exit_date
            3
            >>> r.node
            -3
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

            TESTS 1
            >>> i = Individual(22)
            >>> i.in_service
            False
            >>> i.end_service_date
            False
            >>> i.id_number
            22
            >>> i.data_records
            {}

            TESTS 2
            >>> i = Individual(5)
            >>> i.in_service
            False
            >>> i.end_service_date
            False
            >>> i.id_number
            5
            >>> i.data_records
            {}

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> i = Individual(-4.6)
            >>> i.in_service
            False
            >>> i.end_service_date
            False
            >>> i.id_number
            -4.6
            >>> i.data_records
            {}
        """
        self.in_service = False
        self.end_service_date = False
        self.id_number = id_number
        self.data_records = {}

    def __repr__(self):
        """
            TESTS 1
            >>> i = Individual(3)
            >>> i
            Individual 3

            TESTS 2
            >>> i = Individual(93)
            >>> i
            Individual 93

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> i = Individual(twelve)
            Traceback (most recent call last):
            ...
            NameError: name 'twelve' is not defined
        """
        return 'Individual %s' % self.id_number

class Node:
    """
    Class for a node on our network
    """
    def __init__(self, lmbda, mu, c, transition_matrix_row, id_number, simulation):
        """
        Initialise a node.

            TESTS 1
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

            TESTS 2
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> N = Q.transitive_nodes[1]
            >>> N.lmbda
            3
            >>> N.mu
            10
            >>> N.c
            1
            >>> N.transition_row
            [0.4, 0.4]
            >>> N.individuals
            []
            >>> N.id_number
            2
            >>> N.next_event_time
            50
            >>> N.cum_transition_row
            [0.4, 0.8]
            >>> N.simulation.max_simulation_time
            50

            TESTS 3 (PARAMETERS DON't MAKE SENSE)
            >>> N = Node(2, 7, 2, [[0.6, 0.1], [0.2, 0.5]], 3, False)
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for +=: 'int' and 'list'
        """
        self.lmbda = lmbda
        self.mu = mu
        self.c = c
        self.transition_row = transition_matrix_row
        self.next_event_time = 0
        self.individuals = []
        self.id_number = id_number
        self.cum_transition_row = self.find_cum_transition_row()
        self.simulation = simulation
        if self.simulation:
            self.next_event_time = self.simulation.max_simulation_time
        self.numbers_in_node = [[0.0,0]]

    def find_cum_transition_row(self):
        """
        Finds the cumulative transition row for the node

            TESTS 1
            >>> N = Node(6, 6, 3, [0.125, 0.200, 0.250, 0.150, 0.170, 0.1], 1, False)
            >>> N.cum_transition_row
            [0.125, 0.325, 0.575, 0.725, 0.895, 0.995]

            TESTS 2
            >>> Q = Simulation([5, 3], [4, 3], [5, 5], [[0.2, 0.5], [0.1, 0.7]], 100)
            >>> N = Q.nodes[2]
            >>> [round(k,1) for k in N.cum_transition_row]
            [0.1, 0.8]
        """

        sum_p = 0
        cum_transition_row = []
        for p in self.transition_row:
            sum_p += p
            cum_transition_row.append(sum_p)
        return cum_transition_row

    def __repr__(self):
        """
        Representation of a node::

            TESTS 1
            >>> N = Node(5, 10, 1, [.2, .5], 1, False)
            >>> N.id_number
            1

            TESTS 2
            >>> Q = Simulation([5, 2, 1], [8, 8, 3], [1, 2, 1], [[0.2, 0.1, 0.1], [0.1, 0.4, 0.3], [0.3, 0.1, 0.1]], 300)
            >>> N = Q.transitive_nodes[2]
            >>> N.id_number
            3

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> N = Node(3, 4, 3, [[0.4, 0.3], [0.1, 0.2]], 2, False)
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for +=: 'int' and 'list'
        """
        return 'Node %s' % self.id_number

    def release(self):
        """
        Update node when a service happens.

            TESTS 1
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
            >>> N.release()
            >>> round(i.exit_date, 5)
            1.01443
            >>> i.data_records[N.id_number][0].wait
            0.0

            TESTS 2
            >>> seed(6)
            >>> Q = Simulation([7, 4], [9, 11], [2, 1], [[.3, .2], [.1, .4]], 60)
            >>> N = Q.transitive_nodes[0]
            >>> i = Individual(4)
            >>> i.arrival_date
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'arrival_date'
            >>> i.service_time
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'service_time'
            >>> N.accept(i, 3)
            >>> i.arrival_date
            3
            >>> round(i.service_time, 5)
            0.17519
            >>> i.data_records[N.id_number]
            Traceback (most recent call last):
            ...
            KeyError: 1
            >>> i.exit_date
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'exit_date'
            >>> N.release()
            >>> round(i.exit_date, 5)
            3.17519
            >>> i.data_records[N.id_number][0].wait
            0.0

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> seed(2)
            >>> Q = Simulation([2], [3], [1], [[0]], 20)
            >>> N = Q.transitive_nodes[0]
            >>> N.release()
            Traceback (most recent call last):
            ...
            IndexError: pop from empty list
        """
        next_individual = self.individuals.pop(0)
        self.count_down(self.next_event_time)

        next_individual.exit_date = self.next_event_time
        self.write_individual_record(next_individual)

        next_node = self.next_node()
        next_node.accept(next_individual, self.next_event_time)
        self.update_next_event_date()

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

            TESTS 1
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

            TESTS 2
            >>> seed(4)
            >>> N = Node(2, 2, 2, [.3, .3], 3, False)
            >>> next_individual = Individual(6)
            >>> N.accept(next_individual, 8.2)
            >>> N.individuals
            [Individual 6]
            >>> next_individual.arrival_date
            8.2
            >>> round(next_individual.service_time, 5)
            0.13463
            >>> round(N.next_event_time, 5)
            8.33463
            >>> N.accept(Individual(10), 1)
            >>> round(N.next_event_time, 5)
            1.05444

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> seed(2)
            >>> N = Node(1, 2, -1, [.2, .1], 1, False)
            >>> next_individual = Individual(2)
            >>> N.accept(next_individual, 8.2)
            Traceback (most recent call last):
            ...
            IndexError: list index out of range
        """
        next_individual.arrival_date = current_time
        next_individual.service_time = expovariate(self.mu)

        if len(self.individuals) < self.c:
            next_individual.end_service_date = current_time + next_individual.service_time
        else:
            next_individual.end_service_date = self.individuals[-self.c].end_service_date + next_individual.service_time

        self.include_individual(next_individual)
        self.count_up(current_time)
        self.update_next_event_date()

    def find_index_for_individual(self, individual):
        """
        Returns the index of the position that the new individual will take


            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [4, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i) for i in range(10)]
            >>> end_date = 2
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 2
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            >>> ind = Individual(10)
            >>> ind.end_service_date = 17
            >>> node.find_index_for_individual(ind)
            -2
            >>> ind = Individual(11)
            >>> ind.end_service_date = 67
            >>> node.find_index_for_individual(ind)
            False

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [5, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i) for i in range(2)]
            >>> end_date = 1
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 4
            >>> [ind.end_service_date for ind in node.individuals]
            [1, 5]
            >>> ind = Individual(3)
            >>> ind.end_service_date = 3
            >>> node.find_index_for_individual(ind)
            -1

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [4, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i) for i in range(3)]
            >>> end_date = 1
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 4
            >>> [ind.end_service_date for ind in node.individuals]
            [1, 5, 9]
            >>> ind = Individual(3)
            >>> ind.end_service_date = 3
            >>> node.find_index_for_individual(ind)
            -2

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [400, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i) for i in range(3)]
            >>> end_date = 1
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 4
            >>> [ind.end_service_date for ind in node.individuals]
            [1, 5, 9]
            >>> ind = Individual(3)
            >>> ind.end_service_date = 3
            >>> node.find_index_for_individual(ind)
            -2

            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [400, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = []
            >>> end_date = 1
            >>> [ind.end_service_date for ind in node.individuals]
            []
            >>> ind = Individual(3)
            >>> ind.end_service_date = 3
            >>> node.find_index_for_individual(ind)
            False
        """
        for i, ind in enumerate(self.individuals[-self.c:]):
                if individual.end_service_date < ind.end_service_date:
                    return -min(self.c,len(self.individuals)) + i
        return False

    def include_individual(self, individual):
        """
        Geraint to write test
            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [4, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i) for i in range(10)]
            >>> end_date = 2
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 2
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 3, Individual 4, Individual 5, Individual 6, Individual 7, Individual 8, Individual 9]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            >>> ind = Individual(10)
            >>> ind.end_service_date = 17
            >>> node.include_individual(ind)
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 3, Individual 4, Individual 5, Individual 6, Individual 7, Individual 10, Individual 8, Individual 9]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 8, 10, 12, 14, 16, 17, 18, 20]

            TESTS 2
            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [7, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i) for i in range(3)]
            >>> end_date = 2
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 2
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6]
            >>> ind = Individual(10)
            >>> ind.end_service_date = 17
            >>> node.include_individual(ind)
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 10]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 17]

            TESTS 3
            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [8, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i) for i in range(6)]
            >>> end_date = 2
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 2
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 3, Individual 4, Individual 5]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 8, 10, 12]
            >>> ind = Individual(33)
            >>> ind.end_service_date = 7
            >>> node.include_individual(ind)
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 33, Individual 3, Individual 4, Individual 5]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 7, 8, 10, 12]

            TESTS 3
            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [2, 1], [[.2, .5], [.4, .4]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals
            []
            >>> [ind.end_service_date for ind in node.individuals]
            []
            >>> ind = Individual(1)
            >>> ind.end_service_date = 3.5
            >>> node.include_individual(ind)
            >>> node.individuals
            [Individual 1]
            >>> [ind.end_service_date for ind in node.individuals]
            [3.5]
        """
        index = self.find_index_for_individual(individual)
        if index:
            self.individuals.insert(self.find_index_for_individual(individual), individual)
        else:
            self.individuals.append(individual)



    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            TESTS 1
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

            TESTS 2
            >>> seed(8)
            >>> Q = Simulation([3, 3, 1], [6, 12, 2], [1, 1, 3], [[.2, .4, .4], [.4, .4, .1], [.1, .1, .1]], 40)
            >>> node = Q.transitive_nodes[1]
            >>> node.individuals
            []
            >>> node.next_event_time
            40
            >>> node.update_next_event_date()
            >>> node.next_event_time
            40
            >>> ind = Individual(2)
            >>> node.accept(ind, 1)
            >>> node.update_next_event_date()
            >>> round(node.next_event_time, 5)
            1.02142

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> seed(3)
            >>> node = Node(2, 2, 2, [.3, .3], 3, False)
            >>> node.update_next_event_date()
            Traceback (most recent call last):
            ...
            AttributeError: 'bool' object has no attribute 'max_simulation_time'
        """
        if len(self.individuals) == 0:
            self.next_event_time = self.simulation.max_simulation_time
        else:
            self.next_event_time = self.individuals[0].end_service_date

    def next_node(self):
        """
        Finds the next node according the random distribution.

            TESTS 1
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

            TESTS 2
            >>> seed(54)
            >>> Q = Simulation([4, 5, 6], [12, 5, 9], [1, 3, 2], [[0.1, 0.2, 0.5], [0.4, 0.2, 0.2], [0.3, 0.3, 0.3]], 80)
            >>> node = Q.transitive_nodes[2]
            >>> node.next_node()
            Exit Node
            >>> node.next_node()
            Node 1
            >>> node.next_node()
            Node 2
            >>> node.next_node()
            Node 2
            >>> node.next_node()
            Exit Node
            >>> node.next_node()
            Node 2
            >>> node.next_node()
            Node 2
            >>> node.next_node()
            Node 2

            TESTS 3 (PARAMETERS DON't MAKE SENSE)
            >>> seed(23)
            >>> Q = Simulation([3, 3], [4, 5], [2, 1], [[0.1, 0.2], [0.3, 0.1]], 30)
            >>> node = Q.transitive_nodes[1]
            >>> node.next_node()
            Exit Node
            >>> node.next_node()
            Exit Node
            >>> node.next_node()
            Exit Node
            >>> node.next_node()
            Node 1

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

            TESTS 1
            >>> seed(7)
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
            3.96087
            >>> round(ind.data_records[1][0].service_date, 5)
            6.96087
            >>> round(ind.data_records[1][0].service_time, 5)
            0.03913
            >>> ind.data_records[1][0].exit_date
            7
            >>> ind.data_records[1][0].node
            1

            TESTS 2
            >>> seed(12)
            >>> Q = Simulation([2, 1], [6, 3], [1, 2], [[.4, .3], [.2, .7]], 70)
            >>> N = Q.transitive_nodes[0]
            >>> ind = Individual(28)
            >>> N.accept(ind, 6)
            >>> N.write_individual_record(ind)
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'exit_date'
            >>> ind.exit_date = 9
            >>> N.write_individual_record(ind)
            >>> ind.data_records[1][0].arrival_date
            6
            >>> round(ind.data_records[1][0].wait, 5)
            2.89274
            >>> round(ind.data_records[1][0].service_date, 5)
            8.89274
            >>> round(ind.data_records[1][0].service_time, 5)
            0.10726
            >>> ind.data_records[1][0].exit_date
            9
            >>> ind.data_records[1][0].node
            1

        """
        record = DataRecord(individual.arrival_date, individual.service_time, individual.exit_date, self.id_number)
        if self.id_number in individual.data_records:
            individual.data_records[self.id_number].append(record)
        else:
            individual.data_records[self.id_number] = [record]

    def count_up(self, current_time):
        """
        Records the time that the node gains an individual and the current number of individuals

            TESTS 1
            >>> N = Node(4, 5, 2, [0.1, 0.5, 0.2], 1, False)
            >>> N.numbers_in_node
            [[0.0, 0]]
            >>> N.count_up(4.2)
            >>> N.numbers_in_node
            [[0.0, 0], [4.2, 1]]
        """
        self.numbers_in_node.append([current_time, self.numbers_in_node[-1][1] + 1])

    def count_down(self,current_time):
        """
        Recored the time that the node loses an individual and the current number of individuals

            TESTS 1
            >>> N = Node(7, 19, 1, [0.3, 0.2], 2, False)
            >>> N.numbers_in_node = [[0.0, 0], [0.3, 1], [0.5, 2]]
            >>> N.count_down(0.9)
            >>> N.numbers_in_node
            [[0.0, 0], [0.3, 1], [0.5, 2], [0.9, 1]]
        """
        self.numbers_in_node.append([current_time, self.numbers_in_node[-1][1] - 1])



class ArrivalNode:
    """
    Class for the arrival node on our network
    """
    def __init__(self, lmbda, transition_row, simulation):
        """
        Initialise a node.

        Here is an example::

            TESTS 1
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

            TESTS 2
            >>> Q = Simulation([3, 2, 3], [4, 5, 3], [2, 1, 2], [[.1, .1, .1], [.3, .4, .1], [.2, .2, .5]], 100)
            >>> N = Q.nodes[0]
            >>> N.lmbda
            8
            >>> N.transition_row
            [0.375, 0.25, 0.375]
            >>> sum(N.transition_row)
            1.0
            >>> N.cum_transition_row
            [0.375, 0.625, 1.0]
            >>> N.simulation.max_simulation_time
            100
        """
        self.lmbda = lmbda
        self.transition_row = transition_row
        self.next_event_time = 0
        self.number_of_individuals = 0
        self.cum_transition_row = self.find_cumulative_transition_row()
        self.simulation = simulation

    def find_cumulative_transition_row(self):
        """
        Finds the cumulative transition row for the arrival node

            TESTS 1
            >>> N = ArrivalNode(6, [0.125, 0.200, 0.250, 0.150, 0.170, 0.1], False)
            >>> N.cum_transition_row
            [0.125, 0.325, 0.575, 0.725, 0.895, 0.995]

            TESTS 2
            >>> Q = Simulation([5, 10, 25], [20, 30, 30], [1, 2, 2], [[0.1, 0.3, 0.1], [0.2, 0.2, 0.2], [0.6, 0.1, 0.1]], 100)
            >>> N = Q.nodes[0]
            >>> N.cum_transition_row
            [0.125, 0.375, 1.0]
        """
        sum_p = 0
        cum_transition_row = []
        for p in self.transition_row:
            sum_p += p
            cum_transition_row.append(sum_p)
        return cum_transition_row

    def __repr__(self):
        """
        Representation of a node::

            TESTS 1
            >>> N = ArrivalNode(5, [.5, .5], False)
            >>> N
            Arrival Node

            TESTS 2
            >>> Q = Simulation([4], [4], [2], [[0.5]], 40)
            >>> N = Q.nodes[0]
            >>> N
            Arrival Node

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> N = ArrivalNode(-5, [0.2, 1.3], False)
            >>> N
            Arrival Node
        """
        return 'Arrival Node'

    def release(self):
        """
        Update node when a service happens.

            TESTS 1
            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> N = ArrivalNode(8, [.625, .375], Q)
            >>> N.next_event_time
            0
            >>> N.release()
            >>> Q.transitive_nodes[0].individuals
            [Individual 1]
            >>> Q.transitive_nodes[1].individuals
            []
            >>> round(N.next_event_time,5)
            0.18037

            TESTS 2
            >>> seed(12)
            >>> Q = Simulation([8, 1], [10, 3], [1, 1], [[.1, .5], [.4, .3]], 50)
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> N = ArrivalNode(90, [.1, .9], Q)
            >>> N.next_event_time
            0
            >>> N.release()
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            [Individual 1]
            >>> round(N.next_event_time,5)
            0.0122

            TESTS 3 (PARAMETERS DON't MAKE SENSE)
            >>> seed(1)
            >>> Q = Simulation([8, 1], [10, 3], [1, 1], [[.1, .5], [.4, .3]], 50)
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> N = ArrivalNode(-3, [0, 0], Q)
            >>> N.release()
            Traceback (most recent call last):
            ...
            AttributeError: 'NoneType' object has no attribute 'accept'



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

            TESTS 1
            >>> seed(1)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> N = ArrivalNode(8, [.625, .375], Q)
            >>> N.next_node()
            Node 1
            >>> N.next_node()
            Node 2
            >>> N.next_node()
            Node 2

            TESTS 2
            >>> seed(401)
            >>> Q = Simulation([2, 9], [7, 9], [1, 3], [[.2, .5], [.4, .4]], 50)
            >>> N = Q.nodes[0]
            >>> N.next_node()
            Node 2
            >>> N.next_node()
            Node 2
            >>> N.next_node()
            Node 2

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> seed(84)
            >>> Q = Simulation([2, 9], [7, 9], [1, 3], [[.2, .5], [.4, .4]], 50)
            >>> N = ArrivalNode(20, [0.0, 0.0], False)
            >>> N.next_node()
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

            TESTS 1
            >>> N = ExitNode(100)
            >>> N.individuals
            []
            >>> N.id_number
            -1
            >>> N.next_event_time
            100

            TESTS 2
            >>> N = ExitNode(4)
            >>> N.id_number
            -1
            >>> N.next_event_time
            4

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> N = ExitNode()
            Traceback (most recent call last):
            ...
            TypeError: __init__() takes exactly 2 arguments (1 given)
        """
        self.individuals = []
        self.id_number = -1
        self.next_event_time = max_simulation_time


    def __repr__(self):
        """
        Representation of a node::
            TESTS 1
            >>> N = ExitNode(500)
            >>> N
            Exit Node

            TESTS 2
            >>> N = ExitNode(320)
            >>> N
            Exit Node

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> N = ExitNode(2, 6, -1, False)
            Traceback (most recent call last):
            ...
            TypeError: __init__() takes exactly 2 arguments (5 given)
        """
        return 'Exit Node'

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

            TESTS 1
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

            TESTS 2
            >>> Q = Simulation([2, 9], [7, 9], [1, 3], [[.2, .5], [.4, .4]], 12)
            >>> N = Q.nodes[-1]
            >>> N.individuals
            []
            >>> N.next_event_time
            12
            >>> next_individual = Individual(3)
            >>> N.accept(next_individual, 3)
            >>> N.individuals
            [Individual 3]
            >>> N.next_event_time
            12

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> N = ExitNode(-5)
            >>> N.accept(Individual(4), 2)
            >>> N.individuals
            [Individual 4]
            >>> N.next_event_time
            -5
        """
        self.individuals.append(next_individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            TESTS 1
            >>> N = ExitNode(25)
            >>> N.next_event_time
            25
            >>> N.update_next_event_date()
            >>> N.next_event_time
            25

            TESTS 2
            >>> Q = Simulation([4, 1], [2, 4], [5, 1], [[.8, .1], [.3, .25]], 60)
            >>> N = Q.nodes[-1]
            >>> N.next_event_time
            60
            >>> N.update_next_event_date()
            >>> N.next_event_time
            60

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> N = ExitNode(False)
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
    def __init__(self, lmbda, mu, c, transition_matrix, max_simulation_time, warm_up=0):
        """
        Initialise a queue instance.

        Here is an example::

            TESTS 1
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

            TESTS 2
            >>> Q = Simulation([5.5], [12.2], [1], [[0]], 600, 250)
            >>> Q.lmbda
            [5.5]
            >>> Q.mu
            [12.2]
            >>> Q.c
            [1]
            >>> Q.transition_matrix
            [[0]]
            >>> Q.nodes
            [Arrival Node, Node 1, Exit Node]
            >>> Q.transitive_nodes
            [Node 1]
            >>> Q.max_simulation_time
            600
            >>> Q.warm_up
            250

            TESTS 3
            >>> Q = Simulation([4, 2], [5, 4], [1, 1], [[.2, .5]], 300, 35)
            Traceback (most recent call last):
            ...
            ValueError: Transition matrix must have same number of rows and columns as nodes (2)

            TESTS 4
            >>> Q = Simulation([4, 2], [5, 4], [1, 1], [[.2], [.5]], 300, 35)
            Traceback (most recent call last):
            ...
            ValueError: Transition matrix must have same number of rows and columns as nodes (2)

        If a negative arrival rate is passed as an argument then the simulation
        raises an error::

            >>> Q = Simulation([-1, 2], [5, 4], [1, 1], [[0.2, 0.2], [.3, .2]], 300, 35)
            Traceback (most recent call last):
            ...
            ValueError: All arrival rates must be positive

        Similarly if a negative service rate is passed as an argument then the simulation
        raises an error::

            >>> Q = Simulation([1, 2], [5, -4], [1, 1], [[0.2, 0.2], [.6, .2]], 300, 35)
            Traceback (most recent call last):
            ...
            ValueError: All service rates must be positive

        All server number must be integers::

            >>> Q = Simulation([1, 2], [5, 4], [1.2, 1], [[0.2, 0.2], [.5, .3]], 300, 35)
            Traceback (most recent call last):
            ...
            ValueError: All servers must be positive integer number

        All server number must be positive::

            >>> Q = Simulation([1, 2], [5, 4], [-2, 1], [[0.2, 0.2], [.3, .2]], 300, 35)
            Traceback (most recent call last):
            ...
            ValueError: All servers must be positive integer number

        All transition rows must sum to less than or equal one::

            >>> Q = Simulation([1, 2], [5, 4], [2, 1], [[0.9, 0.2], [.4, .2]], 300, 35)
            Traceback (most recent call last):
            ...
            ValueError: All transition rows must have sum less than or equal to 1
        """

        if len(transition_matrix) != len(lmbda) or any(len(row) != len(lmbda) for row in transition_matrix):
            raise ValueError('Transition matrix must have same number of rows and columns as nodes (%s)' % len(lmbda))

        if any(l <= 0 for l in lmbda):
            raise ValueError('All arrival rates must be positive')

        if any(m <= 0 for m in mu):
            raise ValueError('All service rates must be positive')

        if any(type(k) is not int or k <= 0 for k in c):
            raise ValueError('All servers must be positive integer number')

        if any(sum(row) > 1 for row in transition_matrix):
            raise ValueError('All transition rows must have sum less than or equal to 1')

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

            TESTS 2
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> i = 0
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i += 1
            >>> Q.find_next_active_node()
            Arrival Node

            TESTS 2
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> i = 10
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i -= 1
            >>> Q.find_next_active_node()
            Node 2

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> Q = Simulation([5, 3], [10, 10], [1, 1], [[.2, .5], [.4, .4]], 50)
            >>> i = 10
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = False
            ...     i -= 1
            >>> Q.find_next_active_node()
            Arrival Node
        """
        return min(self.nodes, key=lambda x: x.next_event_time)

    def simulate(self):
        """
        Run the actual simulation.

            TESTS 1
            >>> seed(99)
            >>> Q = Simulation([1], [2], [1], [[0]], 20, 5)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            0.31442

            TESTS 2
            >>> seed(2)
            >>> Q = Simulation([2, 3], [2, 5], [2, 1], [[0.2, 0.2], [0.3, 0.3]], 60, 10)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            1.78606
            >>> round(Q.mean_waits()[2], 5)
            4.2586

            TESTS 3
            >>> seed(99)
            >>> Q = Simulation([2, 3], [4, 5], [500, 1], [[0.2, 0.2], [0.3, 0.3]], 60, 10)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            0.0

            TESTS 4 a quiet m/m/c queue
            >>> seed(9)
            >>> Q = Simulation([4], [3], [3], [[0]], 50)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            0.03382
        """
        next_active_node = self.find_next_active_node()
        while next_active_node.next_event_time < self.max_simulation_time:
            next_active_node.release()
            next_active_node = self.find_next_active_node()

    def get_all_individuals(self):
        """
        Returns list of all individuals with at least one record

            TESTS 1
            >>> seed(1)
            >>> Q = Simulation([1], [2], [1], [[0]], 5)
            >>> Q.simulate()
            >>> Q.get_all_individuals()
            [Individual 1, Individual 2, Individual 3, Individual 4]

            TESTS 2
            >>> seed(10)
            >>> Q = Simulation([2, 3], [2, 5], [2, 1], [[0.2, 0.2], [0.3, 0.3]], 2)
            >>> Q.simulate()
            >>> Q.get_all_individuals()
            [Individual 4, Individual 9, Individual 2, Individual 3, Individual 6, Individual 1, Individual 8, Individual 7, Individual 5, Individual 10]

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> seed(100)
            >>> Q = Simulation([1], [2], [1], [[0]], -2)
            >>> Q.simulate()
            >>> Q.get_all_individuals()
            []
        """
        return [individual for node in self.nodes[1:] for individual in node.individuals if len(individual.data_records) > 0]

    def get_individuals_by_node(self):
        """
        Return a dictionary with keys nodes and values: lists of players who have a complete record for that node.

            TESTS 1
            >>> seed(1)
            >>> Q = Simulation([1], [2], [1], [[0]], 5)
            >>> Q.simulate()
            >>> len(Q.get_individuals_by_node()[1])
            4

            TESTS 2
            >>> seed(10)
            >>> Q = Simulation([2, 3], [2, 5], [2, 1], [[0.2, 0.2], [0.3, 0.3]], 2)
            >>> Q.simulate()
            >>> len(Q.get_individuals_by_node()[1])
            6
            >>> Q.get_individuals_by_node()[2]
            [Individual 4, Individual 9, Individual 2, Individual 3, Individual 1, Individual 5]

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> seed(2)
            >>> Q = Simulation([1], [0.01], [1], [[0]], 5)
            >>> Q.simulate()
            >>> Q.get_individuals_by_node()[1]
            []
        """
        return {node.id_number:[individual for individual in self.get_all_individuals() if node.id_number in individual.data_records] for node in self.transitive_nodes}

    def get_records_by_node(self):
        """
        Returns all records of an individual

            TESTS 1
            >>> seed(1)
            >>> Q = Simulation([1], [2], [1], [[0]], 5)
            >>> Q.simulate()
            >>> Q.get_records_by_node()[1][0].wait
            0.0
            >>> round(Q.get_records_by_node()[1][1].arrival_date, 5)
            1.44297

            TESTS 2
            >>> seed(3)
            >>> Q = Simulation([1, 2], [2, 2], [1, 2], [[0.2, 0.2], [0.2, 0.2]], 5)
            >>> Q.simulate()
            >>> round(Q.get_records_by_node()[1][0].wait, 5)
            0.0
            >>> round(Q.get_records_by_node()[1][1].service_date, 5)
            0.39288
            >>> round(Q.get_records_by_node()[2][1].wait, 5)
            0.0

            TESTS 3 (PARAMETERS DON'T MAKE SENSE)
            >>> seed(2)
            >>> Q = Simulation([8], [8], [2], [[0]], 5)
            >>> Q.simulate()
            >>> Q.get_records_by_node()[0][0].wait
            Traceback (most recent call last):
            ...
            KeyError: 0
        """
        individuals_by_node = self.get_individuals_by_node()
        return {node_id:[record for individual in individuals_by_node[node_id] for record in individual.data_records[node_id]] for node_id in individuals_by_node}

    def mean_waits(self):
        """
        A method to return the mean wait in the system (after simulation has been run)

            TESTS 1
            >>> seed(11)
            >>> Q = Simulation([6], [12], [1], [[0]], 25)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            0.15754

            TESTS 2
            >>> seed(18)
            >>> Q = Simulation([5, 7], [6, 7], [1, 2], [[0.1, 0.1], [0.2, 0.1]], 30)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            4.51115
            >>> round(Q.mean_waits()[2], 5)
            0.03058
            >>> round(Q.mean_waits()[0], 5)
            Traceback (most recent call last):
            ...
            KeyError: 0

            TESTS 3
            >>> seed(25)
            >>> Q = Simulation([5, 7], [6, 7], [1, 2], [[0.1, 0.1], [0.2, 0.1]], 0, 0)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            Traceback (most recent call last):
            ...
            ValueError: No data simulated

            TESTS 4
            >>> seed(1)
            >>> Q = Simulation([0.00005, 7], [6, 7], [1, 2], [[0, 0.1], [0, 0.1]], 10, 0)
            >>> Q.simulate()
            >>> Q.mean_waits()[1]
            False
        """
        records_by_node = self.get_records_by_node()
        if all(len(r) == 0 for r in records_by_node.values()):
            raise ValueError("No data simulated")
        mean_waits = {node_id:mean([r.wait for r in records_by_node[node_id] if r.arrival_date > self.warm_up]) for node_id in records_by_node}
        return mean_waits

    def records(self):
        """
        Return all records

            TESTS 1
            >>> seed(1)
            >>> Q = Simulation([11, 2], [4, 3], [4, 2], [[0.6, 0.1], [0.3, 0.1]], 0.2824)
            >>> Q.simulate()
            >>> Q.records()
            2 0.110997609642 -2.77555756156e-17 0.110997609642 0.171014694915 0.282012304557 1

            TESTS 2
            >>> seed(8)
            >>> Q = Simulation([3], [7], [1], [[0]], 0.5)
            >>> Q.simulate()
            >>> Q.records()
            1 0 0.0 0.0 0.468280502531 0.468280502531 1
            2 0.0450178591967 0.423262643334 0.468280502531 0.0127191018503 0.480999604381 1
        """
        all_individuals = sorted([individual for node in self.nodes[1:] for individual in node.individuals], key=lambda x:x.id_number)
        for ind in all_individuals:
            if 1 in ind.data_records:
                record = ind.data_records[1][0]
                print ind.id_number, record.arrival_date, record.wait, record.service_date, record.service_time, record.exit_date, record.node

    def find_times_in_state(self):
        """
        Returns a list of dictionaries for each node, with the amount of time that node spent in each state

            TESTS 1
            >>> Q = Simulation([3, 3], [7, 7], [1, 1], [[0.1, 0.5], [0.1, 0.2]], 0.5)
            >>> Q.nodes[1].numbers_in_node = [[0, 1], [3, 2], [4, 1], [6, 0], [9, 1], [11, 0]]
            >>> Q.nodes[2].numbers_in_node = [[0, 0], [2, 1], [4, 0], [5, 1], [8, 2], [12, 1], [13, 2], [15, 1], [17, 0]]
            >>> Q.find_times_in_state()
            [{0: 3, 1: 7, 2: 1}, {0: 3, 1: 8, 2: 6}]

            TESTS 2
            >>> Q = Simulation([3, 3, 1], [7, 7, 2], [1, 1, 1], [[0.1, 0.5, 0.1], [0.1, 0.2, 0.1], [0.3, 0.5, 0.1]], 0.5)
            >>> Q.nodes[1].numbers_in_node = [[0, 0], [0.3, 1], [0.4, 2], [0.7, 1], [1.1, 0], [1.6, 1], [1.7, 2], [1.9, 3], [2.4, 2], [2.5, 1], [2.7, 2], [2.8, 1], [3, 0]]
            >>> Q.nodes[2].numbers_in_node = [[0, 0], [0.1, 1], [0.3, 0], [0.8, 1], [1.0, 2], [1.2, 3], [1.6, 2], [1.9, 3], [2.4, 4], [2.5, 3], [2.7, 2]]
            >>> Q.nodes[3].numbers_in_node = [[0, 0], [0.6, 1], [0.8, 0], [1.7, 1], [2.3, 2], [2.4, 1], [2.6, 1], [2.9, 0]]
            >>> Q.find_times_in_state()
            [{0: 0.8, 1: 1.0000000000000004, 2: 0.6999999999999996, 3: 0.5}, {0: 0.6, 1: 0.3999999999999999, 2: 0.4999999999999998, 3: 1.1000000000000003, 4: 0.10000000000000009}, {0: 1.5, 1: 1.2999999999999998, 2: 0.10000000000000009}]
        """

        return [{j:sum([node.numbers_in_node[i+1][0] - node.numbers_in_node[i][0] for i in range(len(node.numbers_in_node)-1) if node.numbers_in_node[i][1]==j]) for j in range(max([node.numbers_in_node[k][1] for k in range(len(node.numbers_in_node))])+1)} for node in self.transitive_nodes]

    def mean_customers(self):
        """
        Returns a dictionary of the mean number of customers at each node

            TESTS 1
            >>> Q = Simulation([3, 3], [7, 7], [1, 1], [[0.1, 0.5], [0.1, 0.2]], 0.5)
            >>> Q.nodes[1].numbers_in_node = [[0, 1], [3, 2], [4, 1], [6, 0], [9, 1], [11, 0]]
            >>> Q.nodes[2].numbers_in_node = [[0, 0], [2, 1], [4, 0], [5, 1], [8, 2], [12, 1], [13, 2], [15, 1], [17, 0]]
            >>> Q.mean_customers()
            {1: 0.8181818181818182, 2: 1.1764705882352942}
        """

        return {node.id_number:(sum([(self.find_times_in_state()[node.id_number-1][i]*i) for i in range(len(self.find_times_in_state()[node.id_number-1]))]))/self.nodes[node.id_number].numbers_in_node[-1][0] for node in self.transitive_nodes}



if __name__ == '__main__':
    Q = Simulation([1,2], [2,1], [5,5], [[.2,.3],[.6,.1]], 1000, 200)
    Q.simulate()
    print Q.mean_waits()
    print Q.mean_customers()