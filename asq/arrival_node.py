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
            >>> from import_params import load_parameters
            >>> seed(5)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = ArrivalNode(Q)
            >>> N.next_event_date
            0.004400313282484739
            >>> N.number_of_individuals
            0
            >>> N.next_event_dates_dict
            {1: {0: 0.21104109989445083, 1: 0.14156146233571273, 2: 0.3923690877168693}, 2: {0: 0.12188255510498336, 1: 0.004400313282484739, 2: 0.24427756009692883}, 3: {0: 0.08194634729677806, 1: 0.41350975417151004, 2: 0.7256307838738146}, 4: {0: 0.17388232234898224, 1: 0.39881841448612376, 2: 0.2987813628296875}}
        """

        self.simulation = simulation
        self.number_of_individuals = 0
        self.next_event_dates_dict = {nd + 1:{cls:False for cls in range(self.simulation.parameters['Number_of_classes'])} for nd in range(self.simulation.number_of_nodes)}
        self.initialise_next_event_dates_dict()
        self.find_next_event_date()

    def initialise_next_event_dates_dict(self):
        """
        Initialises the next event dates dictionary with random times for each node and class

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> seed(6)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = ArrivalNode(Q)
            >>> N.next_event_dates_dict
            {1: {0: 0.43622825409205973, 1: 0.26722324060759933, 2: 0.38642562730637603}, 2: {0: 0.16369523112791148, 1: 0.07147095652645417, 2: 0.8065738413825493}, 3: {0: 0.4088480189803173, 1: 0.0514323247956018, 2: 0.8132038176069183}, 4: {0: 1.157375143843249, 1: 0.46492767142177205, 2: 0.8176876726520277}}
            >>> N.initialise_next_event_dates_dict()
            >>> N.next_event_dates_dict
            {1: {0: 0.03258707753070194, 1: 0.8054262557674572, 2: 0.8168179514964325}, 2: {0: 0.08416713808943652, 1: 0.03282452990969279, 2: 0.219602384651059}, 3: {0: 0.25190890679024003, 1: 0.05735978139796031, 2: 1.5117882120904502}, 4: {0: 0.8881158889281887, 1: 0.05605926220383697, 2: 2.1307650867721044}}
        """
        for nd in self.next_event_dates_dict:
            for cls in self.next_event_dates_dict[nd]:
                if self.simulation.lmbda == 0:
                    self.next_event_dates_dict[nd][cls] = 'Inf'
                else:
                    self.next_event_dates_dict[nd][cls] = expovariate(self.simulation.lmbda[cls][nd-1])


    def __repr__(self):
        """
        Representation of a node::

        An example showing how an arrival node is represented.
            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
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
            >>> from import_params import load_parameters
            >>> seed(1)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> Q.transitive_nodes[3].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.find_next_event_date()
            >>> N.next_event_date
            0.0010541371000842435
            >>> N.next_node
            1
            >>> N.have_event()
            >>> Q.transitive_nodes[0].individuals
            [Individual 1]
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> Q.transitive_nodes[3].individuals
            []
            >>> round(N.next_event_date,5)
            0.00518

        Another example.
            >>> seed(12)
            >>> from import_params import load_parameters
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> Q.transitive_nodes[2].individuals
            []
            >>> Q.transitive_nodes[3].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.find_next_event_date()
            >>> N.next_event_date
            0.01938490320079715
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
            0.02021
        """
        self.number_of_individuals += 1
        next_individual = Individual(self.number_of_individuals, self.next_class)
        next_node = self.simulation.transitive_nodes[self.next_node-1]
        if len(next_node.individuals) < next_node.node_capacity:
            next_node.accept(next_individual, self.next_event_date)
        self.next_event_dates_dict[self.next_node][self.next_class] += expovariate(self.simulation.lmbda[self.next_class][self.next_node-1])
        self.find_next_event_date()

    def find_next_event_date(self):
        """
        Finds the time of the next event at this node

            >>> from simulation import Simulation
            >>> from import_params import load_parameters
            >>> seed(1)
            >>> Q = Simulation(load_parameters('tests/datafortesting/logs_test_for_simulation/'))
            >>> N = ArrivalNode(Q)
            >>> N.next_event_date
            0.0010541371000842435
            >>> N.find_next_event_date()
            >>> round(N.next_event_date, 5)
            0.00105
            >>> N.next_node
            1
            >>> N.next_class
            1

            >>> N.have_event()
            >>> N.find_next_event_date()
            >>> round(N.next_event_date, 5)
            0.00518
            >>> N.next_node
            3
            >>> N.next_class
            1
        """
        times = [[self.next_event_dates_dict[nd+1][cls] for cls in range(len(self.next_event_dates_dict[1]))] for nd in range(len(self.next_event_dates_dict))]
        mintimes = [min(obs) for obs in times]
        nd = mintimes.index(min(mintimes))
        cls = times[nd].index(min(times[nd]))
        self.next_node = nd + 1
        self.next_class = cls
        self.next_event_date = self.next_event_dates_dict[self.next_node][self.next_class]

    def update_next_event_date(self):
        """
        Passes, updatign enxt event happens at time of event
        """
        pass
