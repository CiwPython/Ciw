"""
Script to analyse a data directory
"""
import os
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

			>>> d = Data('logs_test_for_analyse')
			>>> d.directory
			'/Users/geraintianpalmer/Documents/SimulatingAQingNetwork/logs_test_for_analyse/'
			>>> d.parameter_file
			'/Users/geraintianpalmer/Documents/SimulatingAQingNetwork/logs_test_for_analyse/parameters.yml'
			>>> d.data_file
			'/Users/geraintianpalmer/Documents/SimulatingAQingNetwork/logs_test_for_analyse/data.csv'
			>>> d.data[0]
			['50359', '1', '2', '1999.7443661524796', '0.13308885758260658', '1999.8774550100622', '0.025921384417214175', '1999.9033763944794']
			>>> d.data_per_node[1][0]
			['50352', '1', '1', '1999.5118337158333', '0.0', '1999.5118337158333', '0.07836194498760167', '1999.5901956608209']
			>>> d.data_per_class[0][0]
			['50332', '0', '1', '1998.4555520726726', '0.0', '1998.4555520726726', '0.26478695690745796', '1998.7203390295801']
			>>> d.data_per_class_per_node[2][1][0]
			['50359', '1', '2', '1999.7443661524796', '0.13308885758260658', '1999.8774550100622', '0.025921384417214175', '1999.9033763944794']
		"""
		self.directory = os.path.dirname(os.path.realpath(__file__)) + '/' + directory_name + '/'
		self.parameter_file = self.directory + 'parameters.yml'
		self.data_file = self.directory + 'data.csv'
		self.parameters = self.load_parameters()
		self.data = self.load_data()
		self.data_per_node = self.find_data_per_node()
		self.data_per_class = self.find_data_per_class()
		self.data_per_class_per_node = self.find_data_per_class_per_node()

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

	def find_data_per_node(self):
		"""
		Finds the data based on node
		"""
		return {node:[datapoint for datapoint in self.data if int(datapoint[2]) == node] for node in range(1, self.parameters['Number_of_nodes']+1)}

	def find_data_per_class(self):
		"""
		Finds the data based on node
		"""
		return {cls:[datapoint for datapoint in self.data if int(datapoint[1]) == cls] for cls in range(self.parameters['Number_of_classes'])}

	def find_data_per_class_per_node(self):
		"""
		Finds the data based on node
		"""
		return {node:{cls:[datapoint for datapoint in self.data_per_node[node] if int(datapoint[1]) == cls] for cls in range(self.parameters['Number_of_classes'])} for node in range(1, self.parameters['Number_of_nodes'])}


d = Data('logs_141210_123602')