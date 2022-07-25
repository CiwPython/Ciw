from __future__ import division
from pickle import FALSE
from random import random
import os
from csv import writer
from math import isinf, nan

import networkx as nx

from .auxiliary import random_choice, flatten_list
from .data_record import DataRecord
from .server import Server


class Node(object):
    """
    Class for a node on the network.
    """
    def __init__(self, id_, simulation):
        """
        Initialise a node.
        """
        self.simulation = simulation
        node = self.simulation.network.service_centres[id_ - 1]
        self.server_priority_function = node.server_priority_function
        if node.schedule:
            raw_schedule = node.schedule
            self.cyclelength = self.increment_time(0, raw_schedule[-1][1])
            boundaries = [0] + [row[1] for row in raw_schedule[:-1]]
            servers = [row[0] for row in raw_schedule]
            self.schedule = [list(pair) for pair in zip(boundaries, servers)]
            self.c = self.schedule[0][1]
            raw_schedule_boundaries = [row[1] for row in raw_schedule]
            self.date_generator = self.date_from_schedule_generator(
                raw_schedule_boundaries)
            self.next_shift_change = next(self.date_generator)
            self.next_event_date = self.next_shift_change
        else:
            self.c = node.number_of_servers
            self.schedule = None
            self.next_event_date = float("Inf")
            self.next_shift_change = float("Inf")
        self.node_capacity = node.queueing_capacity + self.c
        if not self.simulation.network.process_based:
            self.transition_row = [
                self.simulation.network.customer_classes[
                clss].routing[id_ - 1] for clss in range(
                self.simulation.network.number_of_classes)]
        self.class_change = node.class_change_matrix
        self.individuals = [[] for _ in
                range(simulation.number_of_priority_classes)]
        self.number_of_individuals = 0
        self.id_number = id_
        self.baulking_functions = [
            self.simulation.network.customer_classes[clss
            ].baulking_functions[id_ - 1] for clss in range(
            self.simulation.network.number_of_classes)]
        self.overtime = []
        self.blocked_queue = []
        self.len_blocked_queue = 0
        if not isinf(self.c):
            self.servers = self.create_starting_servers()
        self.highest_id = self.c
        self.simulation.deadlock_detector.initialise_at_node(self)
        self.schedule_preempt = node.schedule_preempt
        self.priority_preempt = node.priority_preempt
        self.interrupted_individuals = []
        self.number_interrupted_individuals = 0
        self.all_servers_total = []
        self.all_servers_busy = []
        self.reneging = node.reneging
        self.next_renege_date = float('Inf')
        self.dynamic_classes = node.class_change_time
        self.next_class_change_date = float('Inf')

    @property
    def all_individuals(self):
        if self.simulation.number_of_priority_classes == 1:
            return self.individuals[0]
        return flatten_list(self.individuals)

    def __repr__(self):
        """
        Representation of a node.
        """
        return 'Node %s' % self.id_number

    def accept(self, next_individual):
        """
        Accepts a new customer to the queue:
          - remove previous exit date and blockage status
          - see if possible to begin service
          - record all other information at arrival point
          - update state tracker
        """
        next_individual.node = self.id_number
        next_individual.exit_date = False
        next_individual.is_blocked = False
        next_individual.original_class = next_individual.customer_class
        next_individual.queue_size_at_arrival = self.number_of_individuals
        self.individuals[next_individual.priority_class].append(next_individual)
        self.number_of_individuals += 1
        self.begin_service_if_possible_accept(next_individual)
        self.simulation.statetracker.change_state_accept(self, next_individual)

    def add_new_servers(self, num_servers):
        """
        Add appropriate amount of servers for the given shift.
        """
        for i in range(num_servers):
            self.highest_id += 1
            self.servers.append(self.simulation.ServerType(self, self.highest_id, self.next_event_date))

    def attach_server(self, server, individual):
        """
        Attaches a server to an individual, and vice versa.
        """
        server.cust = individual
        server.busy = True
        individual.server = server
        self.simulation.deadlock_detector.action_at_attach_server(
            self, server, individual)

    def begin_service_if_possible_accept(self, next_individual):
        """
        Begins the service of the next individual (at acceptance point):
            - Sets the arrival date as the current time
            - If there is a free server or there are infinite servers:
                - Attach the server to the individual (only when servers are not infinite)
            - Get service start time, service time, service end time
            - Update the server's end date (only when servers are not infinite)
        """
        next_individual.arrival_date = self.get_now()
        if self.reneging is True:
            next_individual.reneging_date = self.get_reneging_date(next_individual)
        if self.dynamic_classes is True:
            self.decide_class_change(next_individual)

        free_server = self.find_free_server(next_individual)
        if free_server is None and isinf(self.c) is False:
            self.decide_preempt(next_individual)
        if free_server is not None or isinf(self.c):
            if isinf(self.c) is False:
                self.attach_server(free_server, next_individual)
            next_individual.service_start_date = self.get_now()
            next_individual.service_time = self.get_service_time(next_individual)
            next_individual.service_end_date = self.increment_time(
                self.get_now(), next_individual.service_time)
            if not isinf(self.c):
                free_server.next_end_service_date = next_individual.service_end_date

    def begin_interrupted_individuals_service(self, srvr):
        """
        Restarts the next interrupted individual's service (by
        resampling service time)
        """
        ind = [i for i in self.interrupted_individuals][0]
        if ind.is_blocked:
            node_blocked_to = self.simulation.nodes[ind.destination]
            ind.destination = False
            node_blocked_to.blocked_queue.remove((self.id_number, ind.id_number))
            node_blocked_to.len_blocked_queue -= 1
            ind.is_blocked = False
        self.attach_server(srvr, ind)
        self.give_service_time_after_preemption(ind)
        ind.service_start_date = self.get_now()
        ind.service_end_date = self.increment_time(self.get_now(), ind.service_time)
        ind.interrupted = False
        srvr.next_end_service_date = ind.service_end_date
        self.interrupted_individuals.remove(ind)
        self.number_interrupted_individuals -= 1

    def begin_service_if_possible_change_shift(self):
        """
        If there are free servers after a shift change:
          - restart interrupted customers' services
          - begin service of any waiting cutsomers
            - give a start date and end date
            - attach servers to individual
        """
        free_servers = [s for s in self.servers if not s.busy]
        for srvr in free_servers:
            if self.number_interrupted_individuals > 0:
                self.begin_interrupted_individuals_service(srvr)
            else:
                for ind in self.all_individuals:
                    if not ind.server:
                        self.attach_server(srvr, ind)
                        ind.service_start_date = self.get_now()
                        if ind.service_time is False: 
                            ind.service_time = self.get_service_time(ind)
                        else:
                            self.give_service_time_after_preemption(ind)
                        ind.service_end_date = self.increment_time(
                            ind.service_start_date, ind.service_time)
                        srvr.next_end_service_date = ind.service_end_date
                        break

    def begin_service_if_possible_release(self, next_individual):
        """
        Begins the service of the next individual (at point
        of previous individual's release)
          - check if there are any interrupted individuals
            left to restart service
          - give an arrival date and service time
          - give a start date and end date
          - attach server to individual
        """
        srvr = self.find_free_server(next_individual)
        if srvr is not None:
            if self.number_interrupted_individuals > 0:
                self.begin_interrupted_individuals_service(srvr)
            else:
                for ind in self.all_individuals:
                    if not ind.server:
                        self.attach_server(srvr, ind)
                        ind.service_start_date = self.get_now()
                        if ind.service_time is False: 
                            ind.service_time = self.get_service_time(ind)
                        else:
                            self.give_service_time_after_preemption(ind)
                        ind.service_end_date = self.increment_time(
                            ind.service_start_date, ind.service_time)
                        srvr.next_end_service_date = ind.service_end_date
                        break

    def block_individual(self, individual, next_node):
        """
        Blocks the individual from entering the next node:
          - change is_blocked attribute
          - update state tracker
          - add information to the next node's blocked queue
          - update deadlock detector
          - inform simulation that there are unchecked
          blockages for deadlock detection
        """
        individual.is_blocked = True
        self.simulation.statetracker.change_state_block(self, next_node, individual)
        next_node.blocked_queue.append(
            (self.id_number, individual.id_number))
        next_node.len_blocked_queue += 1
        self.simulation.deadlock_detector.action_at_blockage(individual, next_node)
        self.simulation.unchecked_blockage = True

    def change_customer_class(self, individual):
        """
        Takes individual and changes customer class
        according to a probability distribution.
        """
        if self.class_change:
            individual.previous_class = individual.customer_class
            individual.customer_class = random_choice(
                range(self.simulation.network.number_of_classes),
                self.class_change[individual.previous_class])
            individual.prev_priority_class = individual.priority_class
            individual.priority_class = self.simulation.network.priority_class_mapping[individual.customer_class]

    def change_customer_class_while_waiting(self):
        """
        Finds the next individual to have a class change (while queueing) and changes their class.
        """
        changing_individual = [ind for ind in self.all_individuals if ind.class_change_date == self.simulation.current_time][0]
        changing_individual.customer_class = changing_individual.next_class
        changing_individual.priority_class = self.simulation.network.priority_class_mapping[changing_individual.next_class]
        if changing_individual.priority_class != changing_individual.prev_priority_class:
            self.change_priority_queue(changing_individual)
            self.decide_preempt(changing_individual)
        self.simulation.statetracker.change_state_classchange(self, changing_individual)
        changing_individual.previous_class = changing_individual.next_class
        changing_individual.prev_priority_class = changing_individual.priority_class
        self.decide_class_change(changing_individual)

    def change_priority_queue(self, individual):
        """
        Moves an individual from their old priority queue to their new priority queue.
        """
        self.individuals[individual.prev_priority_class].remove(individual)
        self.individuals[individual.priority_class].append(individual)

    def change_shift(self):
        """
        Implment a server shift change:
         - adds / deletes servers, or indicates which servers should go off duty
         - begin any new services if free servers
        """
        shift = self.next_event_date % self.cyclelength

        try:
            indx = self.schedule.index(shift)
        except:
            tms = [obs[0] for obs in self.schedule]
            diffs = [abs(x - float(shift)) for x in tms]
            indx = diffs.index(min(diffs))

        num_servers = self.schedule[indx][1]
        self.take_servers_off_duty()
        self.add_new_servers(num_servers)

        self.c = self.schedule[indx][1]
        self.next_shift_change = next(self.date_generator)
        self.begin_service_if_possible_change_shift()

    def check_if_renege(self):
        """
        Checks whether the current time is a renege time.
        """
        if self.reneging is True:
            return self.next_event_date == self.next_renege_date
        return False

    def check_if_shiftchange(self):
        """
        Check whether current time is a shift change.
        """
        if self.schedule:
            return self.next_event_date == self.next_shift_change
        return False

    def check_if_classchange(self):
        """
        Checks whether the current time is a class change time.
        """
        if self.dynamic_classes is True:
            return self.next_event_date == self.next_class_change_date
        return False

    def create_starting_servers(self):
        """
        Initialise the servers.
        """
        return [self.simulation.ServerType(self, i + 1, 0.0) for i in range(self.c)]

    def decide_class_change(self, next_individual):
        """
        Decides on the next_individual's next class and class change date
        """
        class_change_times = [float('Inf') if dist is None else dist.sample() for dist in self.simulation.network.customer_classes[next_individual.customer_class].class_change_time_distributions]
        next_class = min(range(len(class_change_times)), key=class_change_times.__getitem__)
        time = class_change_times[next_class]
        next_individual.next_class = next_class
        next_individual.class_change_date = self.increment_time(self.get_now(), time)

    def decide_preempt(self, individual):
        """
        Decides if priority preemption is needed, finds the individual to preempt, and preempt them.
        """
        if self.priority_preempt != False:
            least_priority = max(s.cust.priority_class for s in self.servers)
            if individual.priority_class < least_priority:
                least_prioritised_individuals = [s.cust for s in self.servers if s.cust.priority_class == least_priority]
                individual_to_preempt = max([ind for ind in least_prioritised_individuals], key=lambda cust: cust.service_start_date)
                self.preempt(individual_to_preempt, individual)

    def detatch_server(self, server, individual):
        """
        Detatches a server from an individual, and vice versa.
        """
        self.simulation.deadlock_detector.action_at_detatch_server(server)
        server.cust = False
        server.busy = False
        individual.server = False
        if not server.busy_time:
            server.busy_time = (individual.exit_date - individual.service_start_date)
        else:
            server.busy_time += (individual.exit_date - individual.service_start_date)
        server.total_time = self.increment_time(self.get_now(), -server.start_date)
        if server.offduty:
            self.kill_server(server)

    def find_free_server(self, ind):
        """
        Finds a free server.
        """
        if isinf(self.c):
            return None
        
        if self.server_priority_function is None:
            all_servers = self.servers
        else:
            all_servers = sorted(
                self.servers, key=lambda srv: self.server_priority_function(srv, ind)
            )

        for svr in all_servers:
            if not svr.busy:
                return svr
        return None

    def find_next_individual(self):
        """
        Finds the next individual that should now finish service.
        """
        next_individual_indices = [i for i, ind in enumerate(
            self.all_individuals) if ind.service_end_date == self.next_event_date if ind.is_blocked==False]
        if len(next_individual_indices) > 1:
            next_individual_index = random_choice(next_individual_indices)
        else:
            next_individual_index = next_individual_indices[0]
        return self.all_individuals[next_individual_index], next_individual_index

    def find_server_utilisation(self):
        """
        Finds the overall server utilisation for the node.
        """
        if isinf(self.c) or self.c == 0:
            self.server_utilisation = None
        else:
            for server in self.servers:
                self.all_servers_total.append(server.total_time)
                self.all_servers_busy.append(server.busy_time)
            self.server_utilisation = sum(self.all_servers_busy) / sum(self.all_servers_total)

    def finish_service(self):
        """
        The next individual finishes service:
          - finds the individual to finish service
          - check if they need to change class
          - find their next node
          - release the individual if there is capacity at destination,
            otherwise cause blockage
        """
        next_individual, next_individual_index = self.find_next_individual()
        self.change_customer_class(next_individual)
        next_node = self.next_node(next_individual)
        next_individual.destination = next_node.id_number
        if not isinf(self.c):
            next_individual.server.next_end_service_date = float('Inf')
        if next_node.number_of_individuals < next_node.node_capacity:
            self.release(next_individual_index, next_node)
        else:
            self.block_individual(next_individual, next_node)

    def get_now(self):
        """
        Gets the current time.
        """
        return self.simulation.current_time

    def give_service_time_after_preemption(self, individual):
        """
        Either resample, restart or continue service time where it was left off
        """
        if individual.service_time == "resample":
            individual.service_time = self.get_service_time(individual)
        if individual.service_time == "restart":
            individual.service_time = individual.original_service_time
        if individual.service_time == "continue":
            individual.service_time = individual.time_left

    def have_event(self):
        """
        Has an event
        """
        if self.check_if_shiftchange() is True:
            self.change_shift()
        elif self.check_if_renege() is True:
            self.renege()
        elif self.check_if_classchange() is True:
            self.change_customer_class_while_waiting()
        else:
            self.finish_service()

    def increment_time(self, original, increment):
        """
        Increments the original time by the increment.
        """
        return original + increment

    def kill_server(self, srvr):
        """
        Kills a server when they go off duty.
        """
        srvr.total_time = self.increment_time(self.next_event_date, -srvr.start_date)
        self.overtime.append(self.increment_time(self.next_event_date, -srvr.shift_end))
        self.all_servers_busy.append(srvr.busy_time)
        self.all_servers_total.append(srvr.total_time)
        indx = self.servers.index(srvr)
        del self.servers[indx]

    def next_node(self, ind):
        """
        Finds the next node according the routing method:
          - if not process-based then sample from transtition matrix
          - if process-based then take the next value from the predefined route,
            removing the current node from the route
        """
        if not self.simulation.network.process_based:
            customer_class = ind.customer_class
            return random_choice(self.simulation.nodes[1:],
                self.transition_row[customer_class] + [1.0 - sum(
                self.transition_row[customer_class])])
        if ind.route == [] or ind.route[0] != self.id_number:
            raise ValueError('Individual process route sent to wrong node')
        ind.route.pop(0)
        if len(ind.route) == 0:
            next_node_number = -1
        else:
            next_node_number = ind.route[0]
        return self.simulation.nodes[next_node_number]

    
    def preempt(self, individual_to_preempt, next_individual):
        """
        Removes individual_to_preempt from service and replaces them with next_individual
        """
        server = individual_to_preempt.server
        individual_to_preempt.original_service_time = individual_to_preempt.service_time
        self.write_interruption_record(individual_to_preempt)
        individual_to_preempt.service_start_date = False
        individual_to_preempt.time_left = individual_to_preempt.service_end_date - self.get_now()
        individual_to_preempt.service_time = self.priority_preempt
        individual_to_preempt.service_end_date = False
        self.detatch_server(server, individual_to_preempt)
        self.decide_class_change(individual_to_preempt)
        self.attach_server(server, next_individual)
        next_individual.service_start_date = self.get_now()
        next_individual.service_time = self.get_service_time(next_individual)
        next_individual.service_end_date = self.increment_time(
            self.get_now(), next_individual.service_time)
        server.next_end_service_date = next_individual.service_end_date


    def release(self, next_individual_index, next_node):
        """
        Update node when an individual is released:
          - find the individual to release
          - remove from queue
          - record relevant information to data record
          - detatch individual from server
          - write record
          - update state tracker
          - begin service of any waiting customers
          - send individual to next destination
          - release any individuals blocked by this node
        """
        next_individual =  self.all_individuals[next_individual_index]
        self.individuals[next_individual.prev_priority_class].remove(next_individual)
        self.number_of_individuals -= 1
        next_individual.queue_size_at_departure = self.number_of_individuals
        next_individual.exit_date = self.get_now()
        self.write_individual_record(next_individual)
        if not isinf(self.c):
            self.detatch_server(next_individual.server, next_individual)
        self.reset_individual_attributes(next_individual)
        self.simulation.statetracker.change_state_release(self,
            next_node, next_individual, next_individual.is_blocked)
        self.begin_service_if_possible_release(next_individual)
        next_node.accept(next_individual)
        self.release_blocked_individual()

    def release_blocked_individual(self):
        """
        Releases an individual who becomes unblocked when
        another individual is released:
          - check if anyone is blocked by this node
          - find the individual who has been blocked the longest
          - remove that individual from blocked queue
          - check if that individual had their service interrupted
          - release that individual from their node
        """
        if self.len_blocked_queue > 0 and self.number_of_individuals < self.node_capacity:
            node_to_receive_from = self.simulation.nodes[self.blocked_queue[0][0]]
            individual_to_receive_index = [ind.id_number
                for ind in node_to_receive_from.all_individuals].index(
                self.blocked_queue[0][1])
            individual_to_receive = node_to_receive_from.all_individuals[individual_to_receive_index]
            self.blocked_queue.pop(0)
            self.len_blocked_queue -= 1
            if individual_to_receive.interrupted:
                individual_to_receive.interrupted = False
                node_to_receive_from.interrupted_individuals.remove(individual_to_receive)
                node_to_receive_from.number_interrupted_individuals -= 1
            node_to_receive_from.release(individual_to_receive_index, self)

    def renege(self):
        """
        Removes the appropriate customer from the queue;
        Resets that customer's reneging date;
        Send customer to their reneging destination.
        """
        reneging_individual = [ind for ind in self.all_individuals if ind.reneging_date == self.simulation.current_time][0]
        reneging_individual.reneging_date = float('Inf')
        next_node_number = self.simulation.network.customer_classes[reneging_individual.customer_class].reneging_destinations[self.id_number-1]
        next_node = self.simulation.nodes[next_node_number]
        self.individuals[reneging_individual.prev_priority_class].remove(reneging_individual)
        self.number_of_individuals -= 1
        reneging_individual.queue_size_at_departure = self.number_of_individuals
        reneging_individual.exit_date = self.get_now()
        self.write_reneging_record(reneging_individual)
        self.reset_individual_attributes(reneging_individual)
        self.simulation.statetracker.change_state_renege(self, next_node, reneging_individual, False)
        next_node.accept(reneging_individual)
        self.release_blocked_individual()


    def get_reneging_date(self, ind):
        """
        Returns the reneging date for a given individual.
        """
        dist = self.simulation.network.customer_classes[ind.customer_class].reneging_time_distributions[self.id_number-1]
        if dist is None:
            return float('inf')
        return self.simulation.current_time + dist.sample(t=self.simulation.current_time, ind=ind)

    def get_service_time(self, ind):
        """
        Returns a service time for the given customer class.
        """
        return self.simulation.service_times[self.id_number][ind.customer_class].sample(t=self.simulation.current_time, ind=ind)

    def take_servers_off_duty(self):
        """
        Gathers servers that should be deleted.
        """
        if self.schedule_preempt == False:
            to_delete = []
            for srvr in self.servers:
                srvr.shift_end = self.next_event_date
                if srvr.busy:
                    srvr.offduty = True
                else:
                    to_delete.append(srvr)
        else:
            to_delete = self.servers[::1]  # copy
            for s in self.servers:
                s.shift_end = self.next_event_date
                if s.cust is not False:
                    self.interrupted_individuals.append(s.cust)
                    s.cust.interrupted = True
                    self.number_interrupted_individuals += 1
                    s.cust.service_start_date = False
                    s.cust.original_service_time = self.interrupted_individuals[-1].service_time
                    s.cust.time_left = self.interrupted_individuals[-1].service_end_date - self.get_now()
                    s.cust.service_time = self.schedule_preempt
                    s.cust.service_end_date = False
            self.interrupted_individuals.sort(key=lambda x: (x.priority_class, x.arrival_date))
        for obs in to_delete:
            self.kill_server(obs)


    def update_next_event_date(self):
        """
        Finds the time of the next event at this node:
          - if infinite servers, return time for next individual to
            end service, or Inf
          - otherwise return minimum of next shift change, and time for
            next individual (who isn't blocked) to end service, or Inf
        """
        next_end_service = float("Inf")
        next_renege_date = float("Inf")
        next_class_change_date = float("Inf")
        if not isinf(self.c):
            for s in self.servers:
                if s.next_end_service_date < next_end_service:
                    next_end_service = s.next_end_service_date
            if self.reneging is True:
                for ind in self.all_individuals:
                    if (ind.reneging_date < next_renege_date) and not ind.server:
                        next_renege_date = ind.reneging_date
                self.next_renege_date = next_renege_date
            if self.dynamic_classes is True:
                for ind in self.all_individuals:
                    if (ind.class_change_date < next_class_change_date) and not ind.server:
                        next_class_change_date = ind.class_change_date
                self.next_class_change_date = next_class_change_date
        else:
            for ind in self.all_individuals:
                if not ind.is_blocked and ind.service_end_date >= self.get_now():
                    if ind.service_end_date < next_end_service:
                        next_end_service = ind.service_end_date
        if self.reneging or self.dynamic_classes or self.schedule:
            self.next_event_date = min(next_end_service, self.next_shift_change, self.next_renege_date, self.next_class_change_date)
        else:
            self.next_event_date = next_end_service

    def wrap_up_servers(self, current_time):
        """
        Updates the servers' total_time and busy_time
        as the end of the simulation run.
        """
        if not isinf(self.c):
            for srvr in self.servers:
                srvr.total_time = self.increment_time(current_time, -srvr.start_date)
                if srvr.busy:
                    srvr.busy_time += self.increment_time(current_time, -srvr.cust.service_start_date)


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
            - Server id
            - Record type
        """
        if isinf(self.c):
            server_id = False
        else:
            server_id = individual.server.id_number
        
        record = DataRecord(
            individual.id_number,
            individual.previous_class,
            individual.original_class,
            self.id_number,
            individual.arrival_date,
            individual.service_start_date - individual.arrival_date,
            individual.service_start_date,
            individual.service_end_date - individual.service_start_date,
            individual.service_end_date,
            individual.exit_date - individual.service_end_date,
            individual.exit_date,
            individual.destination,
            individual.queue_size_at_arrival,
            individual.queue_size_at_departure,
            server_id,
            'service')
        individual.data_records.append(record)

    def write_interruption_record(self, individual):
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
            - Server id
            - Record type
        """
        record = DataRecord(
            individual.id_number,
            individual.previous_class,
            individual.original_class,
            self.id_number,
            individual.arrival_date,
            individual.service_start_date - individual.arrival_date,
            individual.service_start_date,
            individual.original_service_time,
            nan,
            nan,
            self.get_now(),
            nan,
            individual.queue_size_at_arrival,
            individual.queue_size_at_departure,
            individual.server.id_number,
            'interrupted service')
        individual.data_records.append(record)


    def write_reneging_record(self, individual):
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
            - Server id
            - Record type
        """        
        record = DataRecord(
            individual.id_number,
            individual.previous_class,
            individual.original_class,
            self.id_number,
            individual.arrival_date,
            individual.exit_date - individual.arrival_date,
            nan,
            nan,
            nan,
            nan,
            individual.exit_date,
            individual.destination,
            individual.queue_size_at_arrival,
            individual.queue_size_at_departure,
            nan,
            'renege')
        individual.data_records.append(record)

    def reset_individual_attributes(self, individual):
        """
        Resets the attributes of an individual
        """
        individual.arrival_date = False
        individual.service_time = False
        individual.service_start_date = False
        individual.service_end_date = False
        individual.exit_date = False
        individual.queue_size_at_arrival = False
        individual.queue_size_at_departure = False
        individual.destination = False


    def date_from_schedule_generator(self, boundaries):
        """
        A generator that yields the next time according to a given schedule.
        """
        boundaries_len = len(boundaries)
        index = 0
        date = 0
        while True:
            date = self.increment_time(
                boundaries[index % boundaries_len],
                (index) // boundaries_len * boundaries[-1])
            index += 1
            yield date
