"""
Usage: simulation.py <dir_name>

Arguments
    dir_name    : name of the directory from which to read in parameters and write data files

Options
    -h          : displays this help file
"""

from __future__ import division
import numpy as np
import scipy.misc
import yaml
import docopt
import os


# Defining some functions that will be used later on
def FindP0s(ro, c):
    	return (sum( ((c*ro)**n)/(scipy.misc.factorial(n)) for n in range(c)) + (((c*ro)**c)/scipy.misc.factorial(c))*(1/(1-ro)))**(-1)

def FindL(c, l, m, p):
    	return (((((l / m) ** c) * l * m)/(scipy.misc.factorial(c - 1)*((c * m) - l) ** 2)) * p) + (l / m)





class JacksonNetwork:
    """
    A class to hold information about the jackson network
    """

    def __init__(self, directory_name):
        """
        Initialises the network parameters

            >>> J = JacksonNetwork('logs_test_for_jackson_networks')
            >>> J.number_of_classes
            3
            >>> J.number_of_nodes
            4
            >>> print J.external_arrival_rates
            [[ 2.   1.   2.   0.5]
             [ 2.   3.   6.   4. ]
             [ 3.   7.   4.   1. ]]
            >>> print J.service_distributions
            [[['Exponential' '13.0']
              ['Exponential' '6.0']
              ['Exponential' '8.0']
              ['Exponential' '9.0']]
            <BLANKLINE>
             [['Exponential' '7.0']
              ['Exponential' '10.0']
              ['Exponential' '8.0']
              ['Exponential' '5.0']]
            <BLANKLINE>
             [['Exponential' '7.0']
              ['Exponential' '7.0']
              ['Exponential' '9.0']
              ['Exponential' '0.5']]]
            >>> print J.number_of_servers
            [ 9 10  8  8]
            >>> print J.routing_matrix
            [[[ 0.   0.   0.4  0.3]
              [ 0.1  0.1  0.1  0.1]
              [ 0.1  0.3  0.2  0.2]
              [ 0.   0.   0.   0.3]]
            <BLANKLINE>
             [[ 0.6  0.   0.   0.2]
              [ 0.1  0.1  0.2  0.2]
              [ 0.9  0.   0.   0. ]
              [ 0.2  0.1  0.1  0.1]]
            <BLANKLINE>
             [[ 0.1  0.2  0.1  0.4]
              [ 0.2  0.2  0.   0.1]
              [ 0.   0.8  0.1  0.1]
              [ 0.4  0.1  0.1  0. ]]]
            >>> print J.service_rates
            [[ 13.    6.    8.    9. ]
             [  7.   10.    8.    5. ]
             [  7.    7.    9.    0.5]]
            >>> print J.service_times
            [[ 0.07692308  0.16666667  0.125       0.11111111]
             [ 0.14285714  0.1         0.125       0.2       ]
             [ 0.14285714  0.14285714  0.11111111  2.        ]]
        """
        self.directory = os.path.dirname(os.path.realpath(__file__)) + '/' + directory_name + '/'
        self.parameters = self.load_parameters()
        self.number_of_classes = self.parameters['Number_of_classes']
        self.number_of_nodes = self.parameters['Number_of_nodes']
        self.external_arrival_rates = np.matrix([self.parameters['Arrival_rates'][cls] for cls in self.parameters['Arrival_rates']])
        self.service_distributions = np.array([self.parameters['Service_rates'][cls] for cls in self.parameters['Service_rates']])
        self.number_of_servers = np.array(self.parameters['Number_of_servers'])
        self.routing_matrix = np.array([self.parameters['Transition_matrices'][cls] for cls in self.parameters['Transition_matrices']])
        self.service_rates, self.service_times = self.find_service_rates_and_times()

    def load_parameters(self):
        """
        Loads in the parameters of the network from a yaml file
        """
        parameter_file_name = self.directory + 'parameters.yml'
        parameter_file = open(parameter_file_name, 'r')
        parameters = yaml.load(parameter_file)
        parameter_file.close()
        return parameters

    def find_service_rates_and_times(self):
        """
        Finds the rates and expected service times for each node each class

            >>> J = JacksonNetwork('logs_test_for_jackson_networks')
            >>> J.find_service_rates_and_times()
            (array([[ 13. ,   6. ,   8. ,   9. ],
                   [  7. ,  10. ,   8. ,   5. ],
                   [  7. ,   7. ,   9. ,   0.5]]), array([[ 0.07692308,  0.16666667,  0.125     ,  0.11111111],
                   [ 0.14285714,  0.1       ,  0.125     ,  0.2       ],
                   [ 0.14285714,  0.14285714,  0.11111111,  2.        ]]))
        """
        service_rates = np.array([[float(self.service_distributions[cls][nd][1]) for nd in range(self.number_of_nodes)] for cls in range(self.number_of_classes)])
        service_times = np.divide(1, service_rates)
        return service_rates, service_times

    def solve_traffic_equations(self):
        """
        Solves the traffic equations

            >>> J = JacksonNetwork('logs_test_for_jackson_networks')
            >>> J.solve_traffic_equations()
            >>> print J.lmbdas
            [[  2.6635514    2.49221184   4.14330218   3.39563863]
             [ 30.7203718    4.70178156   8.17195972  12.31603408]
             [ 11.15001159  19.11662416   6.57546951   8.029214  ]]
        """
        lmbdas = np.empty((self.number_of_classes, self.number_of_nodes))
        for cls in range(self.number_of_classes):
            A = self.routing_matrix[cls].transpose() - np.identity(self.number_of_nodes)
            B = -self.external_arrival_rates[cls]
            l = B * np.linalg.inv(A).transpose()
            lmbdas[cls] = np.squeeze(np.asarray(l))
        self.lmbdas = lmbdas

    def aggregate_over_classes(self):
        """
        Aggregates the arrivals, routing matrix and service rates and times over the classes

            >>> J = JacksonNetwork('logs_test_for_jackson_networks')
            >>> J.solve_traffic_equations()
            >>> J.aggregate_over_classes()
            >>> print J.aggregate_lmbdas
            [ 44.5339348   26.31061756  18.89073141  23.74088672]
            >>> print J.aggregate_service_times
            [ 0.13891366  0.13745375  0.12016557  0.7960498 ]
            >>> print J.aggregate_service_rates
            [ 7.19871605  7.27517426  8.32185143  1.25620282]
            >>> print J.aggregate_external_arrival_rates
            [[  7.   11.   12.    5.5]]
            >>> print J.aggregate_routing_matrix
            [[ 0.43892875  0.05007423  0.0489609   0.25605517]
             [ 0.17265745  0.17265745  0.04521283  0.11787028]
             [ 0.41126486  0.34426228  0.07867389  0.07867389]
             [ 0.23903456  0.08569709  0.08569709  0.09478563]]
        """
        self.aggregate_lmbdas = sum(self.lmbdas)
        self.aggregate_service_times = sum(np.multiply(np.divide(self.lmbdas, self.aggregate_lmbdas), self.service_times))
        self.aggregate_service_rates = np.divide(1, self.aggregate_service_times)
        self.aggregate_external_arrival_rates = sum(self.external_arrival_rates)
        self.aggregate_routing_matrix = self.find_aggregate_routing_matrix(self.aggregate_lmbdas)

    def find_aggregate_routing_matrix(self, Agg_lmbdas):
        """
        Aggregates the routing matrix over the classes

            >>> J = JacksonNetwork('logs_test_for_jackson_networks')
            >>> J.solve_traffic_equations()
            >>> J.aggregate_over_classes()
            >>> J.find_aggregate_routing_matrix(J.aggregate_lmbdas)
            array([[ 0.43892875,  0.05007423,  0.0489609 ,  0.25605517],
                   [ 0.17265745,  0.17265745,  0.04521283,  0.11787028],
                   [ 0.41126486,  0.34426228,  0.07867389,  0.07867389],
                   [ 0.23903456,  0.08569709,  0.08569709,  0.09478563]])
        """
        agg_rout_matrx = []
        for i in range(self.number_of_nodes):
            agg_rout_matrx.append([])
            for j in range(self.number_of_nodes):
                agg_rout_matrx[i].append(0)
                for k in range(self.number_of_classes):
                    agg_rout_matrx[i][j] += (self.routing_matrix[k][i][j] * self.lmbdas[k][i])
                agg_rout_matrx[i][j] = agg_rout_matrx[i][j] / Agg_lmbdas[i]
        return np.array(agg_rout_matrx)

    def find_ros(self):
        """
        Finds the trafic intensities of each node
        """
        self.ros = np.divide(self.aggregate_lmbdas, (self.aggregate_service_rates*self.number_of_servers))

    def find_p0s(self):
        """
        Finds the probabilities of having empty nodes
        """
        self.p0s = np.array([FindP0s(self.ros[i], self.number_of_servers[i]) for i in range(self.number_of_nodes)])

    def find_Ls(self):
        """
        Finds the expected number of people at each node
        """
        self.Ls = np.array([FindL(self.number_of_servers[i], self.aggregate_lmbdas[i], self.aggregate_service_rates[i], self.p0s[i]) for i in range(self.number_of_nodes)])

    def find_Ws(self):
        """
        Finds the expected time spent at each node
        """
        self.Ws = np.divide(self.Ls, self.aggregate_lmbdas)

    def find_Lqs(self):
        """
        Finds the expected number of people waiting in the queue at each node
        """
        self.Lqs = self.Ls - self.ros

    def find_Wqs(self):
        """
        Finds the expected time waiting in the queue at each node
        """
        self.Wqs = np.divide(self.Ls - np.divide(self.aggregate_lmbdas, self.aggregate_service_rates), self.aggregate_lmbdas)

    def find_overall_external_arrival_rate(self):
        """
        Finds the overall external arrival rate of the network
        """
        self.overall_external_arrival_rate = np.sum(self.aggregate_external_arrival_rates)

    def find_L(self):
        """
        Finds the expected number of customers in the system
        """
        self.L = sum(self.Ls)

    def find_W(self):
        """
        Finds the expected time spent in the system
        """
        self.W = self.L / self.overall_external_arrival_rate

    def solve(self):
        """
        Solves the Jackson network and outputs performance measures
        """
        self.solve_traffic_equations()
        self.aggregate_over_classes()
        self.find_ros()
        self.find_p0s()
        self.find_Ls()
        self.find_Ws()
        self.find_Lqs()
        self.find_Wqs()
        self.find_overall_external_arrival_rate()
        self.find_L()
        self.find_W()
        print '##############################'
        print 'PERFORMANCE MEASURES OF THE JACKSON NETWORK'
        print '\n'
        print 'Expected number of customers at each node:'
        print self.Ls
        print 'Expected number of customers in each queue:'
        print self.Lqs
        print 'Expected number of customers in the network:'
        print self.L
        print '\n'
        print 'Expected time spent at each node:'
        print self.Ws
        print 'Expected time spent queueing at each node:'
        print self.Wqs
        print 'Expected amount of time spent in the network:'
        print self.W
        print '\n'
        print 'Traffic intensities at each node:'
        print self.p0s
        print '##############################'










if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    dirname = arguments['<dir_name>']
    J = JacksonNetwork(dirname)
    J.solve()
