from __future__ import division
import os
from random import (random, expovariate, uniform, triangular,
    gammavariate, gauss, lognormvariate, weibullvariate, choice)
from csv import writer, reader
import copy
from decimal import Decimal, getcontext

import yaml
import numpy.random as nprandom

from node import Node
from exactnode import ExactNode, ExactArrivalNode
from arrival_node import ArrivalNode
from exit_node import ExitNode
from server import Server
from individual import Individual
from data_record import DataRecord
from state_tracker import *
from deadlock_detector import *

class Simulation:
    """
    Overall simulation class
    """
    def __init__(self, network, exact=False, name='Simulation', tracker=False, deadlock_detector=False):
        """
        Initialise a queue instance.
        """
        self.network = network
        # self.check_valid_parameters(network)
        if not exact:
            NodeType = Node
            ArrivalNodeType = ArrivalNode
        else:
            NodeType = ExactNode
            ArrivalNodeType = ExactArrivalNode
            getcontext().prec = exact
        self.name = name
        self.deadlock_detector = self.choose_deadlock_detection(deadlock_detector)
        self.inter_arrival_times = self.find_times_dict('Arr')
        self.service_times = self.find_times_dict('Ser')
        self.transitive_nodes = [NodeType(i + 1, self)
            for i in xrange(network.number_of_nodes)]
        self.nodes = ([ArrivalNodeType(self)] +
                      self.transitive_nodes +
                      [ExitNode()])
        self.statetracker = self.choose_tracker(tracker, deadlock_detector)
        self.times_dictionary = {self.statetracker.hash_state(): 0.0}
        self.times_to_deadlock = {}
        self.rejection_dict = self.nodes[0].rejection_dict

    def __repr__(self):
        """
        Represents the simulation
        """
        return self.name

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
        if self.parameters['Detect_deadlock'] not in set([False, 'StateDigraph']):
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

    def choose_tracker(self, tracker, deadlock_detector):
        """
        Chooses the state tracker to use for the simulation.
        If no tracker is selected, the basic StateTracker is
        used, unless Detect_deadlock is on, then NaiveTracker
        is the default.
        """
        if tracker:
            if tracker == 'Naive':
                return NaiveTracker(self)
            if tracker == 'Matrix':
                return MatrixTracker(self)
        elif deadlock_detector:
            return NaiveTracker(self)
        return StateTracker(self)

    def choose_deadlock_detection(self, deadlock_detector):
        """
        Chooses the deadlock detection mechanism to use for the
        simulation.
        """
        if deadlock_detector == False:
            return NoDeadlockDetection()
        if deadlock_detector == 'StateDigraph':
            return StateDigraphMethod()

    def find_distributions(self, n, c, kind):
        """
        Finds distribution functions
        """
        if self.source(c, n, kind) == 'NoArrivals':
            return lambda : 'Inf'
        if self.source(c, n, kind)[0] == 'Uniform':
            return lambda : uniform(self.source(c, n, kind)[1],
                                    self.source(c, n, kind)[2])
        if self.source(c, n, kind)[0] == 'Deterministic':
            return lambda : self.source(c, n, kind)[1]
        if self.source(c, n, kind)[0] == 'Triangular':
            return lambda : triangular(self.source(c, n, kind)[1],
                                       self.source(c, n, kind)[2],
                                       self.source(c, n, kind)[3])
        if self.source(c, n, kind)[0] == 'Exponential':
            return lambda : expovariate(self.source(c, n, kind)[1])
        if self.source(c, n, kind)[0] == 'Gamma':
            return lambda : gammavariate(self.source(c, n, kind)[1],
                                         self.source(c, n, kind)[2])
        if self.source(c, n, kind)[0] == 'Lognormal':
            return lambda : lognormvariate(self.source(c, n, kind)[1],
                                           self.source(c, n, kind)[2])
        if self.source(c, n, kind)[0] == 'Weibull':
            return lambda : weibullvariate(self.source(c, n, kind)[1],
                                           self.source(c, n, kind)[2])
        if self.source(c, n, kind)[0] == 'Custom':
            P, V = zip(*self.source(c, n, kind)[1])
            probs, values = list(P), list(V)
            return lambda : nprandom.choice(values, p=probs)
        if self.source(c, n, kind)[0] == 'UserDefined':
            return lambda : self.check_userdef_dist(self.source(c, n, kind)[1])
        if self.source(c, n, kind)[0] == 'Empirical':
            if isinstance(self.source(c, n, kind)[1], str):
                empirical_dist = self.import_empirical(self.source(c, n, kind)[1])
                return lambda : choice(empirical_dist)
            return lambda : choice(self.source(c, n, kind)[1])

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

    def find_times_dict(self, kind):
        """
        Create the dictionary of service time
        functions for each node for each class
        """
        return {node+1: {
            cls: self.find_distributions(node, cls, kind)
            for cls in xrange(self.network.number_of_classes)}
            for node in xrange(self.network.number_of_nodes)}

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
            deadlocked = self.deadlock_detector.detect_deadlock()
            if deadlocked:
                time_of_deadlock = current_time
            next_active_node = self.find_next_active_node()
            current_time = next_active_node.next_event_date
        self.times_to_deadlock = {state:
            time_of_deadlock - self.times_dictionary[state]
            for state in self.times_dictionary.keys()}

    def simulate_until_max_time(self, max_simulation_time):
        """
        Runs the simulation until max_simulation_time is reached.
        """
        self.nodes[0].update_next_event_date()
        next_active_node = self.find_next_active_node()
        current_time = next_active_node.next_event_date
        while current_time < max_simulation_time:
            next_active_node.have_event()
            for node in self.transitive_nodes:
                node.update_next_event_date(current_time)
            next_active_node = self.find_next_active_node()
            current_time = next_active_node.next_event_date

    def source(self, c, n, kind):
        """
        Returns the location of class c node n's arrival or
        service distributions information, depending on kind.
        """
        if kind == 'Arr':
            return self.network.customer_classes[c].arrival_distributions[n]
        if kind == 'Ser':
            return self.network.customer_classes[c].service_distributions[n]

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
