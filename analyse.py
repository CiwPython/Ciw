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
			>>> d.data_per_node_per_class[2][1][0]
			['50359', '1', '2', '1999.7443661524796', '0.13308885758260658', '1999.8774550100622', '0.025921384417214175', '1999.9033763944794']
		"""
		self.directory = os.path.dirname(os.path.realpath(__file__)) + '/' + directory_name + '/'
		self.parameter_file = self.directory + 'parameters.yml'
		self.data_file = self.directory + 'data.csv'
		self.parameters = self.load_parameters()
		self.data = self.load_data()
		self.data_per_node = self.find_data_per_node()
		self.data_per_class = self.find_data_per_class()
		self.data_per_node_per_class = self.find_data_per_node_per_class()
		self.summary_statistics = {}

	def load_parameters(self):
		"""
		Loads parameter into a dictionary

			>>> d = Data('logs_test_for_analyse')
			>>> d.parameters['Number_of_nodes']
			3
			>>> d.parameters['Number_of_classes']
			2
		"""
		parameter_file = open(self.parameter_file, 'r')
		parameters = yaml.load(parameter_file)
		parameter_file.close()
		return parameters

	def load_data(self):
		"""
		Loads data into an array

			>>> d = Data('logs_test_for_analyse')
			>>> d.data[0]
			['50359', '1', '2', '1999.7443661524796', '0.13308885758260658', '1999.8774550100622', '0.025921384417214175', '1999.9033763944794']
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

	def find_data_per_node_per_class(self):
		"""
		Finds the data based on node
		"""
		return {node:{cls:[datapoint for datapoint in self.data_per_node[node] if int(datapoint[1]) == cls] for cls in range(self.parameters['Number_of_classes'])} for node in range(1, self.parameters['Number_of_nodes'])}

	def mean_waits(self, data):
		"""
		Finds the mean waits for a subset of this data

			>>> d = Data('logs_test_for_analyse')
			>>> round(d.mean_waits(d.data), 5)
			0.05958
			>>> round(d.mean_waits(d.data_per_node[1]), 5)
			0.08674
		"""
		return sum([float(data_point[4]) for data_point in data]) / len(data)

	def mean_visits(self, data):
		"""
		Finds the mean number of visits to each node for a subset of the data
		data here must be for 1 node only

			>>> d = Data('logs_test_for_analyse')
			>>> round(d.mean_visits(d.data_per_node[3]), 5)
			1.46107
			>>> round(d.mean_visits(d.data_per_node_per_class[1][1]), 5)
			2.6662
		"""
		visits_per_customer = {}
		for data_point in data:
			if data_point[0] in visits_per_customer:
				visits_per_customer[data_point[0]] += 1.0
			else:
				visits_per_customer[data_point[0]] = 1.0
		return sum(visits_per_customer.values()) / len(visits_per_customer)

	def mean_customers(self, data):
		"""
		Finds the mean customers at a node for a subset of the data
		data here must be for 1 node only

			>>> d = Data('logs_test_for_analyse')
			>>> round(d.mean_customers(d.data_per_node[1]), 5)
			10.26873
		"""
		arrivals_and_exits = [[float(datapoint[3]), 'a'] for datapoint in data] + [[float(datapoint[7]), 'd'] for datapoint in data]
		sorted_arrivals_and_exits = sorted(arrivals_and_exits, key=lambda data_point: data_point[0])
		current_number_of_customers = 0
		current_mean_customers = 0
		previous_time = 0
		for data_point in sorted_arrivals_and_exits:
			if data_point[1] == 'a':
				current_number_of_customers += 1
			elif data_point[1] == 'd':
				current_number_of_customers -= 1
			current_mean_customers += current_number_of_customers * (data_point[0] - previous_time)
			previous_time = data_point[0]
		return current_mean_customers / sorted_arrivals_and_exits[-1][0]

	def find_summary_statistics(self):
		"""
		Finds summary statistics for this data

			>>> d = Data('logs_test_for_analyse')
			>>> d.find_summary_statistics()
			>>> d.summary_statistics
			{'Mean_Visits_per_Node': {1: 2.302018238899686, 2: 1.4304280556988138}, 'Mean_Customers_Overall': 19.83493819543286, 'Mean_Waiting_Times_Overall': 0.05957745472321155, 'Mean_Waiting_Times_per_Node': {1: 0.08674002964863309, 2: 0.06159968388285421}, 'Mean_Waiting_Times_per_Node_per_Class': {1: {0: 0.08624344804990342, 1: 0.08700978025811745}, 2: {0: 0.06120378613866512, 1: 0.06216585910776624}}, 'Mean_Customers_per_Node': {1: 10.268726632090543, 2: 6.43425954346275}, 'Mean_Waiting_Times_per_Class': {1: 0.0661709436923146}}
		"""
		self.summary_statistics['Mean_Waiting_Times_Overall'] = self.mean_waits(self.data)
		self.summary_statistics['Mean_Waiting_Times_per_Node'] = {node:self.mean_waits(self.data_per_node[node]) for node in range(1,self.parameters['Number_of_nodes'])}
		self.summary_statistics['Mean_Waiting_Times_per_Class'] = {cls:self.mean_waits(self.data_per_class[cls]) for cls in range(1,self.parameters['Number_of_classes'])}
		self.summary_statistics['Mean_Waiting_Times_per_Node_per_Class'] = {node: {cls:self.mean_waits(self.data_per_node_per_class[node][cls]) for cls in range(self.parameters['Number_of_classes'])} for node in range(1,self.parameters['Number_of_nodes'])}
		self.summary_statistics['Mean_Visits_per_Node'] = {node:self.mean_visits(self.data_per_node[node]) for node in range(1,self.parameters['Number_of_nodes'])}
		self.summary_statistics['Mean_Customers_per_Node'] = {node:self.mean_customers(self.data_per_node[node]) for node in range(1,self.parameters['Number_of_nodes'])}
		self.summary_statistics['Mean_Customers_Overall'] = self.mean_customers(self.data)


d = Data('logs_141210_123602')