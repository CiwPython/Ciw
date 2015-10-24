from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import networkx as nx
from node import Node
from arrival_node import ArrivalNode
from exit_node import ExitNode
from server import Server
from individual import Individual
from data_record import DataRecord


class Simulation:
    """
    Overall simulation class
    """
    def __init__(self, parameters):
        """
        Initialise a queue instance.

        Here is an example::

        An example of creating a simulation instance.
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
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

        self.parameters = parameters
        self.digraph = nx.DiGraph()
        self.lmbda = [self.parameters['Arrival_rates']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        self.overall_lmbda = sum([sum(self.lmbda[i]) for i in range(len(self.lmbda))])
        self.class_probs = [sum(self.lmbda[i])/self.overall_lmbda for i in range(len(self.lmbda))]
        self.node_given_class_probs = [[self.lmbda[j][i]/(self.class_probs[j]*self.overall_lmbda) for i in range(len(self.lmbda[0]))] for j in range(len(self.lmbda))]
        self.mu = [self.parameters['Service_rates']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        self.c = self.parameters['Number_of_servers']
        self.queue_capacities = self.parameters['Queue_capacities']
        self.transition_matrix = [self.parameters['Transition_matrices']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        self.max_simulation_time = self.parameters['Simulation_time']
        self.transitive_nodes = [Node(i + 1, self) for i in range(len(self.c))]
        self.nodes = [ArrivalNode(self)] + self.transitive_nodes + [ExitNode("Inf")]
        self.number_of_nodes = len(self.transitive_nodes)
        self.service_times = self.find_service_time_dictionary()
        self.order = sum([nd.c for nd in self.transitive_nodes])
        self.state = [[0, 0] for i in range(self.number_of_nodes)]
        initial_state = [[0, 0] for i in range(self.number_of_nodes)]
        self.times_dictionary = {tuple(tuple(initial_state[i]) for i in range(self.number_of_nodes)): 0.0}

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


    def find_next_active_node(self):
        """
        Return the next active node:

        A mock example testing if this method works.
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> i = 0
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_date = i
            ...     i += 1
            >>> Q.find_next_active_node()
            Arrival Node

        And again.
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> i = 10
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_date = i
            ...     i -= 1
            >>> Q.find_next_active_node()
            Node 4
        """
        return min(self.nodes, key=lambda x: x.next_event_date)

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

    def simulate_until_max_time(self):
        """
        Run the actual simulation.

            >>> seed(3)
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> Q.simulate_until_max_time()
        """
        self.nodes[0].update_next_event_date()
        next_active_node = self.find_next_active_node()
        current_time = next_active_node.next_event_date
        while current_time < self.max_simulation_time:
            next_active_node.have_event()
            for node in self.transitive_nodes:
                node.update_next_event_date(current_time)
            next_active_node = self.find_next_active_node()
            current_time = next_active_node.next_event_date

    def simulate_until_deadlock(self):
        """
        Run the actual simulation.

            >>> seed(3)
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_deadlock_sim/'))
            >>> times = Q.simulate_until_deadlock()
            >>> times[((0, 0), (0, 0))]
            8.699770274666774
        """
        deadlocked = False
        self.nodes[0].update_next_event_date()
        next_active_node = self.find_next_active_node()
        current_time = next_active_node.next_event_date
        while not deadlocked:
            next_active_node.have_event()

            current_state = tuple(tuple(self.state[i]) for i in range(len(self.state)))
            if current_state not in self.times_dictionary:
                self.times_dictionary[current_state] = current_time

            for node in self.transitive_nodes:
                node.update_next_event_date(current_time)
            deadlocked = self.detect_deadlock()

            if deadlocked:
                time_of_deadlock = current_time

            next_active_node = self.find_next_active_node()
            current_time = next_active_node.next_event_date

        return {state: time_of_deadlock - self.times_dictionary[state] for state in self.times_dictionary.keys()}

    def detect_deadlock(self):
        """
        Detects whether the system is in a deadlocked state, that is, is there a knot

        Note that this code is taken and adapted from the NetworkX Developer Zone Ticket #663 knot.py (09/06/2015)

            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> nodes = ['A', 'B', 'C', 'D', 'E']
            >>> connections = [('A', 'D'), ('A', 'B'), ('B', 'E'), ('C', 'B'), ('E', 'C')]
            >>> for nd in nodes:
            ...     Q.digraph.add_node(nd)
            >>> for cnctn in connections:
            ...     Q.digraph.add_edge(cnctn[0], cnctn[1])
            >>> Q.detect_deadlock()
            True

            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> nodes = ['A', 'B', 'C', 'D']
            >>> connections = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D')]
            >>> for nd in nodes:
            ...     Q.digraph.add_node(nd)
            >>> for cnctn in connections:
            ...     Q.digraph.add_edge(cnctn[0], cnctn[1])
            >>> Q.detect_deadlock()
            False

            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> nodes = ['A', 'B']
            >>> for nd in nodes:
            ...     Q.digraph.add_node(nd)
            >>> Q.detect_deadlock()
            False
            >>> connections = [('A', 'A')]
            >>> for cnctn in connections:
            ...     Q.digraph.add_edge(cnctn[0], cnctn[1])
            >>> Q.detect_deadlock()
            True
        """
        knots = []
        for subgraph in nx.strongly_connected_component_subgraphs(self.digraph):
            nodes = set(subgraph.nodes())
            if len(nodes) == 1:
                n = nodes.pop()
                nodes.add(n)
                if set(self.digraph.successors(n)) == nodes:
                    knots.append(subgraph)
            else:
                for n in nodes:
                    successors = nx.descendants(self.digraph, n)
                    if not successors <= nodes:
                        break
                else:
                    knots.append(subgraph)
        if len(knots) > 0:
            return True
        return False

    def get_all_individuals(self):
        """
        Returns list of all individuals with at least one record
        """
        return [individual for node in self.nodes[1:] for individual in node.individuals if len(individual.data_records) > 0]

    def write_records_to_file(self, directory_name):
        """
        Writes the records for all individuals to a csv file
        """
        root = os.getcwd()
        directory = os.path.join(root, directory_name)
        data_file = open('%sdata.csv' % directory, 'w')
        csv_wrtr = writer(data_file)
        for individual in self.get_all_individuals():
            for node in individual.data_records:
                for record in individual.data_records[node]:
                    csv_wrtr.writerow([individual.id_number,
                                       individual.customer_class,
                                       node,
                                       record.arrival_date,
                                       record.wait,
                                       record.service_start_date,
                                       record.service_time,
                                       record.service_end_date,
                                       record.blocked,
                                       record.exit_date])
        data_file.close()