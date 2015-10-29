from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import networkx as nx

class Individual:
    """
    Class for an individual
    """
    def __init__(self, id_number, customer_class=0):
        """
        Initialise an individual

        An example of an Individual instance.
            >>> i = Individual(22, 3)
            >>> i.arrival_date
            False
            >>> i.service_start_date
            False
            >>> i.service_time
            False
            >>> i.service_end_date
            False
            >>> i.id_number
            22
            >>> i.data_records
            {}
            >>> i.customer_class
            3
            >>> i.previous_class
            3

        Another example of an individual instance.
            >>> i = Individual(5)
            >>> i.arrival_date
            False
            >>> i.service_start_date
            False
            >>> i.service_time
            False
            >>> i.service_end_date
            False
            >>> i.id_number
            5
            >>> i.data_records
            {}
            >>> i.customer_class
            0
            >>> i.previous_class
            0
        """
        self.arrival_date = False
        self.service_start_date = False
        self.service_time = False
        self.service_end_date = False
        self.exit_date = False
        self.id_number = id_number
        self.data_records = {}
        self.customer_class = customer_class
        self.previous_class = customer_class
        self.is_blocked = False
        self.server = False

    def __repr__(self):
        """
        Represents an Individual instance as a string

        An example of how an intance in represented.
            >>> i = Individual(3, 6)
            >>> i
            Individual 3

        Another example of how an individual is represented.
            >>> i = Individual(93, 2)
            >>> i
            Individual 93

        Although individuals should be represented by unique integers, they can be called anything.
            >>> i = Individual('twelve', 2)
            >>> i
            Individual twelve
        """
        return 'Individual %s' % self.id_number