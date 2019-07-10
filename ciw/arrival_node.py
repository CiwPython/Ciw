from __future__ import division
from random import random
from .individual import Individual


class ArrivalNode(object):
    """
    Class for the arrival node of the network
    """
    def __init__(self, simulation):
        """
        Initialise the arrvial node.
        """
        self.simulation = simulation
        self.number_of_individuals = 0
        self.number_accepted_individuals = 0
        self.event_dates_dict = {nd + 1: {clss: False for clss in range(
            self.simulation.network.number_of_classes)}
            for nd in range(self.simulation.network.number_of_nodes)}
        self.rejection_dict = {nd + 1: {clss:[] for clss in range(
            self.simulation.network.number_of_classes)}
            for nd in range(self.simulation.network.number_of_nodes)}
        self.baulked_dict = {nd + 1: {clss:[] for clss in range(
            self.simulation.network.number_of_classes)}
            for nd in range(self.simulation.network.number_of_nodes)}
        self.initialise_event_dates_dict()
        self.find_next_event_date()

    def __repr__(self):
        """
        Representation of an arrival node.
        """
        return 'Arrival Node'

    def decide_baulk(self, next_node, next_individual):
        """
        Either makes an individual baulk, or sends the individual
        to the next node.
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
        self.next_event_date = self.event_dates_dict[self.next_node][self.next_class]

    def have_event(self):
        """
        Finds a batch size. Creates that many Individuals and send
        them to the relevent node. Then updates the event_dates_dict.
        """
        batch = self.batch_size(self.next_node, self.next_class)
        for _ in range(batch):
            self.number_of_individuals += 1
            priority_class = self.simulation.network.priority_class_mapping[
                self.next_class]
            next_individual = Individual(self.number_of_individuals,
                                         self.next_class,
                                         priority_class)
            next_individual.simulation = self.simulation
            if self.simulation.network.process_based:
                next_individual.route = self.simulation.network.customer_classes[
                next_individual.customer_class].routing[self.next_node - 1](next_individual)
            next_node = self.simulation.transitive_nodes[self.next_node - 1]
            self.release_individual(next_node, next_individual)

        self.event_dates_dict[self.next_node][
            self.next_class] = self.increment_time(
            self.event_dates_dict[self.next_node][
            self.next_class], self.inter_arrival(
            self.next_node, self.next_class))
        self.find_next_event_date()

    def increment_time(self, original, increment):
        """
        Increments the original time by the increment.
        """
        return original + increment

    def initialise_event_dates_dict(self):
        """
        Initialises the next event dates dictionary
        with random times for each node and class.
        """
        for nd in self.event_dates_dict:
            for clss in self.event_dates_dict[nd]:
                self.event_dates_dict[nd][clss] = self.inter_arrival(nd, clss)

    def inter_arrival(self, nd, clss):
        """
        Samples the inter-arrival time for next class and node.
        """
        return self.simulation.inter_arrival_times[nd][clss]._sample(t=self.simulation.current_time)

    def batch_size(self, nd, clss):
        """
        Samples the batch size for next class and node.
        Raises error if a positive integer is not sampled.
        """
        batch = self.simulation.batch_sizes[nd][clss]._sample(t=self.simulation.current_time)
        if isinstance(batch, int) and batch >= 0:
            return batch
        raise ValueError('Batch sizes must be positive integers.')

    def record_baulk(self, next_node):
        """
        Adds an individual to the baulked dictionary.
        """
        self.baulked_dict[next_node.id_number][self.next_class].append(self.next_event_date)

    def record_rejection(self, next_node):
        """
        Adds an individual to the rejection dictionary.
        """
        self.rejection_dict[next_node.id_number][self.next_class].append(self.next_event_date)

    def release_individual(self, next_node, next_individual):
        """
        Either rejects the next_individual die to lack of capacity,
        or sends that individual to baulk or not.
        """
        if next_node.number_of_individuals >= next_node.node_capacity:
            self.record_rejection(next_node)
        else:
            self.decide_baulk(next_node, next_individual)

    def send_individual(self, next_node, next_individual):
        """
        Sends the next_individual to the next_node.
        """
        self.number_accepted_individuals += 1
        next_node.accept(next_individual)

    def update_next_event_date(self):
        """
        Passes, as updating next event happens at time of event.
        """
        pass
