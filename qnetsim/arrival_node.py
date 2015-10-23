from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import networkx as nx

from individual import Individual


class ArrivalNode:
    """
    Class for the arrival node on our network
    """
    def __init__(self, simulation):
        """
        Initialise a node.

        Here is an example::
            >>> from simulation import Simulation
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = ArrivalNode(Q)
            >>> N.lmbda
            35.5
            >>> N.transition_row_given_class
            [[0.2, 0.4666666666666667, 0.26666666666666666, 0.06666666666666667], [0.13333333333333333, 0.2, 0.4, 0.26666666666666666], [0.36363636363636365, 0.18181818181818182, 0.36363636363636365, 0.09090909090909091]]
            >>> N.next_event_date
            0.0
            >>> N.number_of_individuals
            0
            >>> N.cum_transition_row
            [[0.2, 0.6666666666666667, 0.9333333333333333, 1.0], [0.13333333333333333, 0.33333333333333337, 0.7333333333333334, 1.0], [0.36363636363636365, 0.5454545454545454, 0.9090909090909091, 1.0]]
            >>> N.cum_class_probs
            [0.4225352112676056, 0.8450704225352113, 1.0]
        """

        self.simulation = simulation
        self.lmbda = self.simulation.overall_lmbda
        self.class_probs = self.simulation.class_probs
        self.transition_row_given_class = self.simulation.node_given_class_probs
        self.next_event_date = 0.0
        self.number_of_individuals = 0
        self.cum_transition_row = self.find_cumulative_transition_row()
        self.cum_class_probs = self.find_cumulative_class_probs()

    def find_cumulative_transition_row(self):
        """
        Finds the cumulative transition row for the arrival node

        An example of finding the cumulative transition row of an arrival node.
            >>> from simulation import Simulation
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = ArrivalNode(Q)
            >>> [[round(pr, 2) for pr in N.cum_transition_row[cls]] for cls in range(len(N.cum_transition_row))]
            [[0.2, 0.67, 0.93, 1.0], [0.13, 0.33, 0.73, 1.0], [0.36, 0.55, 0.91, 1.0]]
        """

        cum_transition_row = []
        for cls in range(len(self.transition_row_given_class)):
            sum_p = 0
            cum_transition_row.append([])
            for p in self.transition_row_given_class[cls]:
                sum_p += p
                cum_transition_row[cls].append(sum_p)
        return cum_transition_row

    def find_cumulative_class_probs(self):
        """
        Returns the cumulative class probs

        An example of finding the cumulative probabilities of a new customer being in each class.
            >>> from simulation import Simulation
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = ArrivalNode(Q)
            >>> N.find_cumulative_class_probs()
            [0.4225352112676056, 0.8450704225352113, 1.0]
        """

        cum_class_probs = []
        sum_p = 0
        for p in self.class_probs:
            sum_p += p
            cum_class_probs.append(sum_p)
        return cum_class_probs

    def __repr__(self):
        """
        Representation of a node::

        An example showing how an arrival node is represented.
            >>> from simulation import Simulation
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = ArrivalNode(Q)
            >>> N
            Arrival Node
        """
        return 'Arrival Node'

    def have_event(self):
        """
        Update node when a service happens.

        An example of creating an individual instance, releasing it to a node, and then updating its next event time.
            >>> from simulation import Simulation
            >>> seed(1)
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> Q.transitive_nodes[3].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.lmbda
            35.5
            >>> N.next_event_date
            0.0
            >>> N.have_event()
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            [Individual 1]
            >>> Q.transitive_nodes[3].individuals
            []
            >>> round(N.next_event_date,5)
            0.01927

        Another example.
            >>> seed(12)
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> Q.transitive_nodes[3].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.next_event_date
            0.0
            >>> N.have_event()
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            [Individual 1]
            >>> Q.transitive_nodes[3].individuals
            []
            >>> round(N.next_event_date,5)
            0.00433
        """
        self.number_of_individuals += 1
        next_individual = Individual(self.number_of_individuals, self.choose_class())
        next_node = self.next_node(next_individual.customer_class)
        if len(next_node.individuals) < next_node.node_capacity:
            next_node.accept(next_individual, self.next_event_date)
        self.update_next_event_date()

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            >>> from simulation import Simulation
            >>> seed(1)
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = ArrivalNode(Q)
            >>> N.next_event_date
            0.0
            >>> N.update_next_event_date()
            >>> round(N.next_event_date, 5)
            0.00406
        """
        self.next_event_date += expovariate(self.lmbda)

    def next_node(self, customer_class):
        """
        Finds the next node according the random distribution.

        An example of finding the individual's starting node.
            >>> from simulation import Simulation
            >>> seed(1)
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = Q.nodes[0]
            >>> N.cum_transition_row
            [[0.2, 0.6666666666666667, 0.9333333333333333, 1.0], [0.13333333333333333, 0.33333333333333337, 0.7333333333333334, 1.0], [0.36363636363636365, 0.5454545454545454, 0.9090909090909091, 1.0]]
            >>> N.next_node(0)
            Node 1
            >>> N.next_node(0)
            Node 3
            >>> N.next_node(0)
            Node 3

        And another example.
            >>> seed(401)
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = Q.nodes[0]
            >>> N.next_node(0)
            Node 2
            >>> N.next_node(0)
            Node 2
            >>> N.next_node(0)
            Node 3
        """
        rnd_num = random()
        for p in range(len(self.cum_transition_row[customer_class])):
            if rnd_num < self.cum_transition_row[customer_class][p]:
                return self.simulation.transitive_nodes[p]

    def choose_class(self):
        """
        Returns the customer's class from the class probabilities

            >>> from simulation import Simulation
            >>> seed(6)
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = ArrivalNode(Q)
            >>> N.choose_class()
            1
        """
        rnd_num = random()
        for p in range(len(self.cum_class_probs)):
            if rnd_num < self.cum_class_probs[p]:
                return p