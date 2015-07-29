"""
Usage: experiment.py <dir_name>

Arguments
    dir_name    : name of the directory from which to read in parameters and write data files

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




class Experiment:
	"""
	A class to hold the current experiment
	"""
	def __init__(self, dirname):
		"""
		Initialises the experiment
		"""
		self.root = os.getcwd()
		self.directory = os.path.join(self.root, dirname)
		self.parameters = self.load_parameters()

	def load_parameters(self):
		"""
		Loads the parameters into the model
		"""
		parameter_file_name = self.directory + 'parameters.yml'
		parameter_file = open(parameter_file_name, 'r')
		parameters = yaml.load(parameter_file)
		parameter_file.close()

		return parameters

	def run_experiment(self):
		"""
		Runs the experiment
		"""
		self.simulation = Simulation(self.directory)
		times = self.simulation.simulate_until_deadlock()


if __name__ == '__main__':
	arguments = docopt.docopt(__doc__)
	dirname = arguments['<dir_name>']
	E = Experiment(dirname)
	E.run_experiment()