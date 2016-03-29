from __future__ import division
from random import random, choice
import os
from csv import writer

import networkx as nx
import numpy.random as nprandom

from data_record import DataRecord
from server import Server


class Node:
    """
    Class for a node on our network
    """
    def __init__(self, id_, simulation):
        """
        Initialise a node.
        """
        self.simulation = simulation
        self.mu = [self.simulation.mu[cls][id_ - 1]
            for cls in xrange(len(self.simulation.mu))]
        self.scheduled_servers = self.simulation.schedules[id_ - 1]
        if self.scheduled_servers:
            self.schedule = self.simulation.parameters[
                self.simulation.c[id_ - 1]]
            self.cyclelength = self.simulation.parameters[
                'Cycle_length']
            self.c = self.schedule[0][1]
            self.masterschedule = [self.increment_time(i*self.cyclelength,
                obs) for i in xrange(int(
                self.simulation.max_simulation_time//self.cyclelength
                ) + 2) for obs in [t[0] for t in self.schedule]][1:]
        else:
            self.c = self.simulation.c[id_ - 1]
        if self.simulation.queue_capacities[id_ - 1] == "Inf":
            self.node_capacity = "Inf"
        else:
            self.node_capacity = self.simulation.queue_capacities[
            id_ - 1] + self.c
        self.transition_row = [self.simulation.transition_matrix[j][
            id_ - 1] for j in xrange(len(
            self.simulation.transition_matrix))]
        if self.simulation.class_change_matrix != 'NA':
            self.class_change = self.simulation.class_change_matrix[
            id_ - 1]
        self.individuals = []
        self.id_number = id_
        if self.scheduled_servers:
            self.next_event_date = self.masterschedule[0]
        else:
            self.next_event_date = "Inf"
        self.blocked_queue = []
        if self.c < 'Inf':
            self.servers = [Server(self, i + 1) for i in xrange(self.c)]
            if simulation.detecting_deadlock:
                self.simulation.digraph.add_nodes_from([str(s)
                    for s in self.servers])
        self.highest_id = 0

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
        next_individual.queue_size_at_arrival = len(self.individuals)
        self.individuals.append(next_individual)
        self.simulation.statetracker.change_state_accept(
            self.id_number, next_individual.customer_class)

    def add_new_servers(self, shift_indx, highest_id):
        """
        Add appropriate amount of servers for the given shift.
        """
        num_servers = self.schedule[shift_indx][1]
        for i in xrange(num_servers):
            self.servers.append(Server(self, highest_id+i+1))

    def attach_server(self, server, individual):
        """
        Attaches a server to an individual, and vice versa.
        """
        server.cust = individual
        server.busy = True
        individual.server = server

        if self.simulation.detecting_deadlock:
            for blq in self.blocked_queue:
                inds = [ind for ind in self.simulation.nodes[
                    blq[0]].individuals if ind.id_number==blq[1]]
                ind = inds[0]
                if ind != individual:
                    self.simulation.digraph.add_edge(
                        str(ind.server), str(server))

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
            if self.c < 'Inf':
                self.attach_server(self.find_free_server(),
                                   next_individual)
            next_individual.service_start_date = self.get_now(current_time)
            next_individual.service_end_date = self.increment_time(
                current_time, next_individual.service_time)

    def begin_service_if_possible_change_shift(self, current_time):
        """
        Attempts to begin service if change_shift
        yields any free servers.
        """
        free_servers = [s for s in self.servers if not s.busy]
        for srvr in free_servers:
            if len([i for i in self.individuals if not i.server]) > 0:
                ind = [i for i in self.individuals if not i.server][0]
                self.attach_server(srvr, ind)
                ind.service_start_date = self.get_now(current_time)
                ind.service_end_date = self.increment_time(
                    ind.service_start_date, ind.service_time)

    def begin_service_if_possible_release(self, current_time):
        """
        Begins the service of the next individual, giving
        that customer a service time, end date and node.
        """
        if self.free_server() and self.c != 'Inf':
            srvr = self.find_free_server()
            if len([i for i in self.individuals if not i.server]) > 0:
                ind = [i for i in self.individuals if not i.server][0]
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
        if self.simulation.detecting_deadlock:
            for svr in next_node.servers:
                self.simulation.digraph.add_edge(
                    str(individual.server), str(svr))

    def change_customer_class(self,individual):
        """
        Takes individual and changes customer class
        according to a probability distribution.
        """
        if self.simulation.class_change_matrix != 'NA':
            individual.previous_class = individual.customer_class
            individual.customer_class = nprandom.choice(
                xrange(len(self.class_change)),
                p = self.class_change[individual.previous_class])

    def change_shift(self):
        """
        Add servers and deletes or indicates which servers
        should go off duty.
        """
        if len(self.servers) != 0:
            self.highest_id = max([srvr.id_number
                for srvr in self.servers])
        shift = self.next_event_date%self.cyclelength

        try: inx = self.schedule.index(shift)
        except:
            tms = [obs[0] for obs in self.schedule]
            diffs = [abs(x-float(shift)) for x in tms]
            indx = diffs.index(min(diffs))

        self.take_servers_off_duty()
        self.add_new_servers(indx, self.highest_id)

        self.c = self.schedule[indx][1]
        self.masterschedule.pop(0)
        self.begin_service_if_possible_change_shift(
            self.next_event_date)

    def check_if_shiftchange(self):
        """
        Check whether current time is a shift change.
        """
        if self.scheduled_servers:
            return self.next_event_date == self.masterschedule[0]
        return False

    def detatch_server(self, server, individual):
        """
        Detatches a server from an individual, and vice versa
        """
        server.cust = False
        server.busy = False
        individual.server = False

        if self.simulation.detecting_deadlock:
            self.simulation.digraph.remove_edges_from(
                self.simulation.digraph.in_edges(
                str(server)) + self.simulation.digraph.out_edges(
                str(server)))

        if server.offduty:
            self.kill_server(server)

    def free_server(self):
        """
        Returns True if a server is available, False otherwise
        """
        if self.c == 'Inf':
            return True
        return len([svr for svr in self.servers if not svr.busy]) > 0

    def find_free_server(self):
        """
        Finds a free server.
        """
        for svr in self.servers:
            if not svr.busy:
                return svr

    def finish_service(self):
        """
        The next individual finishes service
        """
        next_individual_indices = [i for i, x in enumerate(
            [ind.service_end_date for ind in self.individuals]
            ) if x == self.next_event_date]
        if len(next_individual_indices) > 1:
            next_individual_index = choice(next_individual_indices)
        else:
            next_individual_index = next_individual_indices[0]
        next_individual = self.individuals[next_individual_index]
        self.change_customer_class(next_individual)
        next_node = self.next_node(next_individual.customer_class)
        next_individual.destination = next_node.id_number
        if len(next_node.individuals) < next_node.node_capacity:
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
        next_individual = self.individuals.pop(next_individual_index)
        next_individual.queue_size_at_departure = len(self.individuals)
        next_individual.exit_date = current_time
        if self.c < 'Inf':
            self.detatch_server(next_individual.server, next_individual)
        self.write_individual_record(next_individual)
        self.simulation.statetracker.change_state_release(self.id_number,
            next_node.id_number, next_individual.customer_class,
            next_individual.is_blocked)
        self.begin_service_if_possible_release(current_time)
        self.release_blocked_individual(current_time)
        next_node.accept(next_individual, current_time)

    def release_blocked_individual(self, current_time):
        """
        Releases an individual who becomes unblocked
        when another individual is released.
        """
        if len(self.blocked_queue) > 0:
            node_to_receive_from = self.simulation.nodes[
                self.blocked_queue[0][0]]
            individual_to_receive_index = [ind.id_number
                for ind in node_to_receive_from.individuals].index(
                self.blocked_queue[0][1])
            individual_to_receive = node_to_receive_from.individuals[
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
        to_delete = []
        for srvr in self.servers:
            if srvr.busy:
                srvr.offduty = True
            else:
                to_delete.append(srvr)
        for obs in to_delete:
            self.kill_server(obs)

    def update_next_event_date(self, current_time):
        """
        Finds the time of the next event at this node
        """
        next_end_service = min([ind.service_end_date
            for ind in self.individuals
            if not ind.is_blocked
            if ind.service_end_date >= current_time] + ["Inf"])
        if self.scheduled_servers:
            next_shift_change = self.masterschedule[0]
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
                            individual.service_time,
                            individual.service_start_date,
                            individual.exit_date,
                            self.id_number,
                            individual.destination,
                            individual.previous_class,
                            individual.queue_size_at_arrival,
                            individual.queue_size_at_departure)
        if self.id_number in individual.data_records:
            individual.data_records[self.id_number].append(record)
        else:
            individual.data_records[self.id_number] = [record]

        individual.arrival_date = False
        individual.service_time = False
        individual.service_start_date = False
        individual.service_end_date = False
        individual.exit_date = False
        individual.queue_size_at_arrival = False
        individual.queue_size_at_departure = False
        individual.destination = False