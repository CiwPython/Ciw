"""
Usage: analyse.py <dir_name> [<sffx>]

Arguments
    dir_name    : name of the directory from which to read in parameters and write data files
    sffx        : optional suffix to add to the data file name

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

            >>> d = Data('results/logs_test_times_to_deadlock/')
            >>> d.directory
            '/Users/geraintianpalmer/Documents/SimulatingAQingNetwork/results/logs_test_times_to_deadlock/'
            >>> d.data_file
            '/Users/geraintianpalmer/Documents/SimulatingAQingNetwork/results/logs_test_times_to_deadlock/deadlocking_times.csv'
            >>> d.data[0]
            ['((5, 0), (2, 0))', '8.22292138352217', '8.276088385537253', '8.475569545729414', '8.681127434273733', '8.814243619633118', '8.971751313503805', '9.232122869186604', '9.613341007129984', '9.724487434948657', '9.827588918926097', '10.012274813713304', '10.038362534652094', '10.108609089003915', '10.290249645095255', '10.45692358673942', '10.583150944986368', '10.735682287868183', '10.83403647187431', '11.126447300394188', '11.458049464290378', '11.58427260280143', '11.627924134634931', '11.804506212824162', '11.913300030137576', '12.1584638812559', '12.285305269705441', '12.472930861945528', '12.538347248895423', '12.609670868829099', '12.668571408532594', '12.771561555866802', '12.82748505887785', '12.840182231528269', '13.095569845924624', '13.392730113562791', '13.53130515277018', '13.83060032568363', '13.878859172546859', '14.022711222450699', '14.201309253727063', '14.677034348258468', '14.928299475827902', '15.102744738329411', '15.350418321743925', '15.784347887973043', '16.035165809421873', '16.193705339341268', '16.528065775081767', '17.063979771946947', '17.660865007820902']
        """
        self.root = os.getcwd()
        self.directory = os.path.join(self.root, directory_name)
        self.sffx = sffx
        self.data_file = self.find_data_file()
        self.n1, self.n2, self.data = self.load_data()

    def find_data_file(self):
		"""
		Finds the data file and directory based on the name given
		"""
		if self.sffx:
			return self.directory + 'deadlocking_times_' + self.sffx + '.csv'
		else:
			return self.directory + 'deadlocking_times.csv'

    def load_data(self):
		"""
		Loads data into an array

			>>> d = Data('results/logs_test_times_to_deadlock/')
            >>> d.load_data()[0]
            ['((5, 0), (2, 0))', '8.22292138352217', '8.276088385537253', '8.475569545729414', '8.681127434273733', '8.814243619633118', '8.971751313503805', '9.232122869186604', '9.613341007129984', '9.724487434948657', '9.827588918926097', '10.012274813713304', '10.038362534652094', '10.108609089003915', '10.290249645095255', '10.45692358673942', '10.583150944986368', '10.735682287868183', '10.83403647187431', '11.126447300394188', '11.458049464290378', '11.58427260280143', '11.627924134634931', '11.804506212824162', '11.913300030137576', '12.1584638812559', '12.285305269705441', '12.472930861945528', '12.538347248895423', '12.609670868829099', '12.668571408532594', '12.771561555866802', '12.82748505887785', '12.840182231528269', '13.095569845924624', '13.392730113562791', '13.53130515277018', '13.83060032568363', '13.878859172546859', '14.022711222450699', '14.201309253727063', '14.677034348258468', '14.928299475827902', '15.102744738329411', '15.350418321743925', '15.784347887973043', '16.035165809421873', '16.193705339341268', '16.528065775081767', '17.063979771946947', '17.660865007820902']
        """
		data_array = []
		data_file = open(self.data_file, 'r')
		rdr = reader(data_file)
		for row in rdr:
			data_array.append(row)
		data_file.close()
		return int(data_array[0][0]), int(data_array[0][1]), data_array[1:]

    def prune_deadlocked_state_for_2node_problem(self):
        """
        Gets rid of the deadlocked state as it has the same state as another state
        """
        d_state = ((self.n1, 1), (self.n2, 1))
        for i in range(len(self.data)):
            if self.data[i][0] == str(d_state):
                index_to_remove = i
                break
        self.data.pop(index_to_remove)


    def find_states_for_2_nodes_problem(self, string):
        """
        Finds the states for the 2 node markov chain problem
        For this setup, the state is simply (i, j) where i is the number waiting
        and in service at the first node + the number blocked at the second node,
        and vice versa

            >>> d = Data('results/logs_test_times_to_deadlock/')
            >>> d.find_states_for_2_nodes_problem('((0, 1), (4, 2))')
            '(2, 5)'
        """
        state = eval(string)
        return str((state[0][0] + state[1][1], state[1][0] + state[0][1]))

    def find_mean_times_to_deadlock(self):
        """
        Writes a dictionary for the mean times to deadlock from each state

            >>> d = Data('results/logs_test_times_to_deadlock/')
            >>> d.find_mean_times_to_deadlock()
            {'(3, 0)': 12.850014064641366, '(6, 2)': 11.143603486569647, '(3, 4)': 8.577760672608571, '(1, 1)': 10.586586423681727, '(2, 1)': 12.569174322357249, '(3, 2)': 12.32883652898345, '(1, 3)': 5.340943506373019, '(2, 3)': 12.381377295313882, '(6, 0)': 9.855897631787759, '(4, 2)': 12.316895967930328, '(4, 0)': 11.722594116177723, '(2, 4)': 11.449543765014896, '(5, 1)': 9.917879044054223, '(0, 3)': 5.32952057089355, '(4, 4)': 4.000835346881616, '(5, 3)': 3.9943438360629218, '(3, 1)': 11.828263451060188, '(1, 0)': 12.96200812646115, '(1, 2)': 10.608334313505429, '(2, 0)': 12.920841722474849, '(6, 1)': 11.255664562073346, '(3, 3)': 11.951397336802293, '(2, 2)': 12.491996167799131, '(0, 0)': 13.08376157446719, '(4, 1)': 11.663588742611367, '(5, 0)': 7.811433454989292, '(5, 2)': 12.217265219585093, '(4, 3)': 12.038253153899632}
        """
        return {self.find_states_for_2_nodes_problem(row[0]):sum([float(obs) for obs in row[1:]])/len(row[1:]) for row in self.data}

    def write_results_to_file(self):
		"""
		Takes the summary statistics and writes them into a .yml file
		"""
		if sffx:
			results_file = open('%sdeadlock_results_' %self.directory + self.sffx + '.yml', 'w')
		else:
			results_file = open('%sdeadlock_results.yml' % self.directory, 'w')
		results_file.write(yaml.dump(self.find_mean_times_to_deadlock(), default_flow_style=False))
		results_file.close()


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    dirname = arguments['<dir_name>']
    sffx = arguments['<sffx>']
    d = Data(dirname, sffx)
    d.prune_deadlocked_state_for_2node_problem()
    d.write_results_to_file()
