from __future__ import division
from random import random
from .individual import Individual


class ArrivalNode(object):
    """
    Class for the arrival node on our network
    """
    def __init__(self, simulation):
        """
        Initialise a node.
        """
        self.simulation = simulation
        self.number_of_individuals = 0
        self.number_accepted_individuals = 0
        self.event_dates_dict = {nd + 1: {clss: False for clss in range(
            self.simulation.network.number_of_classes)}
            for nd in range(self.simulation.network.number_of_nodes)}
        self.batch_size_dict = {nd + 1: {clss: 1 for clss in range(
            self.simulation.network.number_of_classes)}
            for nd in range(self.simulation.network.number_of_nodes)}
        self.rejection_dict = {nd + 1: {clss:[] for clss in range(
            self.simulation.network.number_of_classes)}
            for nd in range(self.simulation.network.number_of_nodes)}
        self.baulked_dict = {nd + 1: {clss:[] for clss in range(
            self.simulation.network.number_of_classes)}
            for nd in range(self.simulation.network.number_of_nodes)}
        self.initialise_event_dates_dict()
        self.initialise_batch_size_dict()
        self.find_next_event_date()

    def __repr__(self):
        """
        Representation of an arrival node.
        """
        return 'Arrival Node'

    def decide_baulk(self, next_node, next_individual):
        """
        Either makes an individual baulk, or sends the individual
        to the next node
        """
        if next_node.baulking_functions[self.next_class] is None:
            self.send_individual(next_node, next_individual)
        else:
            rnd_num = random()
            if rnd_num < next_node.baulking_functions[self.next_class](
                next_node.number_of_individuals):
                self.record_baulk(next_node)
            else:
                self.send_individual(next_node, next_individual)

    def find_next_event_date(self):
        """
        Finds the time of the next arrival.
        """
        times = [[self.event_dates_dict[nd + 1][clss]
            for clss in range(len(self.event_dates_dict[1]))]
            for nd in range(len(self.event_dates_dict))]

        mintimes = [min(obs) for obs in times]
        nd = mintimes.index(min(mintimes))
        clss = times[nd].index(min(times[nd]))
        self.next_node = nd + 1
        self.next_class = clss
        self.next_event_date = self.event_dates_dict[
            self.next_node][self.next_class]

    def have_event(self):
        """
        Send new arrival to relevent node.
        """
        for _ in range(self.batch_size_dict[self.next_node][self.next_class]):
            self.number_of_individuals += 1
            priority_class = self.simulation.network.priority_class_mapping[
                self.next_class]
            next_individual = Individual(self.number_of_individuals,
                                         self.next_class,
                                         priority_class)
            next_node = self.simulation.transitive_nodes[self.next_node-1]
            self.release_individual(next_node, next_individual)

        self.event_dates_dict[self.next_node][
            self.next_class] = self.increment_time(
            self.event_dates_dict[self.next_node][
            self.next_class], self.inter_arrival(
            self.next_node, self.next_class,
            self.next_event_date))
        self.batch_size_dict[self.next_node][
            self.next_class] = self.batch_size(
            self.next_node, self.next_class,
            self.next_event_date)
        self.find_next_event_date()

    def increment_time(self, original, increment):
        """
        Increments the original time by the increment
        """
        return original + increment

    def initialise_event_dates_dict(self):
        """
        Initialises the next event dates dictionary
        with random times for each node and class.
        """
        for nd in self.event_dates_dict:
            for clss in self.event_dates_dict[nd]:
                self.event_dates_dict[nd][
                clss] = self.inter_arrival(nd, clss, 0.0)

    def initialise_batch_size_dict(self):
        """
        Initialises the batch sizes dictionary with
        random batch sizes for each node and class.
        """
        for nd in self.batch_size_dict:
            for clss in self.batch_size_dict[nd]:
                self.batch_size_dict[nd][
                clss] = self.batch_size(nd, clss, 0.0)

    def inter_arrival(self, nd, clss, current_time):
        """
        Samples the inter-arrival time for next class and node.
        """
        if self.simulation.network.customer_classes[
            clss].arrival_distributions[nd-1][0] == "TimeDependent":
            return self.simulation.inter_arrival_times[nd][clss](current_time)
        return self.simulation.inter_arrival_times[nd][clss]()

    def batch_size(self, nd, clss, current_time):
        """
        Samples the batch size for next class and node.
        """
        #return int(round(self.simulation.batch_sizes[nd][clss](getattr(self,'next_event_date',None))))
        if self.simulation.network.customer_classes[
            clss].batching_distributions[nd-1][0] == "TimeDependent":
            return int(round(self.simulation.batch_sizes[nd][clss](current_time)))
        return int(round(self.simulation.batch_sizes[nd][clss]()))

    def record_baulk(self, next_node):
        """
        Adds an individual to the baulked dictionary
        """
        self.baulked_dict[next_node.id_number][
            self.next_class].append(self.next_event_date)

    def record_rejection(self, next_node):
        """
        Adds an individual to the rejection dictionary
        """
        self.rejection_dict[next_node.id_number][
            self.next_class].append(self.next_event_date)

    def release_individual(self, next_node, next_individual):
        """
        Either sends next_individual to the next node, or rejects
        that individual.
        """
        if next_node.number_of_individuals >= next_node.node_capacity:
            self.record_rejection(next_node)
        else:
            self.decide_baulk(next_node, next_individual)

    def send_individual(self, next_node, next_individual):
        """
        Sends the next_individual to the next_node
        """
        self.number_accepted_individuals += 1
        next_node.accept(next_individual, self.next_event_date)

    def update_next_event_date(self):
        """
        Passes, updating next event happens at time of event.
        """
        pass
