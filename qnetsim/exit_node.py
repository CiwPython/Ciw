from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import networkx as nx

from individual import Individual

class ExitNode:
    """
    Class for the exit node on our network
    """
    def __init__(self, max_simulation_time):
        """
        Initialise a node.

        An example of an exit node instance.
            >>> N = ExitNode(100)
            >>> N.individuals
            []
            >>> N.id_number
            -1
            >>> N.next_event_date
            100

        And another.
            >>> N = ExitNode(4)
            >>> N.id_number
            -1
            >>> N.next_event_date
            4
        """
        self.individuals = []
        self.id_number = -1
        self.next_event_date = max_simulation_time
        self.node_capacity = "Inf"

    def __repr__(self):
        """
        Representation of a node::

        An example of how an exit node is represented.
            >>> N = ExitNode(500)
            >>> N
            Exit Node

        And another.
            >>> N = ExitNode(320)
            >>> N
            Exit Node
        """
        return 'Exit Node'

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

        An example of a customer leaving the system (getting accepted to the exit node).
            >>> N = ExitNode(200)
            >>> N.individuals
            []
            >>> N.next_event_date
            200
            >>> next_individual = Individual(5, 1)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]
            >>> N.next_event_date
            200

        Another example.
            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('datafortesting/logs_test_for_simulation/'))
            >>> N = Q.nodes[-1]
            >>> N.individuals
            []
            >>> N.next_event_date
            'Inf'
            >>> next_individual = Individual(3)
            >>> N.accept(next_individual, 3)
            >>> N.individuals
            [Individual 3]
            >>> N.next_event_date
            'Inf'
        """
        self.individuals.append(next_individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

        An example showing that this method does nothing.
            >>> N = ExitNode(25)
            >>> N.next_event_date
            25
            >>> N.update_next_event_date()
            >>> N.next_event_date
            25

        And again.
            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('datafortesting/logs_test_for_simulation/'))
            >>> N = Q.nodes[-1]
            >>> N.next_event_date
            'Inf'
            >>> N.update_next_event_date()
            >>> N.next_event_date
            'Inf'

        And again, even when parameters don't make sense.
            >>> N = ExitNode(False)
            >>> N.next_event_date
            False
            >>> N.update_next_event_date()
            >>> N.next_event_date
            False
        """
        pass