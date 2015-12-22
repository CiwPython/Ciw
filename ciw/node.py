from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import networkx as nx

from data_record import DataRecord
from server import Server

class Node:
    """
    Class for a node on our network
    """
    def __init__(self, id_number, simulation):
        """
        Initialise a node.
        """
        self.simulation = simulation
        self.mu = [self.simulation.mu[cls][id_number-1] for cls in range(len(self.simulation.mu))]
        self.scheduled_servers = self.simulation.schedules[id_number-1]
        if self.scheduled_servers:
            self.schedule = self.simulation.parameters[self.simulation.c[id_number-1]]
            self.cyclelength = self.simulation.parameters['cycle_length']
            self.c = self.schedule[0][1]
            self.masterschedule = [i*self.cyclelength + obs for i in range(self.simulation.max_simulation_time//self.cyclelength + 1) for obs in [t[0] for t in  self.schedule]][1:]
        else:
            self.c = self.simulation.c[id_number-1]

        self.node_capacity = "Inf" if self.simulation.queue_capacities[id_number-1] == "Inf" else self.simulation.queue_capacities[id_number-1] + self.c
        self.transition_row = [self.simulation.transition_matrix[j][id_number-1] for j in range(len(self.simulation.transition_matrix))]
        if self.simulation.class_change_matrix != 'NA':
            self.class_change_for_node = self.simulation.class_change_matrix[id_number-1]
            self.class_change_cdf = self.find_cdf_class_changes()
        self.individuals = []
        self.id_number = id_number
        self.cum_transition_row = self.find_cum_transition_row()
        if self.scheduled_servers:
            self.next_event_date = self.masterschedule[0]
        else:
            self.next_event_date = "Inf"
        self.blocked_queue = []
        if self.c < 'Inf':
            self.servers = [Server(self, i+1) for i in range(self.c)]
            if simulation.detecting_deadlock:
                self.simulation.digraph.add_nodes_from([str(s) for s in self.servers])
        self.highest_id = 0

    def find_cdf_class_changes(self):
        """
        Turning the pdf of the class change probabilities into a cdf.
        """
        return [[sum(self.class_change_for_node[j][0:i+1]) for i in range(len(self.class_change_for_node[j]))] for j in range(len(self.class_change_for_node))]

    def find_cum_transition_row(self):
        """
        Finds the cumulative transition row for the node
        """

        cum_transition_row = []
        for cls in range(len(self.transition_row)):
            sum_p = 0
            cum_transition_row.append([])
            for p in self.transition_row[cls]:
                sum_p += p
                cum_transition_row[cls].append(sum_p)
        return cum_transition_row

    def __repr__(self):
        """
        Representation of a node::
        """
        return 'Node %s' % self.id_number

    def attach_server(self, server, individual):
        """
        Attaches a server to an individual, and vice versa
        """
        server.cust = individual
        server.busy = True
        individual.server = server

        if self.simulation.detecting_deadlock:
            for blq in self.blocked_queue:
                inds = [ind for ind in self.simulation.nodes[blq[0]].individuals if ind.id_number==blq[1]]
                ind = inds[0]
                if ind != individual:
                    self.simulation.digraph.add_edge(str(ind.server), str(server))


    def detatch_server(self, server, individual):
        """
        Detatches a server from an individual, and vice versa
        """
        server.cust = False
        server.busy = False
        individual.server = False

        if self.simulation.detecting_deadlock:
            self.simulation.digraph.remove_edges_from(self.simulation.digraph.in_edges(str(server)) + self.simulation.digraph.out_edges(str(server)))

        if server.offduty:
            self.kill_server(server)

    def have_event(self):
        """
        Has an event
        """
        if self.check_if_shiftchange():
            self.change_shift()
        else:
            self.finish_service()


    def change_shift(self):
        """
        Add servers and deletes or indicates which servers should go off duty
        """
        if len(self.servers) != 0:
            self.highest_id = max([srvr.id_number for srvr in self.servers])
        shift = self.next_event_date%self.cyclelength

        self.take_servers_off_duty()

        self.add_new_server(shift, self.highest_id)

        indx = [obs[0] for obs in self.schedule].index(shift)
        self.c = self.schedule[indx][1]

    def take_servers_off_duty(self):
        """
        Gathers servers that should be deleted
        """

        to_delete = []
        for srvr in self.servers:
            if srvr.busy:
                srvr.offduty = True
            else:
                to_delete.append(srvr)
        for obs in to_delete:
            self.kill_server(obs)

    def check_if_shiftchange(self):
        """
        Check whether current time is a shift change
        """
        if self.scheduled_servers:
            return self.next_event_date == self.masterschedule[0]
        return False


    def finish_service(self):
        """
        The next individual finishes service
        """
        if self.c == "Inf":
            next_individual_index = [ind.service_end_date for ind in self.individuals].index(self.next_event_date)
        else:
            next_individual_index = [ind.service_end_date for ind in self.individuals[:self.c]].index(self.next_event_date)
        next_individual = self.individuals[next_individual_index]

        self.change_customer_class(next_individual)

        next_node = self.next_node(next_individual.customer_class)

        if len(next_node.individuals) < next_node.node_capacity:
            self.release(next_individual_index, next_node, self.next_event_date)
        else:
            self.block_individual(next_individual, next_node)

    def change_customer_class(self,individual):
        """
        Takes individual and changes customer class according to a probability distribution.
        """
        if self.simulation.class_change_matrix != 'NA':
            rnd_num=random()
            cdf=self.class_change_cdf[individual.customer_class]
            individual.previous_class=individual.customer_class
            
            inx=0
            for i in cdf:
                if rnd_num<=i:
                    individual.customer_class=inx
                    break
                inx+=1

    def block_individual(self, individual, next_node):
        """
        Blocks the individual from entering the next node
        """
        individual.is_blocked = True
        self.change_state_block()
        next_node.blocked_queue.append((self.id_number, individual.id_number))
        if self.simulation.detecting_deadlock:
            for svr in next_node.servers:
                self.simulation.digraph.add_edge(str(individual.server), str(svr))


    def release(self, next_individual_index, next_node, current_time):
        """
        Update node when an individual is released.
        """
        next_individual = self.individuals.pop(next_individual_index)
        next_individual.exit_date = current_time
        if self.c < 'Inf':
            self.detatch_server(next_individual.server, next_individual)
        self.write_individual_record(next_individual)
        self.change_state_release(next_individual)
        self.release_blocked_individual(current_time)
        self.begin_service_if_possible_release(current_time)
        next_node.accept(next_individual, current_time)

    def begin_service_if_possible_release(self, current_time):
        """
        Begins the service of the next individual, giving that customer a service time, end date and node
        """
        if len(self.individuals) >= self.c:
            for ind in self.individuals[:self.c]:
                if not ind.service_start_date:
                    self.attach_server(self.find_free_server(), ind)
                    ind.service_start_date = current_time
                    ind.service_end_date = ind.service_start_date + ind.service_time


    def release_blocked_individual(self, current_time):
        """
        Releases an individual who becomes unblocked when another individual is released
        """
        if len(self.blocked_queue) > 0:
            node_to_receive_from = self.simulation.nodes[self.blocked_queue[0][0]]
            individual_to_receive_index = [ind.id_number for ind in node_to_receive_from.individuals].index(self.blocked_queue[0][1])
            individual_to_receive = node_to_receive_from.individuals[individual_to_receive_index]
            self.blocked_queue.pop(0)
            node_to_receive_from.release(individual_to_receive_index, self, current_time)

    def change_state_release(self, next_individual):
        """
        Changes the state of the system when a customer gets blocked
        """
        if next_individual.is_blocked:
            self.simulation.state[self.id_number-1][1] -= 1
        else:
            self.simulation.state[self.id_number-1][0] -= 1

    def change_state_block(self):
        """
        Changes the state of the system when a customer gets blocked
        """
        self.simulation.state[self.id_number-1][1] += 1
        self.simulation.state[self.id_number-1][0] -= 1

    def change_state_accept(self):
        """
        Changes the state of the system when a customer gets blocked
        """
        self.simulation.state[self.id_number-1][0] += 1

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue
        """
        next_individual.exit_date = False
        next_individual.is_blocked = False
        self.begin_service_if_possible_accept(next_individual, current_time)
        self.individuals.append(next_individual)
        self.change_state_accept()

    def begin_service_if_possible_accept(self, next_individual, current_time):
        """
        Begins the service of the next individual, giving that customer a service time, end date and node
        """
        next_individual.arrival_date = current_time
        next_individual.service_time = self.simulation.service_times[self.id_number][next_individual.customer_class]()
        if len(self.individuals) < self.c:
            if self.c < 'Inf':
                self.attach_server(self.find_free_server(), next_individual)
            next_individual.service_start_date = current_time
            next_individual.service_end_date = current_time + next_individual.service_time

    def find_free_server(self):
        """
        Finds a free server
        """
        free_servers = [svr for svr in self.servers if not svr.busy]
        return free_servers[0]

    def kill_server(self,srvr):
        """
        Kills server
        """
        indx = self.servers.index(srvr)
        del self.servers[indx]

    def add_new_server(self, shift, highest_id):
        """
        Add appropriate amount of servers for the given shift
        """
        indx = [obs[0] for obs in self.schedule].index(shift)
        num_servers = self.schedule[indx][1]
        for i in range(num_servers):
            self.servers.append(Server(self, highest_id+i+1))


    def update_next_event_date(self, current_time):
        """
        Finds the time of the next event at this node
        """
        if self.c == "Inf":
            next_end_service = min([ind.service_end_date for ind in self.individuals if not ind.is_blocked if ind.service_end_date>current_time] + ["Inf"])
        else:
            next_end_service = min([ind.service_end_date for ind in self.individuals[:self.c] if not ind.is_blocked if ind.service_end_date>current_time] + ["Inf"])
        if self.scheduled_servers:
            next_shift_change = self.masterschedule[0]
            self.next_event_date = min(next_end_service, next_shift_change)
        else:
            self.next_event_date = next_end_service

    def next_node(self, customer_class):
        """
        Finds the next node according the random distribution.
        """
        rnd_num = random()
        for p in range(len(self.cum_transition_row[customer_class])):
            if rnd_num < self.cum_transition_row[customer_class][p]:
                return self.simulation.transitive_nodes[p]
        return self.simulation.nodes[-1]

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
        """
        record = DataRecord(individual.arrival_date, individual.service_time, individual.service_start_date, individual.exit_date, self.id_number, individual.previous_class)
        if self.id_number in individual.data_records:
            individual.data_records[self.id_number].append(record)
        else:
            individual.data_records[self.id_number] = [record]

        individual.arrival_date = False
        individual.service_time = False
        individual.service_start_date = False
        individual.service_end_date = False
        individual.exit_date = False