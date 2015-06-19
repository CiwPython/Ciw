"""
Usage: experiment_parallelprocessing.py <dir_name> <split_list>...

Arguments
    dir_name    : name of the directory from which to read in parameters and write data files
    split_list	: list of parameters

Options
    -h          : displays this help file
"""
from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer, reader
import yaml
import shutil
import docopt
import networkx as nx
from simulation import *
from multiprocessing import Pool


class Experiment:
	"""
	A class to hold the current experiment
	"""
	def __init__(self, dirname, current_parameter):
		"""
		Initialises the experiment

			>>> E = Experiment('datafortesting/logs_test_for_experiment/')
			>>> E.parameters
			{'Arrival_rates': {'Class 0': [24.0, 20.0]}, 'Number_of_nodes': 2, 'Simulation_time': 2500, 'Number_of_servers': [2, 2], 'Queue_capacities': [2, 3], 'Number_of_classes': 1, 'Service_rates': {'Class 0': [['Exponential', 7.0], ['Exponential', 7.0]]}, 'Transition_matrices': {'Class 0': [[0.2, 0.2], [0.2, 0.2]]}}
		"""
		self.root = os.getcwd()
		self.directory = os.path.join(self.root, dirname)
		self.current_parameter = current_parameter

	def rewrite_csv_file(self, directory, sffx, new_results):
		"""
		Reads in the current csv file and adds the new data to it
		"""
		results = {}

		data_file = open('%sdeadlocking_times_%s.csv' % (self.directory, sffx), 'r')
		rdr = reader(data_file)
		for row in rdr:
			results[row[0]] = row[1:]
		data_file.close()
		print "A"
		print results
		for state in new_results:
			if str(state) in results:
				results[str(state)].append(new_results[state])
			else:
				results[str(state)] = [new_results[state]]
		print "B"
		print results
		data_file = open('%sdeadlocking_times_%s.csv' % (self.directory, sffx), 'w')
		wrtr = writer(data_file)
		for state in results:
			row_to_write = [state] + results[state]
			wrtr.writerow(row_to_write)
		data_file.close()
		
def worker(experiment):
	"""
	Actually runs the damn thing
	"""
	while True:
		current_dir_name = experiment.directory + str(experiment.current_parameter) + "/" 
		Q = Simulation(current_dir_name)
		times = Q.simulate_until_deadlock()
		experiment.rewrite_csv_file(current_dir_name, experiment.current_parameter, times)
	


if __name__ == '__main__':
	arguments = docopt.docopt(__doc__)
	dirname = arguments['<dir_name>']
	split_list = arguments['<split_list>']
	experiments = [Experiment(dirname, current_parameter) for current_parameter in split_list]
	pool = Pool()
	stuff = pool.map(worker, experiments)
	