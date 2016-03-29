from __future__ import division
import os
from random import (random, expovariate, uniform, triangular,
    gammavariate, gauss, lognormvariate, weibullvariate, choice)
from csv import writer, reader
import copy
from decimal import Decimal, getcontext

import yaml
import networkx as nx
import numpy.random as nprandom

from node import Node
from exactnode import ExactNode, ExactArrivalNode
from arrival_node import ArrivalNode
from exit_node import ExitNode
from server import Server
from individual import Individual
from data_record import DataRecord
from state_tracker import *

class Simulation:
    """
    Overall simulation class
    """
    def __init__(self, *args, **kwargs):
        """
        Initialise a queue instance.
        """
        if args:
            parameters = copy.deepcopy(args[0])
        else:
            parameters = kwargs
        self.parameters = self.build_parameters(parameters)
        self.check_valid_parameters()
        if not self.parameters['Exact']:
            NodeType = Node
            ArrivalNodeType = ArrivalNode
        else:
            NodeType = ExactNode
            ArrivalNodeType = ExactArrivalNode
            getcontext().prec = self.parameters['Exact']
        self.name = self.parameters['Name']
        self.c = self.parameters['Number_of_servers']
        self.number_of_nodes = self.parameters['Number_of_nodes']
        self.detecting_deadlock = self.parameters['Detect_deadlock']
        self.digraph = nx.DiGraph()
        self.lmbda = [self.parameters['Arrival_distributions'][
            'Class ' + str(i)] for i in xrange(self.parameters[
            'Number_of_classes'])]
        self.mu = [self.parameters['Service_distributions'][
            'Class ' + str(i)] for i in xrange(
            self.parameters['Number_of_classes'])]
        self.schedules = [False for i in xrange(len(self.c))]
        for i in xrange(len(self.c)):
            if isinstance(self.c[i], str) and self.c[i] != 'Inf':
                self.schedules[i] = True
        self.queue_capacities = self.parameters['Queue_capacities']
        self.transition_matrix = [self.parameters[
            'Transition_matrices']['Class ' + str(i)]
            for i in xrange(self.parameters['Number_of_classes'])]
        if 'Class_change_matrices' in self.parameters:
            self.class_change_matrix = [self.parameters[
                'Class_change_matrices']['Node ' + str(i)]
                for i in xrange(self.parameters['Number_of_nodes'])]
        else:
            self.class_change_matrix = 'NA'
        self.max_simulation_time = self.parameters['Simulation_time']
        self.inter_arrival_times = self.find_times_dict(self.lmbda)
        self.service_times = self.find_times_dict(self.mu)
        self.transitive_nodes = [NodeType(i + 1, self)
            for i in xrange(len(self.c))]
        self.nodes = ([ArrivalNodeType(self)] +
                      self.transitive_nodes +
                      [ExitNode("Inf")])
        self.statetracker = self.choose_tracker()
        self.times_dictionary = {self.statetracker.hash_state(): 0.0}
        self.times_to_deadlock = {}
        self.rejection_dict = self.nodes[0].rejection_dict

    def __repr__(self):
        """
        Represents the simulation
        """
        return self.name

    def build_parameters(self, params):
        """
        Fills out the parameters dictionary with any
        default arguments. Creates dictionaries for
        things if onyl 1 class is given.
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

        default_dict = {
            'Name': 'Simulation',
            'Number_of_nodes': len(params['Number_of_servers']),
            'Number_of_classes': len(params['Arrival_distributions']),
            'Queue_capacities': ['Inf' for _ in xrange(len(
                params['Number_of_servers']))],
            'Detect_deadlock': False,
            'Simulation_time': None,
            'Exact': False
            }

        for a in default_dict:
            params[a] = params.get(a, default_dict[a])
        return params

    def check_simulation_time(self):
        """
        Raises errors if there is an invalide simulation time
        """
        if self.parameters['Simulation_time'] is None:
            raise ValueError('Simulation_time not set.')
        if self.parameters['Simulation_time'] <= 0:
            raise ValueError('Simulation_time must be a positive number.')

    def check_userdef_dist(self, func):
        """
        Safely sample from a user defined distribution
        """
        sample = func()
        if not isinstance(sample, float) or sample < 0:
            raise ValueError("UserDefined function must return positive float.")
        return sample

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
        if not isinstance(self.parameters['Detect_deadlock'], bool):
            raise ValueError('Detect_deadlock must be a boolean.')
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
        for cls in self.parameters['Service_distributions'].values():
            for nd in cls:
                if nd[0] not in ['Uniform', 'Triangular', 'Deterministic', 'Exponential', 'Gamma', 'Lognormal', 'Weibull', 'Empirical', 'Custom', 'UserDefined']:
                    raise ValueError("Service distribution must be one of 'Uniform', 'Triangular', 'Deterministic', 'Exponential', 'Gamma', 'Lognormal', 'Weibull', 'Empirical', 'Custom', or 'UserDefined'")
                if nd[0] == 'Uniform':
                    if nd[1] < 0.0 or nd[2] < 0.0:
                        raise ValueError('Uniform distribution must sample positive numbers only.')
                    if nd[2] <= nd[1]:
                        raise ValueError('Upper limit of Uniform distribution must be greater than the lower limit.')
                if nd[0] == 'Deterministic':
                    if nd[1] < 0.0:
                        raise ValueError('Deterministic distribution must sample positive numbers only.')
                if nd[0] == 'Triangular':
                    if nd[1] < 0.0 or nd[2] < 0.0 or nd[3] < 0.0:
                        raise ValueError('Triangular distribution must sample positive numbers only.')
                    if nd[1] > nd[2] or nd[1] >= nd[3] or nd[3] >= nd[2]:
                        raise ValueError('Triangular distribution\'s median must lie between the lower and upper limits.')
                if nd[0] == 'Custom':
                        P, V = zip(*self.parameters[nd[1]])
                        for el in P:
                            if not isinstance(el, float) or el < 0.0:
                                raise ValueError('Probabilities for Custom distribution need to be floats between 0.0 and 1.0.')
                        for el in V:
                            if el < 0.0:
                                raise ValueError('Custom distribution must sample positive values only.')
                if nd[0] == 'Empirical':
                    if isinstance(nd[1], list):
                        if any([el<0.0 for el in nd[1]]):
                            raise ValueError('Empirical distribution must sample positive floats.')
        for cls in self.parameters['Arrival_distributions'].values():
            for nd in cls:
                if nd != 'NoArrivals':
                    if nd[0] not in ['Uniform', 'Triangular', 'Deterministic', 'Exponential', 'Gamma', 'Lognormal', 'Weibull', 'Empirical', 'Custom', 'UserDefined']:
                        raise ValueError("Arrival distribution must be one of 'Uniform', 'Triangular', 'Deterministic', 'Exponential', 'Gamma', 'Lognormal', 'Weibull', 'Empirical', 'Custom', 'UserDefined', or 'NoArrivals'.")
                    if nd[0] == 'Uniform':
                        if nd[1] < 0.0 or nd[2] < 0.0:
                            raise ValueError('Uniform distribution must sample positive numbers only.')
                        if nd[2] <= nd[1]:
                            raise ValueError('Upper limit of Uniform distribution must be greater than the lower limit.')
                    if nd[0] == 'Deterministic':
                        if nd[1] < 0.0:
                            raise ValueError('Deterministic distribution must sample positive numbers only.')
                    if nd[0] == 'Triangular':
                        if nd[1] < 0.0 or nd[2] < 0.0 or nd[3] < 0.0:
                            raise ValueError('Triangular distribution must sample positive numbers only.')
                        if nd[1] > nd[2] or nd[1] >= nd[3] or nd[3] >= nd[2]:
                            raise ValueError('Triangular distribution\'s median must lie between the lower and upper limits.')
                    if nd[0] == 'Custom':
                            P, V = zip(*self.parameters[nd[1]])
                            for el in P:
                                if not isinstance(el, float) or el < 0.0:
                                    raise ValueError('Probabilities for Custom distribution need to be floats between 0.0 and 1.0.')
                            for el in V:
                                if el < 0.0:
                                    raise ValueError('Custom distribution must sample positive values only.')
                    if nd[0] == 'Empirical':
                        if isinstance(nd[1], list):
                            if any([el<0.0 for el in nd[1]]):
                                raise ValueError('Empirical distribution must sample positive floats.')

    def choose_tracker(self):
        """
        Chooses the state tracker to use for the simulation.
        If no tracker is selected, the basic StateTracker is
        used, unless Detect_deadlock is on, then NaiveTracker
        is the default.
        """
        if 'Tracker' in self.parameters:
            if self.parameters['Tracker'] == 'Naive':
                return NaiveTracker(self)
            if self.parameters['Tracker'] == 'Matrix':
                return MatrixTracker(self)
        elif self.parameters['Detect_deadlock']:
            return NaiveTracker(self)
        return StateTracker(self)
    
    def detect_deadlock(self):
        """
        Detects whether the system is in a deadlocked state,
        that is, is there a knot. Note that this code is taken
        and adapted from the NetworkX Developer Zone Ticket
        #663 knot.py (09/06/2015)
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

    def find_distributions(self, n, c, source):
        """
        Finds distribution functions
        """
        if source[c][n] == 'NoArrivals':
            return lambda : 'Inf'
        if source[c][n][0] == 'Uniform':
            return lambda : uniform(source[c][n][1],
                                    source[c][n][2])
        if source[c][n][0] == 'Deterministic':
            return lambda : source[c][n][1]
        if source[c][n][0] == 'Triangular':
            return lambda : triangular(source[c][n][1],
                                       source[c][n][2],
                                       source[c][n][3])
        if source[c][n][0] == 'Exponential':
            return lambda : expovariate(source[c][n][1])
        if source[c][n][0] == 'Gamma':
            return lambda : gammavariate(source[c][n][1],
                                         source[c][n][2])
        if source[c][n][0] == 'Lognormal':
            return lambda : lognormvariate(source[c][n][1],
                                           source[c][n][2])
        if source[c][n][0] == 'Weibull':
            return lambda : weibullvariate(source[c][n][1],
                                           source[c][n][2])
        if source[c][n][0] == 'Custom':
            P, V = zip(*self.parameters[source[c][n][1]])
            probs, values = list(P), list(V)
            return lambda : nprandom.choice(values, p=probs)
        if source[c][n][0] == 'UserDefined':
            return lambda : self.check_userdef_dist(source[c][n][1])
        if source[c][n][0] == 'Empirical':
            if isinstance(source[c][n][1], str):
                empirical_dist = self.import_empirical(source[c][n][1])
                return lambda : choice(empirical_dist)
            return lambda : choice(source[c][n][1])

    def find_next_active_node(self):
        """
        Returns the next active node:
        """
        next_active_node_indices = [i for i, x in enumerate([
            nd.next_event_date for nd in self.nodes]) if x == min([
            nd.next_event_date for nd in self.nodes])]
        if len(next_active_node_indices) > 1:
            return self.nodes[choice(next_active_node_indices)]
        return self.nodes[next_active_node_indices[0]]

    def find_times_dict(self, source):
        """
        Create the dictionary of service time
        functions for each node for each class
        """
        return {node+1: {
            cls: self.find_distributions(node, cls, source)
            for cls in xrange(len(self.lmbda))}
            for node in xrange(self.number_of_nodes)}

    def get_all_individuals(self):
        """
        Returns list of all individuals with at least one record
        """
        return [individual for node in self.nodes[1:]
            for individual in node.individuals
            if len(individual.data_records) > 0]

    def get_all_records(self, headers=True):
        """
        Gets all records from all individuals
        """
        records = []
        if headers:
            records.append(['I.D. Number',
                            'Customer Class',
                            'Node',
                            'Arrival Date',
                            'Waiting Time',
                            'Service Start Date',
                            'Service Time',
                            'Service End Date',
                            'Time Blocked',
                            'Exit Date',
                            'Destination',
                            'Queue Size at Arrival',
                            'Queue Size at Departure'])
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

    def import_empirical(self, dist_file):
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

    def simulate_until_deadlock(self):
        """
        Runs the simulation until deadlock is reached.
        """
        deadlocked = False
        self.nodes[0].update_next_event_date()
        next_active_node = self.find_next_active_node()
        current_time = next_active_node.next_event_date
        while not deadlocked:
            next_active_node.have_event()
            current_state = self.statetracker.hash_state()
            if current_state not in self.times_dictionary:
                self.times_dictionary[current_state] = current_time
            for node in self.transitive_nodes:
                node.update_next_event_date(current_time)
            deadlocked = self.detect_deadlock()
            if deadlocked:
                time_of_deadlock = current_time
            next_active_node = self.find_next_active_node()
            current_time = next_active_node.next_event_date
        self.times_to_deadlock = {state:
            time_of_deadlock - self.times_dictionary[state]
            for state in self.times_dictionary.keys()}

    def simulate_until_max_time(self):
        """
        Runs the simulation until max_simulation_time is reached.
        """
        self.check_simulation_time()
        self.nodes[0].update_next_event_date()
        next_active_node = self.find_next_active_node()
        current_time = next_active_node.next_event_date
        while current_time < self.max_simulation_time:
            next_active_node.have_event()
            for node in self.transitive_nodes:
                node.update_next_event_date(current_time)
            next_active_node = self.find_next_active_node()
            current_time = next_active_node.next_event_date

    def write_records_to_file(self, file_name, headers=True):
        """
        Writes the records for all individuals to a csv file
        """
        root = os.getcwd()
        directory = os.path.join(root, file_name)
        data_file = open('%s' % directory, 'w')
        csv_wrtr = writer(data_file)
        records = self.get_all_records(headers=headers)
        for row in records:
            csv_wrtr.writerow(row)
        data_file.close()
