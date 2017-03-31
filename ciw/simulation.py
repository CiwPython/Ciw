from __future__ import division
import os
import tqdm
from random import (expovariate, uniform, triangular, gammavariate,
                    lognormvariate, weibullvariate)
from csv import writer, reader
from decimal import getcontext
from collections import namedtuple
from itertools import cycle

from .auxiliary import *
from .node import Node
from .exactnode import ExactNode, ExactArrivalNode
from .arrival_node import ArrivalNode
from .exit_node import ExitNode
from .state_tracker import *
from .deadlock_detector import *

Record = namedtuple('Record', 'id_number customer_class node arrival_date waiting_time service_start_date service_time service_end_date time_blocked exit_date destination queue_size_at_arrival queue_size_at_departure')

class Simulation(object):
    """
    Overall simulation class
    """
    def __init__(self, network,
                 exact=False,
                 name='Simulation',
                 tracker=False,
                 deadlock_detector=False,
        node_class=None, arrival_node_class=None):
        """
        Initialise a queue instance.
        """
        self.network = network
        self.set_classes(node_class, arrival_node_class)
        if exact:
            self.NodeType = ExactNode
            self.ArrivalNodeType = ExactArrivalNode
            getcontext().prec = exact

        self.name = name
        self.deadlock_detector = self.choose_deadlock_detection(deadlock_detector)
        self.generators = self.find_generators()
        self.inter_arrival_times = self.find_times_dict('Arr')
        self.service_times = self.find_times_dict('Ser')
        self.number_of_priority_classes = self.network.number_of_priority_classes
        self.transitive_nodes = [self.NodeType(i + 1, self)
            for i in range(network.number_of_nodes)]
        self.nodes = ([self.ArrivalNodeType(self)] +
                      self.transitive_nodes +
                      [ExitNode()])
        self.statetracker = self.choose_tracker(tracker, deadlock_detector)
        self.times_dictionary = {self.statetracker.hash_state(): 0.0}
        self.times_to_deadlock = {}
        self.rejection_dict = self.nodes[0].rejection_dict
        self.baulked_dict = self.nodes[0].baulked_dict

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
            raise ValueError("UserDefined func must return positive float.")
        return sample

    def check_timedependent_dist(self, func, current_time):
        sample = func(current_time)
        if not isinstance(sample, float) or sample < 0:
            raise ValueError("TimeDependent func must return positive float.")
        return sample


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
            return lambda : float('Inf')
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
        if self.source(c, n, kind)[0] == 'Normal':
            return lambda : truncated_normal(self.source(c, n, kind)[1],
                                             self.source(c, n, kind)[2])
        if self.source(c, n, kind)[0] == 'Custom':
            values = self.source(c, n, kind)[1]
            probs = self.source(c, n, kind)[2]
            return lambda : random_choice(values, probs)
        if self.source(c, n, kind)[0] == 'UserDefined':
            return lambda : self.check_userdef_dist(self.source(c, n, kind)[1])
        if self.source(c, n, kind)[0] == 'Empirical':
            if isinstance(self.source(c, n, kind)[1], str):
                empirical_dist = self.import_empirical(self.source(c, n, kind)[1])
                return lambda : random_choice(empirical_dist)
            return lambda : random_choice(self.source(c, n, kind)[1])
        if self.source(c, n, kind)[0] == 'TimeDependent':
            return lambda t : self.check_timedependent_dist(self.source(c, n, kind)[1], t)
        if self.source(c, n, kind)[0] == 'Sequential':
            return lambda : next(self.generators[kind][n][c])

    def find_generators(self):
        """
        A dictionary containing all generators used for distributions.
        """
        generators_dict = {'Arr': {}, 'Ser': {}}
        for nd in range(self.network.number_of_nodes):
            generators_dict['Arr'][nd] = {}
            generators_dict['Ser'][nd] = {}
            for clss in range(self.network.number_of_classes):
                arrival = self.network.customer_classes[clss].arrival_distributions[nd]
                service = self.network.customer_classes[clss].service_distributions[nd]
                if arrival[0] == 'Sequential':
                    generators_dict['Arr'][nd][clss] = cycle(arrival[1])
                if service[0] == 'Sequential':
                    generators_dict['Ser'][nd][clss] = cycle(service[1])
        return generators_dict

    def find_next_active_node(self):
        """
        Returns the next active node:
        """
        next_active_node_indices = [i for i, x in enumerate([
            nd.next_event_date for nd in self.nodes]) if x == min([
            nd.next_event_date for nd in self.nodes])]
        if len(next_active_node_indices) > 1:
            return self.nodes[random_choice(next_active_node_indices)]
        return self.nodes[next_active_node_indices[0]]

    def find_times_dict(self, kind):
        """
        Create the dictionary of service time
        functions for each node for each class
        """
        return {node+1: {
            clss: self.find_distributions(node, clss, kind)
            for clss in range(self.network.number_of_classes)}
            for node in range(self.network.number_of_nodes)}

    def get_all_individuals(self):
        """
        Returns list of all individuals with at least one record
        """
        return [individual for node in self.nodes[1:]
            for individual in node.all_individuals
            if len(individual.data_records) > 0]

    def get_all_records(self):
        """
        Gets all records from all individuals
        """
        records = []
        for individual in self.get_all_individuals():
            for record in individual.data_records:
                records.append(Record(individual.id_number,
                                record.customer_class,
                                record.node,
                                record.arrival_date,
                                record.wait,
                                record.service_start_date,
                                record.service_time,
                                record.service_end_date,
                                record.blocked,
                                record.exit_date,
                                record.destination,
                                record.queue_size_at_arrival,
                                record.queue_size_at_departure))
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

    def set_classes(self, node_class, arrival_node_class):
        """
        Sets the type of classes being used in the Simulation model
        """
        if arrival_node_class is not None:
            self.ArrivalNodeType = arrival_node_class
        else:
            self.ArrivalNodeType = ArrivalNode

        if node_class is not None:
            self.NodeType = node_class
        else:
            self.NodeType = Node

    def event_and_return_nextnode(self, next_active_node, current_time):
        """
        Carries out the event of current next_active_node, and return the next
        next_active_node
        """
        next_active_node.have_event()
        for node in self.transitive_nodes:
            node.update_next_event_date(current_time)
        return self.find_next_active_node()

    def simulate_until_deadlock(self):
        """
        Runs the simulation until deadlock is reached.
        """
        deadlocked = False
        next_active_node = self.find_next_active_node()
        current_time = next_active_node.next_event_date
        while not deadlocked:
            next_active_node = self.event_and_return_nextnode(next_active_node, current_time)

            current_state = self.statetracker.hash_state()
            if current_state not in self.times_dictionary:
                self.times_dictionary[current_state] = current_time
            deadlocked = self.deadlock_detector.detect_deadlock()
            if deadlocked:
                time_of_deadlock = current_time
            current_time = next_active_node.next_event_date
        self.times_to_deadlock = {state:
            time_of_deadlock - self.times_dictionary[state]
            for state in self.times_dictionary.keys()}

    def simulate_until_max_time(self, max_simulation_time, progress_bar=False):
        """
        Runs the simulation until max_simulation_time is reached.
        """
        next_active_node = self.find_next_active_node()
        current_time = next_active_node.next_event_date

        if progress_bar is not False:
            self.progress_bar = tqdm.tqdm(total=max_simulation_time)

        while current_time < max_simulation_time:
            next_active_node = self.event_and_return_nextnode(next_active_node, current_time)

            if progress_bar:
                remaining_time = max_simulation_time - self.progress_bar.n
                time_increment = next_active_node.next_event_date - current_time
                self.progress_bar.update(min(time_increment, remaining_time))

            current_time = next_active_node.next_event_date

        if progress_bar:
            remaining_time = max(max_simulation_time - self.progress_bar.n, 0)
            self.progress_bar.update(remaining_time)
            self.progress_bar.close()

    def simulate_until_max_customers(self, max_customers,
                                     progress_bar=False, method='Finish'):
        """
        Runs the simulation until max_customers is reached:

            - Method: Finish
                Simulates until max_customers has reached the Exit Node
            - Method: Arrive
                Simulates until max_customers have spawned at the Arrival Node
            - Method: Accept
                Simulates until max_customers have been spawned and accepted
                (not rejected) at the Arrival Node
        """
        next_active_node = self.find_next_active_node()
        current_time = next_active_node.next_event_date

        if progress_bar is not False:
            self.progress_bar = tqdm.tqdm(total=max_customers)

        if method == 'Finish':
            check = lambda : self.nodes[-1].number_completed
        elif method == 'Arrive':
            check = lambda : self.nodes[0].number_of_individuals
        elif method == 'Accept':
            check = lambda : self.nodes[0].number_accepted_individuals
        else:
            raise ValueError("Invalid 'method' for 'simulate_until_max_customers'.")

        while check() < max_customers:
            old_check = check()
            next_active_node = self.event_and_return_nextnode(next_active_node, current_time)

            if progress_bar:
                remaining_time = max_customers - self.progress_bar.n
                time_increment = check() - old_check
                self.progress_bar.update(min(time_increment, remaining_time))

            current_time = next_active_node.next_event_date

        if progress_bar:
            remaining_time = max(max_customers - self.progress_bar.n, 0)
            self.progress_bar.update(remaining_time)
            self.progress_bar.close()

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
        if headers:
            csv_wrtr.writerow(['I.D. Number',
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
        records = self.get_all_records()
        for row in records:
            csv_wrtr.writerow(row)
        data_file.close()
