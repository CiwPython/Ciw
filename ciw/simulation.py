from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate, choice
import os
from csv import writer, reader
import yaml
import networkx as nx
import copy
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
            parameters = copy.deepcopy(args[0])
        else:
            parameters = kwargs

        self.parameters = self.build_parameters(parameters)
        self.check_valid_parameters()

        self.c = self.parameters['Number_of_servers']
        self.number_of_nodes = self.parameters['Number_of_nodes']
        self.detecting_deadlock = self.parameters['detect_deadlock']
        self.digraph = nx.DiGraph()
        self.lmbda = [self.parameters['Arrival_distributions']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        self.mu = [self.parameters['Service_distributions']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]
        
        self.schedules = [False for i in range(len(self.c))]
        for i in range(len(self.c)):
            if type(self.c[i])==type('string') and self.c[i]!='Inf':
                self.schedules[i] =  True
        self.queue_capacities = self.parameters['Queue_capacities']
        self.transition_matrix = [self.parameters['Transition_matrices']['Class ' + str(i)] for i in range(self.parameters['Number_of_classes'])]

        if 'Class_change_matrices' in self.parameters:
            self.class_change_matrix = [self.parameters['Class_change_matrices']['Node ' + str(i)] for i in range(self.parameters['Number_of_nodes'])]
        else:
            self.class_change_matrix = 'NA'

        self.max_simulation_time = self.parameters['Simulation_time']

        self.inter_arrival_times = self.find_times_dictionary(self.lmbda)
        self.transitive_nodes = [Node(i + 1, self) for i in range(len(self.c))]
        self.nodes = [ArrivalNode(self)] + self.transitive_nodes + [ExitNode("Inf")]
        self.service_times = self.find_times_dictionary(self.mu)
        self.inter_arrival_times = self.find_times_dictionary(self.lmbda)
        self.state = [[0, 0] for i in range(self.number_of_nodes)]
        initial_state = [[0, 0] for i in range(self.number_of_nodes)]
        self.times_dictionary = {tuple(tuple(initial_state[i]) for i in range(self.number_of_nodes)): 0.0}


    def build_parameters(self, params):
        """
        Builds the parameters dictionary for an M/M/C queue
        """
        if isinstance(params['Arrival_distributions'], list):
            arr_dists = params['Arrival_distributions']
            params['Arrival_distributions'] = {'Class 0': arr_dists}
        if isinstance(params['Service_distributions'], list):
            srv_dists = params['Service_distributions']
            params['Service_distributions'] = {'Class 0': srv_dists}
        if isinstance(params['Transition_matrices'], list):
            trns_mat = params['Transition_matrices']
            params['Transition_matrices'] = {'Class 0': trns_mat}

        default_dict ={'Number_of_nodes': len(params['Number_of_servers']),
                       'Number_of_classes': len(params['Arrival_distributions']),
                       'Queue_capacities': ['Inf' for _ in range(len(params['Number_of_servers']))],
                       'detect_deadlock': False}

        for a in default_dict:
            params[a] = params.get(a, default_dict[a])

        return params

    def check_valid_parameters(self):
        """
        Raises errors if parameter set isn't valid
        """
        if not isinstance(self.parameters['Number_of_classes'], int) or self.parameters['Number_of_classes'] <= 0:
            raise ValueError('Number_of_classes must be a positive integer.')
        if not isinstance(self.parameters['Number_of_nodes'], int) or self.parameters['Number_of_nodes'] <= 0:
            raise ValueError('Number_of_nodes must be a positive integer.')
        if len(self.parameters['Number_of_servers']) != self.parameters['Number_of_nodes']:
            raise ValueError('Number_of_servers must be list of length Number_of_nodes.')
        for x in self.parameters['Number_of_servers']:
            if isinstance(x, int):
                if x < 0:
                    raise ValueError('Number_of_servers must be list of positive integers or valid server schedules.')
            if isinstance(x, str):
                if x != 'Inf':
                    if x not in self.parameters:
                        raise ValueError('Number_of_servers must be list of positive integers or valid server schedules.')
        if not isinstance(self.parameters['detect_deadlock'], bool):
            raise ValueError('detect_deadlock must be a boolean.')
        if len(self.parameters['Queue_capacities']) != self.parameters['Number_of_nodes']:
            raise ValueError('Queue_capacities must be list of length Number_of_nodes.')
        for x in self.parameters['Queue_capacities']:
            if isinstance(x, int):
                if x < 0:
                    raise ValueError('Queue_capacities must be list of positive integers.')
        if not isinstance(self.parameters['Arrival_distributions'], dict) or len(self.parameters['Arrival_distributions']) != self.parameters['Number_of_classes']:
            raise ValueError('Arrival_distributions must be dictionary with classes as keys.')
        for x in self.parameters['Arrival_distributions'].keys():
            if not isinstance(x, str) or x[:6] != 'Class ':
                raise ValueError('Keys of Arrival_distributions must be strings numbered "Class #".')
        for x in self.parameters['Arrival_distributions'].values():
            if not isinstance(x, list) or len(x) != self.parameters['Number_of_nodes']:
                raise ValueError('Arrival_distributions for each class must be a list of length Number_of_nodes')
        if not isinstance(self.parameters['Service_distributions'], dict) or len(self.parameters['Service_distributions']) != self.parameters['Number_of_classes']:
            raise ValueError('Service_distributions must be dictionary with classes as keys.')
        for x in self.parameters['Service_distributions'].keys():
            if not isinstance(x, str) or x[:6] != 'Class ':
                raise ValueError('Keys of Service_distributions must be strings numbered "Class #".')
        for x in self.parameters['Service_distributions'].values():
            if not isinstance(x, list) or len(x) != self.parameters['Number_of_nodes']:
                raise ValueError('Service_distributions for each class must be a list of length Number_of_nodes')
        if not isinstance(self.parameters['Transition_matrices'], dict) or len(self.parameters['Transition_matrices']) != self.parameters['Number_of_classes']:
            raise ValueError('Transition_matrices must be dictionary with classes as keys.')
        for x in self.parameters['Transition_matrices'].keys():
            if not isinstance(x, str) or x[:6] != 'Class ':
                raise ValueError('Keys of Transition_matrices must be strings numbered "Class #".')
        for x in self.parameters['Transition_matrices'].values():
            if not isinstance(x, list) or len(x) != self.parameters['Number_of_nodes']:
                raise ValueError('Transition_matrices for each class must be list of lists of shape Number_of_nodes x Number_of_nodes.')
            for y in x:
                if not isinstance(y, list) or len(y) != self.parameters['Number_of_nodes']:
                    raise ValueError('Transition_matrices for each class must be list of lists of shape Number_of_nodes x Number_of_nodes.')
                for z in y:
                    if not isinstance(z, float) or z < 0.0:
                        raise ValueError('Entries of Transition_matrices must be floats between 0.0 and 1.0.')
                if sum(y) > 1.0:
                    raise ValueError('Rows of Transition_matrices must sum to 1.0 or less.')
        if 'Class_change_matrices' in self.parameters:
            if not isinstance(self.parameters['Class_change_matrices'], dict) or len(self.parameters['Class_change_matrices']) != self.parameters['Number_of_nodes']:
                raise ValueError('Class_change_matrices must be dictionary with nodes as keys.')
            for x in self.parameters['Class_change_matrices'].keys():
                if not isinstance(x, str) or x[:5] != 'Node ':
                    raise ValueError('Keys of Class_change_matrices must be strings numbered "Node #".')
            for x in self.parameters['Class_change_matrices'].values():
                if not isinstance(x, list) or len(x) != self.parameters['Number_of_classes']:
                    raise ValueError('Class_change_matrices for each class must be list of lists of shape Number_of_classes x Number_of_classes.')
                for y in x:
                    if not isinstance(y, list) or len(y) != self.parameters['Number_of_classes']:
                        raise ValueError('Class_change_matrices for each class must be list of lists of shape Number_of_classes x Number_of_classes.')
                    for z in y:
                        if not isinstance(z, float) or z < 0.0:
                            raise ValueError('Entries of Class_change_matrices must be floats between 0.0 and 1.0.')
                    if sum(y) > 1.0:
                        raise ValueError('Rows of Class_change_matrices must sum to 1.0 or less.')
        if self.parameters['Simulation_time'] <= 0:
            raise ValueError('Simulation_time must be a positive number.')




    def find_next_active_node(self):
        """
        Return the next active node:
        """
        next_active_node_indices = [i for i, x in enumerate([nd.next_event_date for nd in self.nodes]) if x == min([nd.next_event_date for nd in self.nodes])]
        if len(next_active_node_indices) > 1:
            return self.nodes[choice(next_active_node_indices)]
        else:
            return self.nodes[next_active_node_indices[0]]

    def find_distributions(self, n, c, source):
        """
        Finds distribution functions
        """
        if source[c][n] == 'NoArrivals':
            return lambda : 'Inf'
        if source[c][n][0] == 'Uniform':
            return lambda : uniform(source[c][n][1], source[c][n][2])
        if source[c][n][0] == 'Deterministic':
            return lambda : source[c][n][1]
        if source[c][n][0] == 'Triangular':
            return lambda : triangular(source[c][n][1], source[c][n][2], source[c][n][3])
        if source[c][n][0] == 'Exponential':
            return lambda : expovariate(source[c][n][1])
        if source[c][n][0] == 'Gamma':
            return lambda : gammavariate(source[c][n][1], source[c][n][2])
        if source[c][n][0] == 'Lognormal':
            return lambda : lognormvariate(source[c][n][1], source[c][n][2])
        if source[c][n][0] == 'Weibull':
            return lambda : weibullvariate(source[c][n][1], source[c][n][2])
        if source[c][n][0] == 'Custom':
            P, V = zip(*self.parameters[source[c][n][1]])
            probs = list(P)
            cum_probs = [sum(probs[0:i+1]) for i in range(len(probs))]
            values = list(V)
            return lambda : self.custom_pdf(cum_probs, values)
        if source[c][n][0] == 'UserDefined':
            return lambda : self.sample_from_user_defined_dist(source[c][n][1])
        if source[c][n][0] == 'Empirical':
            if isinstance(source[c][n][1], str):
                empirical_dist = self.import_empirical_dist(source[c][n][1])
                return lambda : choice(empirical_dist)
            return lambda : choice(source[c][n][1])
        return False

    def sample_from_user_defined_dist(self, func):
        """
        Safely sample from a user defined distribution
        """
        sample = func()

        if not (isinstance(sample, float) or isinstance(sample, int)):
            raise TypeError("User defined function returns invalid type: {}".format(type(sample)))

        elif sample < 0: 
            raise ValueError("User defined function returns invalid value: {}".format(sample))
        return sample

    def import_empirical_dist(self, dist_file):
        """
        Imports an empirical distribution from a .csv file
        """
        root = os.getcwd()
        file_name = root + '/' + dist_file
        empirical_file = open(file_name, 'r')
        rdr = reader(empirical_file)
        empirical_dist = [[float(x) for x in row] for row in rdr][0]
        empirical_file.close()
        return empirical_dist


    def custom_pdf(self, cum_probs, values):
        """
        Samples from a custom pdf
        """
        rnd_num = random()
        for p in range(len(cum_probs)):
            if rnd_num < cum_probs[p]:
                return values[p]

    def find_times_dictionary(self, source):
        """
        Finds the dictionary of service time functions for each node for each class
        """
        return {node+1:{customer_class:self.find_distributions(node, customer_class, source) for customer_class in range(len(self.lmbda))} for node in range(self.number_of_nodes)}

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
            records.append(['I.D. Number', 'Customer Class', 'Node', 'Arrival Date', 'Waiting Time', 'Service Start Date', 'Service Time', 'Service End Date', 'Time Blocked', 'Exit Date', 'Destination', 'Queue Size at Arrival', 'Queue Size at Departure'])
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
                                    record.exit_date,
                                    record.destination,
                                    record.queue_size_at_arrival,
                                    record.queue_size_at_departure])
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
