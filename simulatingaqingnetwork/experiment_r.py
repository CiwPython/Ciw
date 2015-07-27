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



def write_deadlock_records_to_file(overall_dict, directory, queue_capacities, sffx):
    """
    Writes the records for times to deadlock to a csv file
    """
    data_file = open('%sdeadlocking_times_%s.csv' % (directory, sffx), 'w')
    csv_wrtr = writer(data_file)
    csv_wrtr.writerow(queue_capacities)
    for state in overall_dict:
        row_to_write = [state] + overall_dict[state]
        csv_wrtr.writerow(row_to_write)
    data_file.close()

def append_times_dictionaies(overall_dict, new_dict):
    """
    Appends the new times to the overall times dictionary

        >>> A = {'t':[9], 'r':[10]}
        >>> B = {'g':3, 't':2}
        >>> append_times_dictionaies(A, B)
        >>> A
        {'r': [10], 't': [9, 2], 'g': [3]}
        >>> B
        {'t': 2, 'g': 3}
    """
    for state in new_dict:
        if state in overall_dict:
            overall_dict[state].append(new_dict[state])
        else:
            overall_dict[state] = [new_dict[state]]



class Experiment:
	"""
	A class to hold the current experiment
	"""
	def __init__(self, dirname):
		"""
		Initialises the experiment

			>>> E = Experiment('datafortesting/logs_test_for_experiment/')
			>>> E.parameters
			{'Arrival_rates': {'Class 0': [24.0, 20.0]}, 'Number_of_nodes': 2, 'Simulation_time': 2500, 'Number_of_servers': [2, 2], 'Queue_capacities': [2, 3], 'Number_of_classes': 1, 'Service_rates': {'Class 0': [['Exponential', 7.0], ['Exponential', 7.0]]}, 'Transition_matrices': {'Class 0': [[0.2, 0.2], [0.2, 0.2]]}}
			>>> E.config
			{'Variable': ['Arrival_rates', 'Class 0', 0], 'Values': [22.0, 24.0], 'Number of Iterations': [5]}
		"""
		self.root = os.getcwd()
		self.directory = os.path.join(self.root, dirname)
		self.parameters = self.load_parameters()
		self.config = self.load_config()

	def load_config(self):
		"""
		Loads the config file into the experiment
    	"""
		config_file_name = self.directory + 'config.yml'
		config_file = open(config_file_name, 'r')
		config = yaml.load(config_file)
		config_file.close()
		return config

	def write_parameters_file(self):
		"""
		Writes the new parameters file
		"""
		parameters_file = open('%sparameters.yml' % self.directory, 'w')
		parameters_file.write(yaml.dump(self.parameters, default_flow_style=False))
		parameters_file.close()

	def load_parameters(self):
		"""
		Loads the parameters into the model
		"""
		parameter_file_name = self.directory + 'parameters.yml'
		parameter_file = open(parameter_file_name, 'r')
		parameters = yaml.load(parameter_file)
		parameter_file.close()

		return parameters

	def update_parameters(self, new_parameter):
		"""
		Updates the parameters to write to file

			>>> E = Experiment('datafortesting/logs_test_for_experiment_r/')
			>>> E.parameters
			{'Arrival_rates': {'Class 0': [22.0, 20.0]}, 'Number_of_nodes': 2, 'Simulation_time': 2500, 'Number_of_servers': [2, 2], 'Queue_capacities': [2, 3], 'Number_of_classes': 1, 'Service_rates': {'Class 0': [['Exponential', 7.0], ['Exponential', 7.0]]}, 'Transition_matrices': {'Class 0': [[0.2, 0.2], [0.2, 0.2]]}}
			>>> E.update_parameters(0.9)
			>>> E.parameters
			{'Arrival_rates': {'Class 0': [22.0, 20.0]}, 'Number_of_nodes': 2, 'Simulation_time': 2500, 'Number_of_servers': [2, 2], 'Queue_capacities': [2, 3], 'Number_of_classes': 1, 'Service_rates': {'Class 0': [['Exponential', 7.0], ['Exponential', 7.0]]}, 'Transition_matrices': {'Class 0': [[0.2, 0.9], [0.2, 0.2]]}}
		"""
		A = [self.parameters[self.config['Variable'][0]][self.config['Variable'][1]][self.config['Variable'][2]]]
		A[0][self.config['Variable'][3]] = new_parameter

	def run_experiment(self):
		"""
		# Runs the experiment

			>>> seed(51)
			>>> E = Experiment('datafortesting/logs_test_for_experiment/')
			>>> E.run_experiment()
			>>> E.all_times[((0, 0), (0, 0))]
			[1.7575488630183014, 0.5764103544711466, 0.8629459649046253, 1.6632958105934947, 1.4026410332480492]
		"""
		for new_parameter in self.config['Values']:
			self.all_times = {}
			times = {}
			self.update_parameters(new_parameter)
			self.write_parameters_file()
			for itr in range(self.config['Number of Iterations'][0]):
				self.simulation = Simulation(self.directory)
				times = self.simulation.simulate_until_deadlock()
				append_times_dictionaies(self.all_times, times)
			write_deadlock_records_to_file(self.all_times, self.directory, self.simulation.queue_capacities, new_parameter)


if __name__ == '__main__':
	arguments = docopt.docopt(__doc__)
	dirname = arguments['<dir_name>']
	E = Experiment(dirname)
	E.run_experiment()