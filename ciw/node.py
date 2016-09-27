from __future__ import division
from random import random
import os
from csv import writer

import networkx as nx
import numpy.random as nprandom

from .data_record import DataRecord
from .server import Server


class Node(object):
    """
    Class for a node on our network
    """
    def __init__(self, id_, simulation):
        """
        Initialise a node.
        """
        self.simulation = simulation
        node = self.simulation.network.service_centres[id_ - 1]
        if node.schedule:
            raw_schedule = node.schedule
            self.cyclelength = self.increment_time(0, raw_schedule[-1][0])
            boundaries = [0] + [row[0] for row in raw_schedule[:-1]]
            servers = [row[1] for row in raw_schedule]
            self.schedule = [list(pair) for pair in zip(boundaries, servers)]
            self.c = self.schedule[0][1]
            raw_schedule_boundaries = [row[0] for row in raw_schedule]
            self.date_generator = self.date_from_schedule_generator(raw_schedule_boundaries)
            self.next_shift_change = next(self.date_generator)
        else:
            self.c = node.number_of_servers
            self.schedule = None
        self.node_capacity = node.queueing_capacity + self.c
        self.transition_row = [
            self.simulation.network.customer_classes[
            cls].transition_matrix[id_ - 1] for cls in range(
            self.simulation.network.number_of_classes)]
        self.class_change = node.class_change_matrix
        self.individuals = [[] for _ in
                range(simulation.number_of_priority_classes)]
        self.id_number = id_
        self.baulking_functions = [self.simulation.network.customer_classes[
            cls].baulking_functions[id_-1] for cls in range(
            self.simulation.network.number_of_classes)]
        if self.schedule:
            self.next_event_date = self.next_shift_change
        else:
            self.next_event_date = float("Inf")
        self.blocked_queue = []
        if self.c < float('Inf'):
            self.servers = [Server(self, i + 1) for i in range(self.c)]
        self.highest_id = self.c
        self.simulation.deadlock_detector.initialise_at_node(self)
        self.preempt = node.preempt
        self.interrupted_individuals = []

    @property
    def all_individuals(self):
        return [i for priority_class in self.individuals
                for i in priority_class]

    @property
    def number_of_individuals(self):
        return len(self.all_individuals)


    def __repr__(self):
        """
        Representation of a node.
        """
        return 'Node %s' % self.id_number

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue.
        """
        next_individual.exit_date = False
        next_individual.is_blocked = False
        self.begin_service_if_possible_accept(
            next_individual, current_time)
        next_individual.queue_size_at_arrival = self.number_of_individuals
        self.individuals[next_individual.priority_class].append(next_individual)
        self.simulation.statetracker.change_state_accept(
            self.id_number, next_individual.customer_class)

    def add_new_servers(self, shift_indx):
        """
        Add appropriate amount of servers for the given shift.
        """
        num_servers = self.schedule[shift_indx][1]
        for i in range(num_servers):
            self.highest_id += 1
            self.servers.append(Server(self, self.highest_id))

    def attach_server(self, server, individual):
        """
        Attaches a server to an individual, and vice versa.
        """
        server.cust = individual
        server.busy = True
        individual.server = server
        self.simulation.deadlock_detector.action_at_attach_server(
            self, server, individual)

    def begin_service_if_possible_accept(self,
                                         next_individual,
                                         current_time):
        """
        Begins the service of the next individual, giving
        that customer a service time, end date and node.
        """
        next_individual.arrival_date = self.get_now(current_time)
        next_individual.service_time = self.get_service_time(
            next_individual.customer_class)
        if self.free_server():
            if self.c < float('Inf'):
                self.attach_server(self.find_free_server(),
                                   next_individual)
            next_individual.service_start_date = self.get_now(current_time)
            next_individual.service_end_date = self.increment_time(
                current_time, next_individual.service_time)

    def begin_interrupted_individuals_service(self, current_time, srvr):
        """
        Restarts the next interrupted individual's service (by
        resampking service time)
        """
        ind = [i for i in self.interrupted_individuals][0]
        self.attach_server(srvr, ind)
        ind.service_time = self.get_service_time(ind.customer_class)
        ind.service_end_date = self.increment_time(self.get_now(current_time), ind.service_time)
        self.interrupted_individuals.remove(ind)

    def begin_service_if_possible_change_shift(self, current_time):
        """
        Attempts to begin service if change_shift
        yields any free servers.
        """
        free_servers = [s for s in self.servers if not s.busy]
        for srvr in free_servers:
            if len(self.interrupted_individuals) > 0:
                self.begin_interrupted_individuals_service(current_time, srvr)
            elif len([i for i in self.all_individuals if not i.server]) > 0:
                ind = [i for i in self.all_individuals if not i.server][0]
                self.attach_server(srvr, ind)
                ind.service_start_date = self.get_now(current_time)
                ind.service_end_date = self.increment_time(
                    ind.service_start_date, ind.service_time)

    def begin_service_if_possible_release(self, current_time):
        """
        Begins the service of the next individual, giving
        that customer a service time, end date and node.
        """
        if self.free_server() and self.c != float('Inf'):
            srvr = self.find_free_server()
            if len(self.interrupted_individuals) > 0:
                self.begin_interrupted_individuals_service(current_time, srvr)
            elif len([i for i in self.all_individuals if not i.server]) > 0:
                ind = [i for i in self.all_individuals if not i.server][0]
                self.attach_server(srvr, ind)
                ind.service_start_date = self.get_now(current_time)
                ind.service_end_date = self.increment_time(
                    ind.service_start_date, ind.service_time)

    def block_individual(self, individual, next_node):
        """
        Blocks the individual from entering the next node.
        """
        individual.is_blocked = True
        self.simulation.statetracker.change_state_block(
            self.id_number, next_node.id_number,
            individual.customer_class)
        next_node.blocked_queue.append(
            (self.id_number, individual.id_number))
        self.simulation.deadlock_detector.action_at_blockage(
            individual, next_node)

    def change_customer_class(self,individual):
        """
        Takes individual and changes customer class
        according to a probability distribution.
        """
        if self.class_change:
            individual.previous_class = individual.customer_class
            individual.customer_class = nprandom.choice(
                range(len(self.class_change)),
                p = self.class_change[individual.previous_class])
            individual.prev_priority_class = individual.priority_class
            individual.priority_class = self.simulation.network.priority_class_mapping[individual.customer_class]

    def change_shift(self):
        """
        Add servers and deletes or indicates which servers
        should go off duty.
        """
        shift = self.next_event_date%self.cyclelength

        try: indx = self.schedule.index(shift)
        except:
            tms = [obs[0] for obs in self.schedule]
            diffs = [abs(x-float(shift)) for x in tms]
            indx = diffs.index(min(diffs))

        self.take_servers_off_duty()
        self.add_new_servers(indx)

        self.c = self.schedule[indx][1]
        self.next_shift_change = next(self.date_generator)
        self.begin_service_if_possible_change_shift(
            self.next_event_date)


    def check_if_shiftchange(self):
        """
        Check whether current time is a shift change.
        """
        if self.schedule:
            return self.next_event_date == self.next_shift_change
        return False

    def detatch_server(self, server, individual):
        """
        Detatches a server from an individual, and vice versa
        """
        server.cust = False
        server.busy = False
        individual.server = False
        self.simulation.deadlock_detector.action_at_detach_server(
            server)
        if server.offduty:
            self.kill_server(server)

    def free_server(self):
        """
        Returns True if a server is available, False otherwise
        """
        if self.c == float('Inf'):
            return True
        return len([svr for svr in self.servers if not svr.busy]) > 0

    def find_free_server(self):
        """
        Finds a free server.
        """
        for svr in self.servers:
            if not svr.busy:
                return svr

    def find_next_individual(self):
        """
        Finds the next individual that should now finish service
        """
        next_individual_indices = [i for i, x in enumerate(
            [ind.service_end_date for ind in self.all_individuals]
            ) if x == self.next_event_date]
        if len(next_individual_indices) > 1:
            next_individual_index = nprandom.choice(next_individual_indices)
        else:
            next_individual_index = next_individual_indices[0]
        return self.all_individuals[next_individual_index], next_individual_index

    def finish_service(self):
        """
        The next individual finishes service
        """
        next_individual, next_individual_index = self.find_next_individual()
        self.change_customer_class(next_individual)
        next_node = self.next_node(next_individual.customer_class)
        next_individual.destination = next_node.id_number
        if len(next_node.all_individuals) < next_node.node_capacity:
            self.release(next_individual_index, next_node,
                self.next_event_date)
        else:
            self.block_individual(next_individual, next_node)

    def get_now(self, current_time):
        """
        Gets the current time
        """
        return current_time

    def have_event(self):
        """
        Has an event
        """
        if self.check_if_shiftchange():
            self.change_shift()
        else:
            self.finish_service()

    def increment_time(self, original, increment):
        """
        Increments the original time by the increment
        """
        return original + increment

    def kill_server(self,srvr):
        """
        Kills server.
        """
        indx = self.servers.index(srvr)
        del self.servers[indx]

    def next_node(self, customer_class):
        """
        Finds the next node according the random distribution.
        """
        return nprandom.choice(self.simulation.nodes[1:],
            p = self.transition_row[customer_class] + [1.0 - sum(
            self.transition_row[customer_class])])

    def release(self, next_individual_index, next_node, current_time):
        """
        Update node when an individual is released.
        """
        next_individual =  self.all_individuals[next_individual_index]
        self.individuals[next_individual.prev_priority_class].remove(next_individual)
        next_individual.queue_size_at_departure = len(self.all_individuals)
        next_individual.exit_date = current_time
        if self.c < float('Inf'):
            self.detatch_server(next_individual.server, next_individual)
        self.write_individual_record(next_individual)
        self.simulation.statetracker.change_state_release(self.id_number,
            next_node.id_number, next_individual.customer_class,
            next_individual.is_blocked)
        self.begin_service_if_possible_release(current_time)
        next_node.accept(next_individual, current_time)
        self.release_blocked_individual(current_time)

    def release_blocked_individual(self, current_time):
        """
        Releases an individual who becomes unblocked
        when another individual is released.
        """
        if len(self.blocked_queue) > 0 and self.number_of_individuals < self.node_capacity:
            node_to_receive_from = self.simulation.nodes[
                self.blocked_queue[0][0]]
            individual_to_receive_index = [ind.id_number
                for ind in node_to_receive_from.all_individuals].index(
                self.blocked_queue[0][1])
            individual_to_receive = node_to_receive_from.all_individuals[
                individual_to_receive_index]
            self.blocked_queue.pop(0)
            node_to_receive_from.release(individual_to_receive_index,
                self, current_time)

    def get_service_time(self, cls):
        """
        Returns a service time for the given customer class
        """
        return self.simulation.service_times[self.id_number][cls]()

    def take_servers_off_duty(self):
        """
        Gathers servers that should be deleted.
        """
        if not self.preempt:
            to_delete = []
            for srvr in self.servers:
                if srvr.busy:
                    srvr.offduty = True
                else:
                    to_delete.append(srvr)
        else:
            to_delete = self.servers[::1]  # copy
            for s in self.servers:
                if s.cust is not False:
                    self.interrupted_individuals.append(s.cust)
                    self.interrupted_individuals[-1].service_end_date = False
                    self.interrupted_individuals[-1].service_time = False
            self.interrupted_individuals.sort(key=lambda x: (x.priority_class,
                                                             x.arrival_date))
        for obs in to_delete:
            self.kill_server(obs)

    def update_next_event_date(self, current_time):
        """
        Finds the time of the next event at this node
        """
        next_end_service = min([ind.service_end_date
            for ind in self.all_individuals
            if not ind.is_blocked
            if ind.service_end_date >= current_time] + [float("Inf")])
        if self.schedule:
            next_shift_change = self.next_shift_change
            self.next_event_date = min(
                next_end_service, next_shift_change)
        else:
            self.next_event_date = next_end_service

    def write_individual_record(self, individual):
        """
        Write a data record for an individual:
            - Arrival date
            - Wait
            - Service start date
            - Service time
            - Service end date
            - Blocked
            - Exit date
            - Node
            - Destination
            - Previous class
            - Queue size at arrival
            - Queue size at departure
        """
        record = DataRecord(individual.arrival_date,
                            individual.service_end_date,
                            individual.service_start_date,
                            individual.exit_date,
                            self.id_number,
                            individual.destination,
                            individual.previous_class,
                            individual.queue_size_at_arrival,
                            individual.queue_size_at_departure)
        individual.data_records.append(record)

        individual.arrival_date = False
        individual.service_time = False
        individual.service_start_date = False
        individual.service_end_date = False
        individual.exit_date = False
        individual.queue_size_at_arrival = False
        individual.queue_size_at_departure = False
        individual.destination = False

    def date_from_schedule_generator(self, boundaries):
        """A generator that yields the next time according to a given schedule"""
        boundaries_len = len(boundaries)
        index = 0
        date = 0
        while True:
            date = self.increment_time(boundaries[index % boundaries_len], (index) // boundaries_len * boundaries[-1])
            index += 1
            yield date
