"""
Usage: experiment.py <dir_name> [<sffx>]

Arguments
	dir_name    : name of the directory from which to read in parameters and write data files
    suff        : optional suffix to add to the data file name

Options
    -h          : displays this help file
"""
from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import docopt
import networkx as nx
from simulation import *

if __name__ == '__main__':
	arguments = docopt.docopt(__doc__)
	dirname = arguments['<dir_name>']
	sffx = arguments['<sffx>']
	Q = Simulation(dirname, sffx)
	Q.simulate_until_max_time()
	Q.write_records_to_file()