from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
import os
from csv import writer
import yaml
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
    def __init__(self, *args, **kwargs):
        """
        Initialise a queue instance.
        """
        if args:  # Catching if dictionary is passed
            parameters = args[0]
        else:
            parameters = kwargs
        self.parameters = parameters

        if set(['arrival_rate', 'number_of_servers',
            'service_rate', 'Simulation_time']) == set(self.parameters.keys()):
            self.parameters = self.build_mmc_parameters(self.parameters['arrival_rate'],
                                                   self.parameters['service_rate'],
                                                   self.parameters['number_of_servers'],
                                                   self.parameters['Simulation_time'])

        # Default arguments
        default_dict ={'Number_of_nodes': len(self.parameters['Number_of_servers']),
                       'Number_of_classes': len(self.parameters['Arrival_rates']),
                       'Queue_capacities': ['Inf' for _ in
                                            range(len(self.parameters['Number_of_servers']))],
                       'detect_deadlock': False}
        for a in default_dict:
            self.parameters[a] = self.parameters.get(a, default_dict[a])


        self.c = self.parameters['Number_of_servers']
        self.number_of_nodes = self.parameters['Number_of_nodes']
        self.detecting_deadlock = self.parameters['detect_deadlock']
        self.digraph = nx.DiGraph()
        self.lmbda = [self.parameters['Arrival_rates']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        
        if any(len(lmbdacls) != len(self.c) for lmbdacls in self.lmbda):
            raise ValueError('Lambda should have same length as c for every class')
        if any(l < 0 for lmbdaclass in self.lmbda for l in lmbdaclass):
            raise ValueError('All arrival rates should be positive')


        self.mu = [self.parameters['Service_distributions']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        
        if any(len(mucls) != len(self.c) for mucls in self.mu):
            raise ValueError('Mu should have same length as c for every class')

        self.schedules = [False for i in range(len(self.c))]
        for i in range(len(self.c)):
            if type(self.c[i])==type('string') and self.c[i]!='Inf':
                self.schedules[i] =  True
        self.queue_capacities = self.parameters['Queue_capacities']
        self.transition_matrix = [self.parameters['Transition_matrices']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]

        if any(len(transmatrxcls) != len(self.c) for transmatrxcls in self.transition_matrix):
            raise ValueError('Transition matrix should be square matrix of length c for every class')
        if any(tmval < 0 for transmatrxcls in self.transition_matrix for transmatrxrow in transmatrxcls for tmval in transmatrxrow) or any(tmval > 1 for transmatrxcls in self.transition_matrix for transmatrxrow in transmatrxcls for tmval in transmatrxrow) or any(sum(transmatrxrow) > 1 for transmatrxcls in self.transition_matrix for transmatrxrow in transmatrxcls):
            raise ValueError('All transition matrix entries should be probabilities 0<=p<=1 and all transition matrix rows should sum to 1 or less')

        if 'Class_change_matrices' in self.parameters:
            self.class_change_matrix = [self.parameters['Class_change_matrices']['Node ' + str(i)] for i in range(self.parameters['Number_of_nodes'])]
        else:
            self.class_change_matrix = 'NA'

        self.max_simulation_time = self.parameters['Simulation_time']

        if self.max_simulation_time < 0:
            raise ValueError('Maximum simulation time should be positive')

        self.transitive_nodes = [Node(i + 1, self) for i in range(len(self.c))]
        self.nodes = [ArrivalNode(self)] + self.transitive_nodes + [ExitNode("Inf")]
        self.service_times = self.find_service_time_dictionary()
        self.state = [[0, 0] for i in range(self.number_of_nodes)]
        initial_state = [[0, 0] for i in range(self.number_of_nodes)]
        self.times_dictionary = {tuple(tuple(initial_state[i]) for i in range(self.number_of_nodes)): 0.0}


    def build_mmc_parameters(self, arrival_rate, service_rate, number_of_servers, Simulation_time):
        """
        Builds the parameters dictionary for an M/M/C queue
        """
        return {'Arrival_rates' : {'Class 0' : [arrival_rate]},
                'Service_distributions' : {'Class 0' : [['Exponential', service_rate]]},
                'Transition_matrices' : {'Class 0' : [[0.0]]},
                'Number_of_servers' : [number_of_servers],
                'Number_of_nodes' : 1,
                'Number_of_classes' : 1,
                'Queue_capacities' : ['Inf'],
                'Simulation_time' : Simulation_time}


    def find_next_active_node(self):
        """
        Return the next active node:
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
        if self.mu[c][n][0] == 'Lognormal':
            return lambda : lognormvariate(self.mu[c][n][1], self.mu[c][n][2])
        if self.mu[c][n][0] == 'Weibull':
            return lambda : weibullvariate(self.mu[c][n][1], self.mu[c][n][2])
        if self.mu[c][n][0] == 'Custom':
            P, V = zip(*self.parameters[self.mu[c][n][1]])
            probs = list(P)
            cum_probs = [sum(probs[0:i+1]) for i in range(len(probs))]
            values = list(V)
            return lambda : self.custom_pdf(cum_probs, values)
        return False

    def custom_pdf(self, cum_probs, values):
        """
        Samples from a custom pdf
        """
        rnd_num = random()
        for p in range(len(cum_probs)):
            if rnd_num < cum_probs[p]:
                return values[p]

    def find_service_time_dictionary(self):
        """
        Finds the dictionary of service time functions for each node for each class
        """
        return {node+1:{customer_class:self.find_service_time(node, customer_class) for customer_class in range(len(self.lmbda))} for node in range(self.number_of_nodes)}

    def simulate_until_max_time(self):
        """
        Run the actual simulation.
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
                    if successors <= nodes:
                        knots.append(subgraph)
                        break
        if len(knots) > 0:
            return True
        return False

    def get_all_individuals(self):
        """
        Returns list of all individuals with at least one record
        """
        return [individual for node in self.nodes[1:] for individual in node.individuals if len(individual.data_records) > 0]

    def get_all_records(self, headers=True):
        """
        Gets all records from all individuals
        """
        records = []
        if headers:
            records.append(['I.D. Number', 'Customer Class', 'Node', 'Arrival Date', 'Waiting Time', 'Service Start Date', 'Service Time', 'Service End Date', 'Time Blocked', 'Exit Date'])
        for individual in self.get_all_individuals():
            for node in individual.data_records:
                for record in individual.data_records[node]:
                    records.append([individual.id_number,
                                    record.customer_class,
                                    node,
                                    record.arrival_date,
                                    record.wait,
                                    record.service_start_date,
                                    record.service_time,
                                    record.service_end_date,
                                    record.blocked,
                                    record.exit_date])
        self.all_records = records
        return records

    def write_records_to_file(self, file_name, headers=True):
        """
        Writes the records for all individuals to a csv file
        """
        root = os.getcwd()
        directory = os.path.join(root, file_name)
        data_file = open('%s' % directory, 'w')
        csv_wrtr = writer(data_file)
        if headers:
            records = self.get_all_records(headers=True)
        else:
            records = self.get_all_records(headers=False)
        for row in records:
            csv_wrtr.writerow(row)
        data_file.close()
