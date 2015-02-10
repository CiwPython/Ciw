"""
Usage: simulation.py <dir_name> [<sffx>]

Arguments
    dir_name    : name of the directory from which to read in parameters and write data files
    suff        : optional suffix to add to the data file name

Options
    -h          : displays this help file
"""

from __future__ import division
from random import random, seed, choice, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
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
    def __init__(self, arrival_date, service_time, exit_date, node):
        """
        An example of a data record instance.
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

        Another example of a data record instance.
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

        If parameters don't make sense, errors occur.
            >>> r = DataRecord(4, 2.5, 3, 3)
            Traceback (most recent call last):
            ...
            ValueError: Arrival date should preceed exit date

            >>> r = DataRecord(4, -2, 7, 1)
            Traceback (most recent call last):
            ...
            ValueError: Service time should be positive

        """
        if exit_date < arrival_date:
            raise ValueError('Arrival date should preceed exit date')

        if service_time < 0:
            raise ValueError('Service time should be positive')

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
    def __init__(self, id_number, customer_class=0):
        """
        Initialise an individual

        An example of an Individual instance.
            >>> i = Individual(22, 3)
            >>> i.in_service
            False
            >>> i.end_service_date
            False
            >>> i.id_number
            22
            >>> i.data_records
            {}
            >>> i.customer_class
            3

        Another example of an individual instance.
            >>> i = Individual(5)
            >>> i.in_service
            False
            >>> i.end_service_date
            False
            >>> i.id_number
            5
            >>> i.customer_class
            0
            >>> i.data_records
            {}
        """
        self.in_service = False
        self.end_service_date = False
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = Node(1, Q)
            >>> N.mu
            [['Exponential', 8.0], ['Exponential', 5.0]]
            >>> N.c
            8
            >>> N.neighbours
            {0: [1, 3], 1: [1, 2, 3]}
            >>> N.next_event_time
            2000
            >>> N.individuals
            []
            >>> N.id_number
            1
        """

        self.simulation = simulation
        self.mu = [self.simulation.mu[cls][id_number-1] for cls in range(len(self.simulation.mu))]
        self.c = self.simulation.c[id_number-1]
        self.exit_rate = [self.simulation.exit_rates[cls][id_number-1] for cls in range(len(self.simulation.exit_rates))]
        self.individuals = []
        self.id_number = id_number
        self.neighbours = {cls:[i+1 for i in range(self.simulation.number_of_nodes) if self.simulation.neighbours_matrix[cls][self.id_number-1][i]] for cls in range(self.simulation.number_of_classes)}
        self.next_event_time = self.simulation.max_simulation_time
        self.learning_rate = 0.1
        self.discount_rate = 0.9
        self.action_selection_parameter = 0.6
        self.Vs = {}
        self.Qs = {}

    def __repr__(self):
        """
        Representation of a node::

        An example of how a node is represented.
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = Q.transitive_nodes[0]
            >>> N.id_number
            1
            >>> N.neighbours
            {0: [1, 3], 1: [1, 2, 3]}
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
            0.01804
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
            1.01804
            >>> i.data_records[N.id_number][0].wait
            0.0

        A node can only release if it has an individual to release.
            >>> seed(2)
            >>> Q = Simulation('logs_test_for_qlearn')
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

        if next_node.id_number != -1:
            reward = self.simulation.find_reward()
            self.update_Qs_and_Vs(next_node.id_number, reward, next_individual.customer_class)
        self.update_next_event_date()

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

        Accepting an individual updates a nodes next event date and appends that individual to its list of customers.
            >>> seed(1)
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = Node(1, Q)
            >>> next_individual = Individual(5, 0)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]
            >>> next_individual.arrival_date
            1
            >>> round(next_individual.service_time, 5)
            0.01804
            >>> round(N.next_event_time, 5)
            1.01804
            >>> N.accept(Individual(10), 1)
            >>> round(N.next_event_time, 5)
            1.01804
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals
            []
            >>> node.next_event_time
            2000
            >>> node.update_next_event_date()
            >>> node.next_event_time
            2000
            >>> ind = Individual(10)
            >>> node.accept(ind, 1)
            >>> node.update_next_event_date()
            >>> round(node.next_event_time, 5)
            1.01804

        And again.
            >>> seed(8)
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> node = Q.transitive_nodes[1]
            >>> node.individuals
            []
            >>> node.next_event_time
            2000
            >>> node.update_next_event_date()
            >>> node.next_event_time
            2000
            >>> ind = Individual(2)
            >>> node.accept(ind, 1)
            >>> node.update_next_event_date()
            >>> round(node.next_event_time, 5)
            1.02857
        """
        if len(self.individuals) == 0:
            self.next_event_time = self.simulation.max_simulation_time
        else:
            self.next_event_time = self.individuals[0].end_service_date

    def next_node(self, customer_class):
        """
        Selects a node to send the customer using the epsilon-soft policy
        """
        rnd_num = random()
        if rnd_num < self.exit_rate[customer_class]: # Does the customer exit the system?
            return self.simulation.nodes[-1]
        else: # Else, have we visited the current state before?
            rnd_num = random()
            self.simulation.find_network_state()
            if self.simulation.state in self.Qs:
                if rnd_num < 1 - self.simulation.action_selection_parameter:
                    return self.simulation.nodes[max(self.Qs[self.simulation.state][customer_class], key=lambda x: self.Qs[self.simulation.state][customer_class][x])]
                else:
                    return self.simulation.nodes[choice(self.neighbours[customer_class])]
            else:
                self.Qs[self.simulation.state] = {cls:{neighbour:0 for neighbour in self.neighbours[cls]} for cls in range(self.simulation.number_of_classes)}
                self.Vs[self.simulation.state] = {cls:0 for cls in range(self.simulation.number_of_classes)}
                return self.simulation.nodes[choice(self.neighbours[customer_class])]

    def update_Qs_and_Vs(self, next_node_id, reward, customer_class):
        """
        Updates the Qs and Vs values for the node
        """
        self.Qs[self.simulation.state][customer_class][next_node_id] = (1 - self.simulation.learning_rate)*self.Qs[self.simulation.state][customer_class][next_node_id] + self.simulation.learning_rate*(reward + self.simulation.discount_rate*self.Vs[self.simulation.state][customer_class])
        self.Vs[self.simulation.state][customer_class] = max(self.Qs[self.simulation.state][customer_class].values())

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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            3.95109
            >>> round(ind.data_records[1][0].service_date, 5)
            6.95109
            >>> round(ind.data_records[1][0].service_time, 5)
            0.04891
            >>> ind.data_records[1][0].exit_date
            7
            >>> ind.data_records[1][0].node
            1

        Another example.
            >>> seed(12)
            >>> Q = Simulation('logs_test_for_qlearn')
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
            2.91956
            >>> round(ind.data_records[1][0].service_date, 5)
            8.91956
            >>> round(ind.data_records[1][0].service_time, 5)
            0.08044
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = ArrivalNode(Q)
            >>> N.lmbda
            25.0
            >>> N.transition_row_given_class
            [[0.45454545454545453, 0.18181818181818182, 0.36363636363636365], [0.21428571428571425, 0.49999999999999994, 0.2857142857142857]]
            >>> N.next_event_time
            0
            >>> N.number_of_individuals
            0
            >>> N.cum_transition_row
            [[0.45454545454545453, 0.6363636363636364, 1.0], [0.21428571428571425, 0.7142857142857142, 0.9999999999999999]]
            >>> N.cum_class_probs
            [0.44, 1.0]
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = ArrivalNode(Q)
            >>> [[round(pr, 2) for pr in N.cum_transition_row[cls]] for cls in range(len(N.cum_transition_row))]
            [[0.45, 0.64, 1.0], [0.21, 0.71, 1.0]]
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = ArrivalNode(Q)
            >>> N.find_cumulative_class_probs()
            [0.44, 1.0]
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.lmbda
            25.0
            >>> N.next_event_time
            0
            >>> N.release()
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            [Individual 1]
            >>> round(N.next_event_time,5)
            0.01178

        Another example.
            >>> seed(12)
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.next_event_time
            0
            >>> N.release()
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            [Individual 1]
            >>> Q.transitive_nodes[2].individuals
            []
            >>> round(N.next_event_time,5)
            0.00615
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = ArrivalNode(Q)
            >>> N.next_event_time
            0
            >>> N.update_next_event_date()
            >>> round(N.next_event_time, 5)
            0.00577
        """
        self.next_event_time += expovariate(self.lmbda)

    def next_node(self, customer_class):
        """
        Finds the next node according the random distribution.

        An example of finding the individual's starting node.
            >>> seed(1)
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = Q.nodes[0]
            >>> N.cum_transition_row
            [[0.45454545454545453, 0.6363636363636364, 1.0], [0.21428571428571425, 0.7142857142857142, 0.9999999999999999]]
            >>> N.next_node(0)
            Node 1
            >>> N.next_node(0)
            Node 3
            >>> N.next_node(0)
            Node 3

        And another example.
            >>> seed(401)
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = Q.nodes[0]
            >>> N.next_node(0)
            Node 2
            >>> N.next_node(0)
            Node 1
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
            >>> Q = Simulation('logs_test_for_qlearn')
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = Q.nodes[-1]
            >>> N.individuals
            []
            >>> N.next_event_time
            2000
            >>> next_individual = Individual(3)
            >>> N.accept(next_individual, 3)
            >>> N.individuals
            [Individual 3]
            >>> N.next_event_time
            2000
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> N = Q.nodes[-1]
            >>> N.next_event_time
            2000
            >>> N.update_next_event_date()
            >>> N.next_event_time
            2000

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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> Q.lmbda
            [[5.0, 2.0, 4.0], [3.0, 7.0, 4.0]]
            >>> Q.mu
            [[['Exponential', 8.0], ['Exponential', 9.0], ['Exponential', 6.0]], [['Exponential', 5.0], ['Exponential', 4.0], ['Exponential', 9.0]]]
            >>> Q.c
            [8, 6, 6]
            >>> Q.neighbours_matrix
            [[[True, False, True], [True, True, True], [False, True, True]], [[True, True, True], [False, True, True], [True, True, False]]]
            >>> Q.nodes
            [Arrival Node, Node 1, Node 2, Node 3, Exit Node]
            >>> Q.transitive_nodes
            [Node 1, Node 2, Node 3]
            >>> Q.max_simulation_time
            2000
        """

        self.directory = os.path.dirname(os.path.realpath(__file__)) + '/' + directory_name + '/'
        self.sffx = sffx
        self.parameters = self.load_parameters()
        self.number_of_classes = self.parameters['Number_of_classes']
        self.number_of_nodes = len(self.parameters['Arrival_rates']['Class 0'])
        self.lmbda = [self.parameters['Arrival_rates']['Class ' + str(i)] for i in range(self.number_of_classes)]
        self.overall_lmbda = sum([sum(self.lmbda[i]) for i in range(len(self.lmbda))])
        self.class_probs = [sum(self.lmbda[i])/self.overall_lmbda for i in range(len(self.lmbda))]
        self.node_given_class_probs = [[self.lmbda[j][i]/(self.class_probs[j]*self.overall_lmbda) for i in range(len(self.lmbda[0]))] for j in range(len(self.lmbda))]
        self.mu = [self.parameters['Service_rates']['Class ' + str(i)] for i in range(self.number_of_classes)]
        self.c = self.parameters['Number_of_servers']
        self.neighbours_matrix = [self.parameters['Neighbours_matrices']['Class ' + str(i)] for i in range(self.number_of_classes)]
        self.exit_rates = [self.parameters['Exit_rates']['Class ' + str(i)] for i in range(self.number_of_classes)]
        self.max_simulation_time = self.parameters['Simulation_time']
        self.transitive_nodes = [Node(i + 1, self) for i in range(len(self.c))]
        self.nodes = [ArrivalNode(self)] + self.transitive_nodes + [ExitNode(self.max_simulation_time)]
        self.service_times = self.find_service_time_dictionary()
        self.action_selection_parameter = self.parameters['Action_selection_parameter']
        self.learning_rate = self.parameters['Learning_rate']
        self.discount_rate = self.parameters['Discount_rate']

        if len(self.lmbda) != len(self.mu) or len(self.lmbda) != len(self.neighbours_matrix) or len(self.mu) != len(self.neighbours_matrix):
            raise ValueError('Lambda, Mu and the Transition Matrix should all have the same number of classes')

        if any(len(lmbdacls) != len(self.c) for lmbdacls in self.lmbda):
            raise ValueError('Lambda should have same length as c for every class')

        if any(len(mucls) != len(self.c) for mucls in self.mu):
            raise ValueError('Mu should have same length as c for every class')

        if any(l < 0 for lmbdaclass in self.lmbda for l in lmbdaclass):
            raise ValueError('All arrival rates should be positive')

        if any(type(k) is not int or k <= 0 for k in self.c):
            raise ValueError('All servers must be positive integer number')

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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> i = 0
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i += 1
            >>> Q.find_next_active_node()
            Arrival Node

        And again.
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> i = 10
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i -= 1
            >>> Q.find_next_active_node()
            Node 3
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

    def find_network_state(self):
        """
        Finds the state of the queueing network and converts to a hashable state

            >>> Q = Simulation('logs_test_for_qlearn')
            >>> Q.find_network_state()
            >>> Q.state
            '[0, 0, 0]'
        """
        network_state = [len(n.individuals) for n in self.transitive_nodes]
        self.state = str(network_state)

    def find_reward(self):
        """
        Finds the reward associated with the action last taken
        """
        return 0


    def simulate(self):
        """
        Run the actual simulation.

        An example of simulating the simulation.
            >>> seed(99)
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> Q.simulate()
            >>> Q.get_all_individuals()[0]
            Individual 49917
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
            >>> Q = Simulation('logs_test_for_qlearn')
            >>> Q.max_simulation_time = 0.5
            >>> Q.simulate()
            >>> Q.get_all_individuals()
            [Individual 13, Individual 21, Individual 6, Individual 3, Individual 10, Individual 4, Individual 1, Individual 18, Individual 15, Individual 14, Individual 11, Individual 8, Individual 7, Individual 9, Individual 2]
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
