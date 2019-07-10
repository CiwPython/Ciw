from __future__ import division
import os
import tqdm
import copy
from random import (expovariate, uniform, triangular, gammavariate,
                    lognormvariate, weibullvariate)
from csv import writer, reader
from decimal import getcontext
from itertools import cycle

from .auxiliary import *
from .node import Node
from .exactnode import ExactNode, ExactArrivalNode
from .arrival_node import ArrivalNode
from .exit_node import ExitNode
from ciw import trackers
from ciw import deadlock

class Simulation(object):
    """
    The Simulation class, that is the engine of the simulation.
    """
    def __init__(self, network,
                 exact=False,
                 name='Simulation',
                 tracker=trackers.StateTracker(),
                 deadlock_detector=deadlock.NoDetection(),
                 node_class=None,
                 arrival_node_class=None):
        """
        Initialise an instance of the simualation.
        """
        self.current_time = 0.0
        self.network = network
        self.set_classes(node_class, arrival_node_class)
        if exact:
            self.NodeType = ExactNode
            self.ArrivalNodeType = ExactArrivalNode
            getcontext().prec = exact

        self.name = name
        self.deadlock_detector = deadlock_detector
        self.inter_arrival_times = self.find_arrival_dists()
        self.service_times = self.find_service_dists()
        self.batch_sizes = self.find_batching_dists()
        self.number_of_priority_classes = self.network.number_of_priority_classes
        self.transitive_nodes = [self.NodeType(i + 1, self) for i in range(network.number_of_nodes)]
        self.nodes = ([self.ArrivalNodeType(self)] + self.transitive_nodes + [ExitNode()])
        self.statetracker = tracker
        self.statetracker.initialise(self)
        self.times_dictionary = {self.statetracker.hash_state(): 0.0}
        self.times_to_deadlock = {}
        self.rejection_dict = self.nodes[0].rejection_dict
        self.baulked_dict = self.nodes[0].baulked_dict
        self.unchecked_blockage = False

    def __repr__(self):
        """
        Representation of the simulation.
        """
        return self.name

    def find_arrival_dists(self):
        """
        Create the dictionary of arrival time distribution
        objects for each node for each customer class.
        """
        return {node + 1: {
            clss: copy.deepcopy(
                self.network.customer_classes[clss].arrival_distributions[node]
            )
            for clss in range(self.network.number_of_classes)}
            for node in range(self.network.number_of_nodes)}

    def find_service_dists(self):
        """
        Create the dictionary of service time distribution
        objects for each node for each customer class.
        """
        return {node + 1: {
            clss: copy.deepcopy(
                self.network.customer_classes[clss].service_distributions[node]
            )
            for clss in range(self.network.number_of_classes)}
            for node in range(self.network.number_of_nodes)}

    def find_batching_dists(self):
        """
        Create the dictionary of batch size distribution
        objects for each node for each class.
        """
        return {node + 1: {
            clss: copy.deepcopy(
                self.network.customer_classes[clss].batching_distributions[node]
            )
            for clss in range(self.network.number_of_classes)}
            for node in range(self.network.number_of_nodes)}

    def find_next_active_node(self):
        """
        Returns the next active node, the node whose next_event_date is next:
        """
        next_event_date = min([nd.next_event_date for nd in self.nodes])
        next_active_node_indices = [i for i, nd in enumerate(
            self.nodes) if nd.next_event_date == next_event_date]
        if len(next_active_node_indices) > 1:
            return self.nodes[random_choice(next_active_node_indices)]
        return self.nodes[next_active_node_indices[0]]

    def get_all_individuals(self):
        """
        Returns list of all individuals with at least one data record.
        """
        return [individual for node in self.nodes[1:] for individual in
        node.all_individuals if len(individual.data_records) > 0]

    def get_all_records(self):
        """
        Gets all data records from all individuals.
        """
        records = []
        for individual in self.get_all_individuals():
            for record in individual.data_records:
                records.append(record)
        self.all_records = records
        return records

    def set_classes(self, node_class, arrival_node_class):
        """
        Sets the type of ArrivalNode and Node classes being used
        in the Simulation model (if customer classes are used.)
        """
        if arrival_node_class is not None:
            self.ArrivalNodeType = arrival_node_class
        else:
            self.ArrivalNodeType = ArrivalNode

        if node_class is not None:
            self.NodeType = node_class
        else:
            self.NodeType = Node

    def event_and_return_nextnode(self, next_active_node):
        """
        Carries out the event of current next_active_node,
        and returns the next next_active_node
        """
        next_active_node.have_event()
        for node in self.transitive_nodes:
            node.update_next_event_date()
        return self.find_next_active_node()

    def simulate_until_deadlock(self):
        """
        Runs the simulation until deadlock is reached.
        """
        deadlocked = False
        next_active_node = self.find_next_active_node()
        self.current_time = next_active_node.next_event_date
        while not deadlocked:
            next_active_node = self.event_and_return_nextnode(next_active_node)

            current_state = self.statetracker.hash_state()
            if current_state not in self.times_dictionary:
                self.times_dictionary[current_state] = self.current_time
            if self.unchecked_blockage:
                deadlocked = self.deadlock_detector.detect_deadlock()
                self.unchecked_blockage = False
            if deadlocked:
                time_of_deadlock = self.current_time
            self.current_time = next_active_node.next_event_date

        self.wrap_up_servers(time_of_deadlock)
        self.times_to_deadlock = {state:
            time_of_deadlock - self.times_dictionary[state]
            for state in self.times_dictionary.keys()}

    def simulate_until_max_time(self, max_simulation_time, progress_bar=False):
        """
        Runs the simulation until max_simulation_time is reached.
        """
        next_active_node = self.find_next_active_node()
        self.current_time = next_active_node.next_event_date

        if progress_bar:
            self.progress_bar = tqdm.tqdm(total=max_simulation_time)

        while self.current_time < max_simulation_time:
            next_active_node = self.event_and_return_nextnode(next_active_node)

            if progress_bar:
                remaining_time = max_simulation_time - self.progress_bar.n
                time_increment = next_active_node.next_event_date - self.current_time
                self.progress_bar.update(min(time_increment, remaining_time))

            self.current_time = next_active_node.next_event_date

        self.wrap_up_servers(max_simulation_time)
        if progress_bar:
            remaining_time = max(max_simulation_time - self.progress_bar.n, 0)
            self.progress_bar.update(remaining_time)
            self.progress_bar.close()

    def simulate_until_max_customers(self,
                                     max_customers,
                                     progress_bar=False,
                                     method='Finish'):
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
        self.current_time = next_active_node.next_event_date

        if progress_bar:
            self.progress_bar = tqdm.tqdm(total=max_customers)

        if method == 'Finish':
            check = lambda : self.nodes[-1].number_of_individuals
        elif method == 'Arrive':
            check = lambda : self.nodes[0].number_of_individuals
        elif method == 'Accept':
            check = lambda : self.nodes[0].number_accepted_individuals
        else:
            raise ValueError("Invalid 'method' for 'simulate_until_max_customers'.")

        while check() < max_customers:
            old_check = check()
            next_active_node = self.event_and_return_nextnode(next_active_node)

            if progress_bar:
                remaining_time = max_customers - self.progress_bar.n
                time_increment = check() - old_check
                self.progress_bar.update(min(time_increment, remaining_time))

            previous_time = self.current_time
            self.current_time = next_active_node.next_event_date

        self.wrap_up_servers(previous_time)

        if progress_bar:
            remaining_time = max(max_customers - self.progress_bar.n, 0)
            self.progress_bar.update(remaining_time)
            self.progress_bar.close()

    def wrap_up_servers(self, current_time):
        """
        Updates the servers' total_time and busy_time as
        the end of the simulation run. Finds the overall
        server utilisation for each node.
        """
        for nd in self.transitive_nodes:
            nd.wrap_up_servers(current_time)
            nd.find_server_utilisation()

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
