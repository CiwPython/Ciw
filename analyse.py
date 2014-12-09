"""
Script to analyse a data directory
"""
import yaml
from sys import argv
from csv import reader

directory_name = 'logs_141209_134914'

class Data():
	"""
	A class to hold the data
	"""

	def __init__(self, directory_name):
		"""
		Initialises the data
		"""
		self.directory = argv[0][:-10] + directory_name + '/'
		self.parameter_file = self.directory + 'parameters.yml'
		self.data_file = self.directory + 'data.csv'
		self.parameters = self.load_parameters()
		self.data = self.load_data()

	def load_parameters(self):
		"""
		Loads parameter into a dictionary
		"""
		parameter_file = open(self.parameter_file, 'r')
		parameters = yaml.load(parameter_file)
		parameter_file.close()
		return parameters

	def load_data(self):
		"""
		Loads data into an array
		"""
		data_array = []
		data_file = open(self.data_file, 'r')
		rdr = reader(data_file)
		for row in rdr:
			data_array.append(row)
		data_file.close()
		return data_array


d = Data('logs_141209_134914')