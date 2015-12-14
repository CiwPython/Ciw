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
            self.finish_service

        self.finish_service()

    def change_shift(self):
        """
        Add servers and deletes or indicates which servers should go off duty
        """
        highest_id = max([srvr.id_number for srvr in self.servers])
        shift = self.next_event_date%self.cyclelength

        self.take_servers_off_duty()

        self.add_new_server(shift,highest_id)

        indx = [obs[0] for obs in self.schedule].index(shift)
        self.c = self.schedule[indx][1]

    def take_servers_off_duty(self):
        """
        Gathers servers that should be deleted

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_server_schedule/'))
            >>> N = Q.transitive_nodes[0]
            >>> N.add_new_server(90, 1)
            >>> N.servers
            [Server 1 at Node 1, Server 2 at Node 1, Server 3 at Node 1, Server 4 at Node 1]
            >>> N.servers[1].busy = True
            >>> N.servers[2].busy = True
            >>> [obs.busy for obs in N.servers]
            [False, True, True, False]
            >>> [obs.offduty for obs in N.servers]
            [False, False, False, False]

            >>> N.take_servers_off_duty()
            >>> N.servers
            [Server 2 at Node 1, Server 3 at Node 1]
            >>> [obs.busy for obs in N.servers]
            [True, True]
            >>> [obs.offduty for obs in N.servers]
            [True, True]
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

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_server_schedule/'))
            >>> N = Q.transitive_nodes[0]
            >>> N.next_event_date = 12.0
            >>> N.check_if_shiftchange()
            False
            >>> N.next_event_date = 30.0
            >>> N.check_if_shiftchange()
            True

            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = Q.transitive_nodes[0]
            >>> N.next_event_date = 12.0
            >>> N.check_if_shiftchange()
            False
            >>> N.next_event_date = 30.0
            >>> N.check_if_shiftchange()
            False

        """
        if self.scheduled_servers:
            return self.next_event_date == self.masterschedule[0]
        return False


    def finish_service(self):
        """
        The next individual finishes service

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> from individual import Individual
            >>> seed(4)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = Q.transitive_nodes[0]
            >>> inds = [Individual(i+1) for i in range(3)]
            >>> for current_time in [0.01, 0.02, 0.03]:
            ...     N.accept(inds[int(current_time*100 - 1)], current_time)
            >>> N.individuals
            [Individual 1, Individual 2, Individual 3]
            >>> N.update_next_event_date(0.03)
            >>> round(N.next_event_date, 5)
            0.03604
            >>> N.finish_service()
            >>> N.individuals
            [Individual 1, Individual 3]
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
        >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> seed(14)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_dynamic_classes/'))
            >>> N1 = Q.transitive_nodes[0]
            >>> ind = Individual(254, 0)
            >>> ind.customer_class
            0
            >>> ind.previous_class
            0
            >>> N1.change_customer_class(ind)
            >>> ind.customer_class
            0
            >>> ind.previous_class
            0
            >>> N1.change_customer_class(ind)
            >>> ind.customer_class
            0
            >>> ind.previous_class
            0
            >>> N1.change_customer_class(ind)
            >>> ind.customer_class
            1
            >>> ind.previous_class
            0
            >>> N1.change_customer_class(ind)
            >>> ind.customer_class
            1
            >>> ind.previous_class
            1

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

            >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> seed(4)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_deadlock_sim/'))
            >>> inds = [Individual(i+1) for i in range(7)]
            >>> N1 = Q.transitive_nodes[0]
            >>> N1.individuals = inds[:6]
            >>> N2 = Q.transitive_nodes[1]
            >>> N2.accept(inds[6], 2)
            >>> inds[6].is_blocked
            False
            >>> N1.blocked_queue
            []
            >>> Q.digraph.edges()
            []
            >>> N2.block_individual(inds[6], N1)
            >>> inds[6].is_blocked
            True
            >>> N1.blocked_queue
            [(2, 7)]
            >>> Q.digraph.edges()
            [('Server 1 at Node 2', 'Server 2 at Node 1'), ('Server 1 at Node 2', 'Server 1 at Node 1')]
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

            >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> seed(4)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = Q.transitive_nodes[0]
            >>> inds = [Individual(i+1) for i in range(3)]
            >>> for current_time in [0.01, 0.02, 0.03]:
            ...     N.accept(inds[int(current_time*100 - 1)], current_time)
            >>> N.individuals
            [Individual 1, Individual 2, Individual 3]
            >>> N.update_next_event_date(0.03)
            >>> round(N.next_event_date, 5)
            0.03604
            >>> N.individuals[1].exit_date = 0.04 #shouldn't affect the next event date
            >>> N.update_next_event_date(N.next_event_date)
            >>> round(N.next_event_date, 5)
            0.03708
            >>> N.release(1, Q.transitive_nodes[1], N.next_event_date)
            >>> N.individuals
            [Individual 1, Individual 3]
            >>> N.update_next_event_date(N.next_event_date)
            >>> round(N.next_event_date, 5)
            0.06447
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

            >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> seed(50)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_deadlock_sim/'))
            >>> inds = [Individual(i) for i in range(30)]
            >>> Q.transitive_nodes[0].individuals = inds
            >>> ind = Q.transitive_nodes[0].individuals[Q.transitive_nodes[0].c - 1]
            >>> ind.service_time = 3.14
            >>> ind.arrival_date = 100.0
            >>> Q.digraph.nodes()
            ['Server 2 at Node 1', 'Server 1 at Node 2', 'Server 1 at Node 1']
            >>> ind.arrival_date
            100.0
            >>> ind.service_time
            3.14
            >>> ind.service_start_date
            False
            >>> ind.service_end_date
            False
            >>> Q.transitive_nodes[0].begin_service_if_possible_release(200.0)
            >>> ind.arrival_date
            100.0
            >>> round(ind.service_time,5)
            3.14
            >>> ind.service_start_date
            200.0
            >>> round(ind.service_end_date,5)
            203.14

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

            >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_deadlock_sim/'))
            >>> N1 = Q.transitive_nodes[0]
            >>> N2 = Q.transitive_nodes[1]
            >>> N1.individuals = [Individual(i) for i in range(N1.c + 3)]
            >>> N2.individuals = [Individual(i + 100) for i in range(N2.c + 4)]

            >>> for ind in N1.individuals[:2]:
            ...     N1.attach_server(N1.find_free_server(), ind)
            >>> for ind in N2.individuals[:1]:
            ...     N2.attach_server(N2.find_free_server(), ind)

            >>> N1.individuals
            [Individual 0, Individual 1, Individual 2, Individual 3, Individual 4]
            >>> N2.individuals
            [Individual 100, Individual 101, Individual 102, Individual 103, Individual 104]
            >>> N1.release_blocked_individual(100)
            >>> N1.individuals
            [Individual 0, Individual 1, Individual 2, Individual 3, Individual 4]
            >>> N2.individuals
            [Individual 100, Individual 101, Individual 102, Individual 103, Individual 104]

            >>> N1.blocked_queue = [(1, 1), (2, 100)]
            >>> rel_ind = N1.individuals.pop(0)
            >>> N1.detatch_server(rel_ind.server, rel_ind)

            >>> N1.release_blocked_individual(110)
            >>> N1.individuals
            [Individual 2, Individual 3, Individual 4, Individual 100, Individual 1]
            >>> N2.individuals
            [Individual 101, Individual 102, Individual 103, Individual 104]
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

            >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> Q.state = [[0, 0], [0, 0], [2, 1], [0, 0]]
            >>> N = Q.transitive_nodes[2]
            >>> inds = [Individual(i) for i in range(3)]
            >>> N.individuals = inds
            >>> N.change_state_release(inds[0])
            >>> Q.state
            [[0, 0], [0, 0], [1, 1], [0, 0]]
            >>> inds[1].is_blocked = True
            >>> N.change_state_release(inds[1])
            >>> Q.state
            [[0, 0], [0, 0], [1, 0], [0, 0]]

        """
        if next_individual.is_blocked:
            self.simulation.state[self.id_number-1][1] -= 1
        else:
            self.simulation.state[self.id_number-1][0] -= 1

    def change_state_block(self):
        """
        Changes the state of the system when a customer gets blocked

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> Q.state = [[0, 0], [0, 0], [2, 1], [0, 0]]
            >>> N = Q.transitive_nodes[2]
            >>> N.change_state_block()
            >>> Q.state
            [[0, 0], [0, 0], [1, 2], [0, 0]]
            >>> N.change_state_block()
            >>> Q.state
            [[0, 0], [0, 0], [0, 3], [0, 0]]

        """
        self.simulation.state[self.id_number-1][1] += 1
        self.simulation.state[self.id_number-1][0] -= 1

    def change_state_accept(self):
        """
        Changes the state of the system when a customer gets blocked

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> Q.state = [[0, 0], [0, 0], [2, 1], [0, 0]]
            >>> N = Q.transitive_nodes[2]
            >>> N.change_state_accept()
            >>> Q.state
            [[0, 0], [0, 0], [3, 1], [0, 0]]
            >>> N.change_state_accept()
            >>> Q.state
            [[0, 0], [0, 0], [4, 1], [0, 0]]

        """
        self.simulation.state[self.id_number-1][0] += 1

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

            >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> seed(6)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = Q.transitive_nodes[0]
            >>> N.next_event_date = 0.0
            >>> N.individuals
            []
            >>> ind1 = Individual(1)
            >>> ind2 = Individual(2)
            >>> ind3 = Individual(3)
            >>> ind4 = Individual(4)
            >>> ind5 = Individual(5)
            >>> ind6 = Individual(6)
            >>> ind7 = Individual(7)
            >>> ind8 = Individual(8)
            >>> ind9 = Individual(9)
            >>> ind10 = Individual(10)

            >>> N.accept(ind1, 0.01)
            >>> N.individuals
            [Individual 1]
            >>> ind1.arrival_date
            0.01
            >>> ind1.service_start_date
            0.01
            >>> round(ind1.service_time, 5)
            0.18695
            >>> round(ind1.service_end_date, 5)
            0.19695

            >>> N.accept(ind2, 0.02)
            >>> N.accept(ind3, 0.03)
            >>> N.accept(ind4, 0.04)
            >>> N.individuals
            [Individual 1, Individual 2, Individual 3, Individual 4]
            >>> round(ind4.arrival_date, 5)
            0.04
            >>> round(ind4.service_start_date, 5)
            0.04
            >>> round(ind4.service_time, 5)
            0.1637
            >>> round(ind4.service_end_date, 5)
            0.2037

            >>> N.accept(ind5, 0.05)
            >>> N.accept(ind6, 0.06)
            >>> N.accept(ind7, 0.07)
            >>> N.accept(ind8, 0.08)
            >>> N.accept(ind9, 0.09)
            >>> N.accept(ind10, 0.1)
            >>> N.individuals
            [Individual 1, Individual 2, Individual 3, Individual 4, Individual 5, Individual 6, Individual 7, Individual 8, Individual 9, Individual 10]
            >>> round(ind10.arrival_date, 5)
            0.1
            >>> ind10.service_start_date
            False
            >>> round(ind10.service_time, 5)
            0.16534
        """
        next_individual.exit_date = False
        next_individual.is_blocked = False
        self.begin_service_if_possible_accept(next_individual, current_time)
        self.individuals.append(next_individual)
        self.change_state_accept()

    def begin_service_if_possible_accept(self, next_individual, current_time):
        """
        Begins the service of the next individual, giving that customer a service time, end date and node

            >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> seed(50)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_deadlock_sim/'))
            >>> ind = Individual(1)
            >>> Q.digraph.nodes()
            ['Server 2 at Node 1', 'Server 1 at Node 2', 'Server 1 at Node 1']
            >>> ind.arrival_date
            False
            >>> ind.service_time
            False
            >>> ind.service_start_date
            False
            >>> ind.service_end_date
            False
            >>> Q.transitive_nodes[0].begin_service_if_possible_accept(ind, 300)
            >>> ind.arrival_date
            300
            >>> round(ind.service_time,5)
            0.03382
            >>> ind.service_start_date
            300
            >>> round(ind.service_end_date,5)
            300.03382

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

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_server_schedule/'))
            >>> N = Q.transitive_nodes[0]
            >>> s = N.servers[0]
            >>> N.servers
            [Server 1 at Node 1]
            >>> N.kill_server(s)
            >>> N.servers
            []


        """
        indx = self.servers.index(srvr)
        del self.servers[indx]

    def add_new_server(self, shift, highest_id):
        """
        Add appropriate amount of servers for the given shift

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_server_schedule/'))
            >>> N = Q.transitive_nodes[0]
            >>> s = 90
            >>> N.servers
            [Server 1 at Node 1]
            >>> N.add_new_server(s,1)
            >>> N.servers
            [Server 1 at Node 1, Server 2 at Node 1, Server 3 at Node 1, Server 4 at Node 1]

        """
        indx = [obs[0] for obs in self.schedule].index(shift)
        num_servers = self.schedule[indx][1]
        for i in range(num_servers):
            self.servers.append(Server(self, highest_id+i+1))


    def update_next_event_date(self, current_time):
        """
        Finds the time of the next event at this node

            >>> from simulation import Simulation
            >>> from individual import Individual
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = Q.transitive_nodes[0]
            >>> N.next_event_date
            'Inf'
            >>> N.individuals
            []
            >>> N.update_next_event_date(0.0)
            >>> N.next_event_date
            'Inf'

            >>> ind1 = Individual(1)
            >>> ind1.arrival_date = 0.3
            >>> ind1.service_time = 0.2
            >>> ind1.service_end_date = 0.5
            >>> N.next_event_date = 0.3
            >>> N.individuals = [ind1]
            >>> N.update_next_event_date(N.next_event_date)
            >>> N.next_event_date
            0.5

            >>> ind2 = Individual(2)
            >>> ind2.arrival_date = 0.4
            >>> ind2.service_time = 0.2
            >>> ind2.service_end_date = 0.6
            >>> ind2.exit_date = False

            >>> N.individuals = [ind1, ind2]
            >>> N.update_next_event_date(N.next_event_date)
            >>> N.next_event_date
            0.6

            >>> ind2.exit_date = 0.9 # shouldn't affect next_event_date

            >>> N.update_next_event_date(N.next_event_date)
            >>> N.next_event_date
            'Inf'


            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_server_schedule/'))
            >>> N = Q.transitive_nodes[0]
            >>> N.next_event_date
            30
            >>> N.individuals
            []
            >>> N.update_next_event_date(0.0)
            >>> N.next_event_date
            30

            >>> ind1 = Individual(1)
            >>> ind1.arrival_date = 0.3
            >>> ind1.service_time = 0.2
            >>> ind1.service_end_date = 0.5
            >>> N.next_event_date = 0.3
            >>> N.individuals = [ind1]
            >>> N.update_next_event_date(N.next_event_date)
            >>> N.next_event_date
            0.5

            >>> ind2 = Individual(2)
            >>> ind2.arrival_date = 0.7
            >>> ind2.service_time = 0.2
            >>> ind2.service_end_date = 0.9
            >>> ind2.exit_date = False

            >>> N.individuals = [ind1, ind2]
            >>> N.update_next_event_date(N.next_event_date)
            >>> N.next_event_date
            30

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

        An example showing a node choosing both nodes and exit node randomly.
            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> seed(6)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> node = Q.transitive_nodes[0]
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 4

        Another example.
            >>> seed(54)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> node = Q.transitive_nodes[2]
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 4
            >>> node.next_node(0)
            Node 2

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

        An example showing the data records written; can only write records once an exit date has been determined.
            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> from individual import Individual
            >>> seed(7)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = Q.transitive_nodes[0]
            >>> ind = Individual(6)
            >>> N.accept(ind, 3)
            >>> ind.service_start_date = 3.5
            >>> ind.exit_date = 9
            >>> N.write_individual_record(ind)
            >>> ind.data_records[1][0].arrival_date
            3
            >>> ind.data_records[1][0].wait
            0.5
            >>> ind.data_records[1][0].service_start_date
            3.5
            >>> round(ind.data_records[1][0].service_time, 5)
            0.07894
            >>> round(ind.data_records[1][0].service_end_date, 5)
            3.57894
            >>> round(ind.data_records[1][0].blocked, 5)
            5.42106
            >>> ind.data_records[1][0].exit_date
            9
            >>> ind.data_records[1][0].customer_class
            0
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