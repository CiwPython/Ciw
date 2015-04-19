"""
Usage: analyse.py <dir_name> [<sffx>]

Arguments
    dir_name    : name of the directory from which to read in parameters and write data files
    suff        : optional suffix to add to the data file name

Options
    -h          : displays this help file
"""
import os
import yaml
from sys import argv
from csv import reader
import docopt

class Data():
	"""
	A class to hold the data
	"""

	def __init__(self, directory_name, sffx=None):
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
            ['50132', '0', '3', '1999.8061066137873', '0.0', '1999.8061066137873', '0.1923943987059666', '1999.9985010124933']
            >>> d.data_per_node[1][0]
            ['50102', '1', '1', '1999.0025591060407', '0.0', '1999.0025591060407', '0.6092886795003283', '1999.6118477855412']
            >>> d.data_per_class[0][0]
            ['50132', '0', '3', '1999.8061066137873', '0.0', '1999.8061066137873', '0.1923943987059666', '1999.9985010124933']
            >>> d.data_per_node_per_class[2][1][0]
            ['50102', '1', '2', '1998.6969428179862', '0.14433402242707416', '1998.8412768404132', '0.1612822656274953', '1999.0025591060407']
		"""
		self.directory = os.path.dirname(os.path.realpath(__file__)) + '/' + directory_name + '/'
		self.sffx = sffx
		self.parameter_file = self.directory + 'parameters.yml'
		self.data_file = self.find_data_file()
		self.parameters = self.load_parameters()
		self.data = self.load_data()
		self.data_per_node = self.find_data_per_node()
		self.data_per_class = self.find_data_per_class()
		self.data_per_node_per_class = self.find_data_per_node_per_class()
		self.summary_statistics = {}

	def find_data_file(self):
		"""
		Finds the data file and directory based on the name given
		"""
		if self.sffx:
			return self.directory + 'data_' + self.sffx + '.csv'
		else:
			return self.directory + 'data.csv'

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
			['50132', '0', '3', '1999.8061066137873', '0.0', '1999.8061066137873', '0.1923943987059666', '1999.9985010124933']
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
			0.05566
			>>> round(d.mean_waits(d.data_per_node[1]), 5)
			0.07253
		"""
		return sum([float(data_point[4]) for data_point in data]) / len(data)

	def mean_visits(self, data):
		"""
		Finds the mean number of visits to each node for a subset of the data
		data here must be for 1 node only

			>>> d = Data('logs_test_for_analyse')
			>>> round(d.mean_visits(d.data_per_node[3]), 5)
			1.46328
			>>> round(d.mean_visits(d.data_per_node_per_class[1][1]), 5)
			2.69957
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
			9.78516
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
			{'Mean_Visits_per_Node': {1: 2.3176760690443254, 2: 1.4333203581159983}, 'Mean_Customers_Overall': 19.62536579897305, 'Mean_Waiting_Times_Overall': 0.055657249979677685, 'Mean_Waiting_Times_per_Node': {1: 0.07252886678329462, 2: 0.06900929721381453}, 'Mean_Waiting_Times_per_Node_per_Class': {1: {0: 0.07296209330440638, 1: 0.07229676234027073}, 2: {0: 0.06776830971106831, 1: 0.07077829841382609}}, 'Mean_Customers_per_Node': {1: 9.785161997806162, 2: 6.673346315685424}, 'Mean_Waiting_Times_per_Class': {1: 0.06011290147533826}}
		"""
		self.summary_statistics['Mean_Waiting_Times_Overall'] = self.mean_waits(self.data)
		self.summary_statistics['Mean_Waiting_Times_per_Node'] = {node:self.mean_waits(self.data_per_node[node]) for node in range(1,self.parameters['Number_of_nodes'])}
		self.summary_statistics['Mean_Waiting_Times_per_Class'] = {cls:self.mean_waits(self.data_per_class[cls]) for cls in range(1,self.parameters['Number_of_classes'])}
		self.summary_statistics['Mean_Waiting_Times_per_Node_per_Class'] = {node: {cls:self.mean_waits(self.data_per_node_per_class[node][cls]) for cls in range(self.parameters['Number_of_classes'])} for node in range(1,self.parameters['Number_of_nodes'])}
		self.summary_statistics['Mean_Visits_per_Node'] = {node:self.mean_visits(self.data_per_node[node]) for node in range(1,self.parameters['Number_of_nodes'])}
		self.summary_statistics['Mean_Customers_per_Node'] = {node:self.mean_customers(self.data_per_node[node]) for node in range(1,self.parameters['Number_of_nodes'])}
		self.summary_statistics['Mean_Customers_Overall'] = self.mean_customers(self.data)

	def write_results_to_file(self):
		"""
		Takes the summary statistics and writes them into a .yml file
		"""
		if sffx:
			results_file = open('%sresults_' %self.directory + self.sffx + '.yml', 'w')
		else:
			results_file = open('%sresults.yml' % self.directory, 'w')
		results_file.write(yaml.dump(self.summary_statistics, default_flow_style=False))
		results_file.close()


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    dirname = arguments['<dir_name>']
    sffx = arguments['<sffx>']
    d = Data(dirname, sffx)
    d.find_summary_statistics()
    d.write_results_to_file()
