from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import networkx as nx

class DataRecord:
    """
    A class for a data record
    """
    def __init__(self, arrival_date, service_time, service_start_date, exit_date, node):
        """
        An example of a data record instance.
            >>> r = DataRecord(2, 3, 2, 8, 1)
            >>> r.arrival_date
            2
            >>> r.wait
            0
            >>> r.service_start_date
            2
            >>> r.service_time
            3
            >>> r.service_end_date
            5
            >>> r.blocked
            3
            >>> r.exit_date
            8
            >>> r.node
            1

        Another example of a data record instance.
            >>> r = DataRecord(5.7, 2.1, 8.2, 10.3, 1)
            >>> r.arrival_date
            5.7
            >>> round(r.wait, 5)
            2.5
            >>> r.service_start_date
            8.2
            >>> r.service_time
            2.1
            >>> round(r.service_end_date, 5)
            10.3
            >>> round(r.blocked, 5)
            0.0
            >>> r.exit_date
            10.3
            >>> r.node
            1
        """
        if exit_date < arrival_date:
            raise ValueError('Arrival date should preceed exit date')

        if service_time < 0:
            raise ValueError('Service time should be positive')

        self.arrival_date = arrival_date
        self.service_time = service_time
        self.service_start_date = service_start_date
        self.exit_date = exit_date

        self.service_end_date = service_start_date + service_time
        self.wait = service_start_date - arrival_date
        self.blocked = exit_date - self.service_end_date
        self.node = node
