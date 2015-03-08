"""
Usage: simulation.py <dir_name> [<sffx>]

Arguments
    dir_name    : name of the directory from which to read in parameters and write data files
    suff        : optional suffix to add to the data file name

Options
    -h          : displays this help file
"""

from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from numpy import mean as np_mean
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import docopt

def mean(lst):
    """
    A function to find the mean of a list, returns false if empty

    Tests with a full list.
        >>> AList = [6, 6, 4, 6, 8]
        >>> mean(AList)
        6.0

     Tests with an empty list.
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
    def __init__(self, arrival_date, service_time, service_start_date, exit_date, node):
        """
        An example of a data record instance.
            >>> r = DataRecord(2, 3, 2, 8, 1)
            >>> r.arrival_date
            2
            >>> r.wait
            0
            >>> r.service_start_date
            2
            >>> r.service_time
            3
            >>> r.service_end_date
            5
            >>> r.blocked
            3
            >>> r.exit_date
            8
            >>> r.node
            1

        Another example of a data record instance.
            >>> r = DataRecord(5.7, 2.1, 8.2, 10.3, 1)
            >>> r.arrival_date
            5.7
            >>> round(r.wait, 5)
            2.5
            >>> r.service_start_date
            8.2
            >>> r.service_time
            2.1
            >>> round(r.service_end_date, 5)
            10.3
            >>> round(r.blocked, 5)
            0.0
            >>> r.exit_date
            10.3
            >>> r.node
            1
        """
        if exit_date < arrival_date:
            raise ValueError('Arrival date should preceed exit date')

        if service_time < 0:
            raise ValueError('Service time should be positive')

        self.arrival_date = arrival_date
        self.service_time = service_time
        self.service_start_date = service_start_date
        self.exit_date = exit_date

        self.service_end_date = service_start_date + service_time
        self.wait = service_start_date - arrival_date
        self.blocked = exit_date - self.service_end_date
        self.node = node

class Individual:
    """
    Class for an individual
    """
    def __init__(self, id_number, customer_class=0):
        """
        Initialise an individual

        An example of an Individual instance.
            >>> i = Individual(22, 3)
            >>> i.arrival_date
            False
            >>> i.service_start_date
            False
            >>> i.service_time
            False
            >>> i.service_end_date
            False
            >>> i.id_number
            22
            >>> i.data_records
            {}
            >>> i.customer_class
            3

        Another example of an individual instance.
            >>> i = Individual(5)
            >>> i.arrival_date
            False
            >>> i.service_start_date
            False
            >>> i.service_time
            False
            >>> i.service_end_date
            False
            >>> i.id_number
            5
            >>> i.data_records
            {}
            >>> i.customer_class
            0
        """
        self.arrival_date = False
        self.service_start_date = False
        self.service_time = False
        self.service_end_date = False
        self.exit_date = False
        self.id_number = id_number
        self.data_records = {}
        self.customer_class = customer_class

    def __repr__(self):
        """
        Represents an Individual instance as a string

        An example of how an intance in represented.
            >>> i = Individual(3, 6)
            >>> i
            Individual 3

        Another example of how an individual is represented.
            >>> i = Individual(93, 2)
            >>> i
            Individual 93

        Although individuals should be represented by unique integers, they can be called anything.
            >>> i = Individual('twelve', 2)
            >>> i
            Individual twelve
        """
        return 'Individual %s' % self.id_number

class Node:
    """
    Class for a node on our network
    """
    def __init__(self, id_number, simulation):
        """
        Initialise a node.

        An example of initialising a node.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Node(1, Q)
            >>> N.mu
            [['Exponential', 7.0], ['Exponential', 7.0], ['Deterministic', 0.3]]
            >>> N.c
            9
            >>> N.transition_row
            [[0.1, 0.2, 0.1, 0.4], [0.6, 0.0, 0.0, 0.2], [0.0, 0.0, 0.4, 0.3]]
            >>> N.next_event_time
            2500
            >>> N.individuals
            []
            >>> N.id_number
            1
            >>> N.cum_transition_row
            [[0.1, 0.30000000000000004, 0.4, 0.8], [0.6, 0.6, 0.6, 0.8], [0.0, 0.0, 0.4, 0.7]]
        """

        self.simulation = simulation
        self.mu = [self.simulation.mu[cls][id_number-1] for cls in range(len(self.simulation.mu))]
        self.c = self.simulation.c[id_number-1]
        self.transition_row = [self.simulation.transition_matrix[j][id_number-1] for j in range(len(self.simulation.transition_matrix))]
        self.individuals = []
        self.id_number = id_number
        self.cum_transition_row = self.find_cum_transition_row()
        self.next_event_time = self.simulation.max_simulation_time

    def find_cum_transition_row(self):
        """
        Finds the cumulative transition row for the node

        An exmaple of finding the cumulative transition row of a node.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Node(1, Q)
            >>> N.cum_transition_row
            [[0.1, 0.30000000000000004, 0.4, 0.8], [0.6, 0.6, 0.6, 0.8], [0.0, 0.0, 0.4, 0.7]]
        """

        cum_transition_row = []
        for cls in range(len(self.transition_row)):
            sum_p = 0
            cum_transition_row.append([])
            for p in self.transition_row[cls]:
                sum_p += p
                cum_transition_row[cls].append(sum_p)
        return cum_transition_row

    def __repr__(self):
        """
        Representation of a node::

        An example of how a node is represented.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Node(1, Q)
            >>> N
            Node 1

        A node cannot exist without a simulation.
            >>> N = Node(2, False)
            Traceback (most recent call last):
            ...
            AttributeError: 'bool' object has no attribute 'mu'
        """
        return 'Node %s' % self.id_number

    def release(self):
        """
        Update node when a service happens.

        Once an individual is released, his exit date will be updated.
            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Q.transitive_nodes[0]
            >>> i = Individual(2, 0)
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
            0.02061
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
            1.02061
            >>> i.data_records[N.id_number][0].wait
            0.0

        A node can only release if it has an individual to release.
            >>> seed(2)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Q.transitive_nodes[0]
            >>> N.release()
            Traceback (most recent call last):
            ...
            IndexError: pop from empty list
        """
        next_individual = self.individuals.pop(0)

        next_individual.exit_date = self.next_event_time
        self.write_individual_record(next_individual)

        next_node = self.next_node(next_individual.customer_class)
        next_node.accept(next_individual, self.next_event_time)
        self.update_next_event_date()

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

        Accepting an individual updates a nodes next event date and appends that individual to its list of customers.
            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Node(1, Q)
            >>> next_individual = Individual(5, 0)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]
            >>> next_individual.arrival_date
            1
            >>> round(next_individual.service_time, 5)
            0.02061
            >>> round(N.next_event_time, 5)
            1.02061
            >>> N.accept(Individual(10), 1)
            >>> round(N.next_event_time, 5)
            1.02061
        """
        next_individual.arrival_date = current_time
        next_individual.service_time = self.simulation.service_times[self.id_number][next_individual.customer_class]()

        if len(self.individuals) < self.c:
            next_individual.end_service_date = current_time + next_individual.service_time
        else:
            next_individual.end_service_date = self.individuals[-self.c].end_service_date + next_individual.service_time

        self.include_individual(next_individual)
        self.update_next_event_date()

    def find_index_for_individual(self, individual):
        """
        Returns the index of the position that the new individual will take


            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(10)]
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
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(2)]
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
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(3)]
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
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(3)]
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
            >>> Q = Simulation('logs_test_for_simulation')
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
        Inserts that individual into the correct position in the list of individuals.

            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(10)]
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
            >>> seed(67)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(3)]
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
        """
        index = self.find_index_for_individual(individual)
        if index:
            self.individuals.insert(self.find_index_for_individual(individual), individual)
        else:
            self.individuals.append(individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

        A example of finding the next event time before and after accepting an individual.
            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals
            []
            >>> node.next_event_time
            2500
            >>> node.update_next_event_date()
            >>> node.next_event_time
            2500
            >>> ind = Individual(10)
            >>> node.accept(ind, 1)
            >>> node.update_next_event_date()
            >>> round(node.next_event_time, 5)
            1.02061

        And again.
            >>> seed(8)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[1]
            >>> node.individuals
            []
            >>> node.next_event_time
            2500
            >>> node.update_next_event_date()
            >>> node.next_event_time
            2500
            >>> ind = Individual(2)
            >>> node.accept(ind, 1)
            >>> node.update_next_event_date()
            >>> round(node.next_event_time, 5)
            1.03673
        """
        if len(self.individuals) == 0:
            self.next_event_time = self.simulation.max_simulation_time
        else:
            self.next_event_time = self.individuals[0].end_service_date

    def next_node(self, customer_class):
        """
        Finds the next node according the random distribution.

        An example showing a node choosing both nodes and exit node randomly.
            >>> seed(6)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[0]
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Exit Node
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 1
            >>> node.next_node(0)
            Node 4

        Another example.
            >>> seed(54)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> node = Q.transitive_nodes[2]
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2

        """
        rnd_num = random()
        for p in range(len(self.cum_transition_row[customer_class])):
            if rnd_num < self.cum_transition_row[customer_class][p]:
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

        An example showing the data records written; can only write records once an exit date has been determined.
            >>> seed(7)
            >>> Q = Simulation('logs_test_for_simulation')
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
            3.9441
            >>> round(ind.data_records[1][0].service_date, 5)
            6.9441
            >>> round(ind.data_records[1][0].service_time, 5)
            0.0559
            >>> ind.data_records[1][0].exit_date
            7
            >>> ind.data_records[1][0].node
            1

        Another example.
            >>> seed(12)
            >>> Q = Simulation('logs_test_for_simulation')
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
            2.90807
            >>> round(ind.data_records[1][0].service_date, 5)
            8.90807
            >>> round(ind.data_records[1][0].service_time, 5)
            0.09193
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


class ArrivalNode:
    """
    Class for the arrival node on our network
    """
    def __init__(self, simulation):
        """
        Initialise a node.

        Here is an example::
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = ArrivalNode(Q)
            >>> N.lmbda
            35.5
            >>> N.transition_row_given_class
            [[0.2, 0.4666666666666667, 0.26666666666666666, 0.06666666666666667], [0.13333333333333333, 0.2, 0.4, 0.26666666666666666], [0.36363636363636365, 0.18181818181818182, 0.36363636363636365, 0.09090909090909091]]
            >>> N.next_event_time
            0
            >>> N.number_of_individuals
            0
            >>> N.cum_transition_row
            [[0.2, 0.6666666666666667, 0.9333333333333333, 1.0], [0.13333333333333333, 0.33333333333333337, 0.7333333333333334, 1.0], [0.36363636363636365, 0.5454545454545454, 0.9090909090909091, 1.0]]
            >>> N.cum_class_probs
            [0.4225352112676056, 0.8450704225352113, 1.0]
        """

        self.simulation = simulation
        self.lmbda = self.simulation.overall_lmbda
        self.class_probs = self.simulation.class_probs
        self.transition_row_given_class = self.simulation.node_given_class_probs
        self.next_event_time = 0
        self.number_of_individuals = 0
        self.cum_transition_row = self.find_cumulative_transition_row()
        self.cum_class_probs = self.find_cumulative_class_probs()

    def find_cumulative_transition_row(self):
        """
        Finds the cumulative transition row for the arrival node

        An example of finding the cumulative transition row of an arrival node.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = ArrivalNode(Q)
            >>> [[round(pr, 2) for pr in N.cum_transition_row[cls]] for cls in range(len(N.cum_transition_row))]
            [[0.2, 0.67, 0.93, 1.0], [0.13, 0.33, 0.73, 1.0], [0.36, 0.55, 0.91, 1.0]]
        """

        cum_transition_row = []
        for cls in range(len(self.transition_row_given_class)):
            sum_p = 0
            cum_transition_row.append([])
            for p in self.transition_row_given_class[cls]:
                sum_p += p
                cum_transition_row[cls].append(sum_p)
        return cum_transition_row


    def find_cumulative_class_probs(self):
        """
        Returns the cumulative class probs

        An example of finding the cumulative probabilities of a new customer being in each class.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = ArrivalNode(Q)
            >>> N.find_cumulative_class_probs()
            [0.4225352112676056, 0.8450704225352113, 1.0]
        """

        cum_class_probs = []
        sum_p = 0
        for p in self.class_probs:
            sum_p += p
            cum_class_probs.append(sum_p)
        return cum_class_probs


    def __repr__(self):
        """
        Representation of a node::

        An example showing how an arrival node is represented.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = ArrivalNode(Q)
            >>> N
            Arrival Node
        """
        return 'Arrival Node'

    def release(self):
        """
        Update node when a service happens.

        An example of creating an individual instance, releasing it to a node, and then updating its next event time.
            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> Q.transitive_nodes[3].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.lmbda
            35.5
            >>> N.next_event_time
            0
            >>> N.release()
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            [Individual 1]
            >>> Q.transitive_nodes[3].individuals
            []
            >>> round(N.next_event_time,5)
            0.01927

        Another example.
            >>> seed(12)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> Q.transitive_nodes[3].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.next_event_time
            0
            >>> N.release()
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            [Individual 1]
            >>> Q.transitive_nodes[3].individuals
            []
            >>> round(N.next_event_time,5)
            0.00433
        """
        self.number_of_individuals += 1
        next_individual = Individual(self.number_of_individuals, self.choose_class())
        next_node = self.next_node(next_individual.customer_class)
        next_node.accept(next_individual, self.next_event_time)
        self.update_next_event_date()

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = ArrivalNode(Q)
            >>> N.next_event_time
            0
            >>> N.update_next_event_date()
            >>> round(N.next_event_time, 5)
            0.00406
        """
        self.next_event_time += expovariate(self.lmbda)

    def next_node(self, customer_class):
        """
        Finds the next node according the random distribution.

        An example of finding the individual's starting node.
            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Q.nodes[0]
            >>> N.cum_transition_row
            [[0.2, 0.6666666666666667, 0.9333333333333333, 1.0], [0.13333333333333333, 0.33333333333333337, 0.7333333333333334, 1.0], [0.36363636363636365, 0.5454545454545454, 0.9090909090909091, 1.0]]
            >>> N.next_node(0)
            Node 1
            >>> N.next_node(0)
            Node 3
            >>> N.next_node(0)
            Node 3

        And another example.
            >>> seed(401)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Q.nodes[0]
            >>> N.next_node(0)
            Node 2
            >>> N.next_node(0)
            Node 2
            >>> N.next_node(0)
            Node 3
        """
        rnd_num = random()
        for p in range(len(self.cum_transition_row[customer_class])):
            if rnd_num < self.cum_transition_row[customer_class][p]:
                return self.simulation.transitive_nodes[p]

    def choose_class(self):
        """
        Returns the customer's class from the class probabilities

            >>> seed(6)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = ArrivalNode(Q)
            >>> N.choose_class()
            1
        """

        rnd_num = random()
        for p in range(len(self.cum_class_probs)):
            if rnd_num < self.cum_class_probs[p]:
                return p


class ExitNode:
    """
    Class for the exit node on our network
    """
    def __init__(self, max_simulation_time):
        """
        Initialise a node.

        An example of an exit node instance.
            >>> N = ExitNode(100)
            >>> N.individuals
            []
            >>> N.id_number
            -1
            >>> N.next_event_time
            100

        And another.
            >>> N = ExitNode(4)
            >>> N.id_number
            -1
            >>> N.next_event_time
            4
        """
        self.individuals = []
        self.id_number = -1
        self.next_event_time = max_simulation_time

    def __repr__(self):
        """
        Representation of a node::

        An example of how an exit node is represented.
            >>> N = ExitNode(500)
            >>> N
            Exit Node

        And another.
            >>> N = ExitNode(320)
            >>> N
            Exit Node
        """
        return 'Exit Node'

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

        An example of a customer leaving the system (getting accepted to the exit node).
            >>> N = ExitNode(200)
            >>> N.individuals
            []
            >>> N.next_event_time
            200
            >>> next_individual = Individual(5, 1)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]
            >>> N.next_event_time
            200

        Another example.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Q.nodes[-1]
            >>> N.individuals
            []
            >>> N.next_event_time
            2500
            >>> next_individual = Individual(3)
            >>> N.accept(next_individual, 3)
            >>> N.individuals
            [Individual 3]
            >>> N.next_event_time
            2500
        """
        self.individuals.append(next_individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

        An example showing that this method does nothing.
            >>> N = ExitNode(25)
            >>> N.next_event_time
            25
            >>> N.update_next_event_date()
            >>> N.next_event_time
            25

        And again.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> N = Q.nodes[-1]
            >>> N.next_event_time
            2500
            >>> N.update_next_event_date()
            >>> N.next_event_time
            2500

        And again, even when parameters don't make sense.
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
    def __init__(self, directory_name, sffx=None):
        """
        Initialise a queue instance.

        Here is an example::

        An example of creating a simulation instance.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> Q.lmbda
            [[3.0, 7.0, 4.0, 1.0], [2.0, 3.0, 6.0, 4.0], [2.0, 1.0, 2.0, 0.5]]
            >>> Q.mu
            [[['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]], [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]]]
            >>> Q.c
            [9, 10, 8, 8]
            >>> Q.transition_matrix
            [[[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]], [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]]]
            >>> Q.nodes
            [Arrival Node, Node 1, Node 2, Node 3, Node 4, Exit Node]
            >>> Q.transitive_nodes
            [Node 1, Node 2, Node 3, Node 4]
            >>> Q.max_simulation_time
            2500
        """

        self.directory = os.path.dirname(os.path.realpath(__file__)) + '/' + directory_name + '/'
        self.sffx = sffx
        self.parameters = self.load_parameters()
        self.lmbda = [self.parameters['Arrival_rates']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        self.overall_lmbda = sum([sum(self.lmbda[i]) for i in range(len(self.lmbda))])
        self.class_probs = [sum(self.lmbda[i])/self.overall_lmbda for i in range(len(self.lmbda))]
        self.node_given_class_probs = [[self.lmbda[j][i]/(self.class_probs[j]*self.overall_lmbda) for i in range(len(self.lmbda[0]))] for j in range(len(self.lmbda))]
        self.mu = [self.parameters['Service_rates']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        self.c = self.parameters['Number_of_servers']
        self.transition_matrix = [self.parameters['Transition_matrices']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        self.max_simulation_time = self.parameters['Simulation_time']
        self.transitive_nodes = [Node(i + 1, self) for i in range(len(self.c))]
        self.nodes = [ArrivalNode(self)] + self.transitive_nodes + [ExitNode(self.max_simulation_time)]
        self.number_of_nodes = len(self.transitive_nodes)
        self.service_times = self.find_service_time_dictionary()

        if len(self.lmbda) != len(self.mu) or len(self.lmbda) != len(self.transition_matrix) or len(self.mu) != len(self.transition_matrix):
            raise ValueError('Lambda, Mu and the Transition Matrix should all have the same number of classes')

        if any(len(lmbdacls) != len(self.c) for lmbdacls in self.lmbda):
            raise ValueError('Lambda should have same length as c for every class')

        if any(len(mucls) != len(self.c) for mucls in self.mu):
            raise ValueError('Mu should have same length as c for every class')

        if any(len(transmatrxcls) != len(self.c) for transmatrxcls in self.transition_matrix):
            raise ValueError('Transition matrix should be square matrix of length c for every class')

        if any(len(transmatrxrow) != len(self.c) for transmatrxcls in self.transition_matrix for transmatrxrow in transmatrxcls):
            raise ValueError('Transition matrix should be square matrix of length c for every class')

        if any(l < 0 for lmbdaclass in self.lmbda for l in lmbdaclass):
            raise ValueError('All arrival rates should be positive')

        if any(type(k) is not int or k <= 0 for k in self.c):
            raise ValueError('All servers must be positive integer number')

        if any(tmval < 0 for transmatrxcls in self.transition_matrix for transmatrxrow in transmatrxcls for tmval in transmatrxrow) or any(tmval > 1 for transmatrxcls in self.transition_matrix for transmatrxrow in transmatrxcls for tmval in transmatrxrow) or any(sum(transmatrxrow) > 1 for transmatrxcls in self.transition_matrix for transmatrxrow in transmatrxcls):
            raise ValueError('All transition matrix entries should be probabilities 0<=p<=1 and all transition matrix rows should sum to 1 or less')

        if self.max_simulation_time < 0:
            raise ValueError('Maximum simulation time should be positive')

    def load_parameters(self):
        parameter_file_name = self.directory + 'parameters.yml'
        parameter_file = open(parameter_file_name, 'r')
        parameters = yaml.load(parameter_file)
        parameter_file.close()
        return parameters

    def find_next_active_node(self):
        """
        Return the next active node:

        A mock example testing if this method works.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> i = 0
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i += 1
            >>> Q.find_next_active_node()
            Arrival Node

        And again.
            >>> Q = Simulation('logs_test_for_simulation')
            >>> i = 10
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i -= 1
            >>> Q.find_next_active_node()
            Node 4
        """
        return min(self.nodes, key=lambda x: x.next_event_time)

    def find_service_time(self, n, c):
        """
        Finds the service time function
        """

        if self.mu[c][n][0] == 'Uniform':
            return lambda : uniform(self.mu[c][n][1], self.mu[c][n][2])
        if self.mu[c][n][0] == 'Deterministic':
            return lambda : self.mu[c][n][1]
        if self.mu[c][n][0] == 'Triangular':
            return lambda : triangular(self.mu[c][n][1], self.mu[c][n][2], self.mu[c][n][3])
        if self.mu[c][n][0] == 'Exponential':
            return lambda : expovariate(self.mu[c][n][1])
        if self.mu[c][n][0] == 'Gamma':
            return lambda : gammavariate(self.mu[c][n][1], self.mu[c][n][2])
        if self.mu[c][n][0] == 'Normal':
            return lambda : gauss(self.mu[c][n][1], self.mu[c][n][2])
        if self.mu[c][n][0] == 'Lognormal':
            return lambda : lognormvariate(self.mu[c][n][1], self.mu[c][n][2])
        if self.mu[c][n][0] == 'Weibull':
            return lambda : weibullvariate(self.mu[c][n][1], self.mu[c][n][2])
        return False

    def find_service_time_dictionary(self):
        """
        Finds the dictionary of service time functions for each node for each class
        """
        return {node+1:{customer_class:self.find_service_time(node, customer_class) for customer_class in range(len(self.lmbda))} for node in range(self.number_of_nodes)}

    def simulate(self):
        """
        Run the actual simulation.

        An example of simulating the simulation.
            >>> seed(99)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> Q.simulate()
            >>> Q.get_all_individuals()[0]
            Individual 88781
        """
        next_active_node = self.find_next_active_node()
        while next_active_node.next_event_time < self.max_simulation_time:
            next_active_node.release()
            next_active_node = self.find_next_active_node()

    def get_all_individuals(self):
        """
        Returns list of all individuals with at least one record

        An example of obtaining the list of all individuals who completed service.
            >>> seed(1)
            >>> Q = Simulation('logs_test_for_simulation')
            >>> Q.max_simulation_time = 0.5
            >>> Q.simulate()
            >>> Q.get_all_individuals()
            [Individual 12, Individual 2, Individual 1, Individual 3, Individual 7, Individual 4, Individual 5, Individual 6, Individual 14, Individual 9]

        """
        return [individual for node in self.nodes[1:] for individual in node.individuals if len(individual.data_records) > 0]

    def write_records_to_file(self):
        """
        Writes the records for all individuals to a csv file
        """
        if self.sffx:
            data_file = open('%sdata_' %self.directory + self.sffx + '.csv', 'w')
        else:
            data_file = open('%sdata.csv' % self.directory, 'w')
        csv_wrtr = writer(data_file)
        for individual in self.get_all_individuals():
            for node in individual.data_records:
                for record in individual.data_records[node]:
                    csv_wrtr.writerow([individual.id_number,
                                       individual.customer_class,
                                       node,
                                       record.arrival_date,
                                       record.wait,
                                       record.service_date,
                                       record.service_time,
                                       record.exit_date])
        data_file.close()


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    dirname = arguments['<dir_name>']
    sffx = arguments['<sffx>']
    Q = Simulation(dirname, sffx)
    Q.simulate()
    Q.write_records_to_file()
