import unittest
import ciw
from hypothesis import given
from hypothesis.strategies import floats, integers, lists, random_module


class TestServiceCentre(unittest.TestCase):

    def test_init_method(self):
        number_of_servers = 2
        queueing_capacity = 'Inf'
        class_change_matrix = [[0.2, 0.8],
                               [1.0, 0.0]]
        schedule = None
        SC = ciw.ServiceCentre(number_of_servers, queueing_capacity, class_change_matrix, schedule)
        self.assertEqual(SC.number_of_servers, number_of_servers)
        self.assertEqual(SC.queueing_capacity, queueing_capacity)
        self.assertEqual(SC.class_change_matrix, class_change_matrix)
        self.assertEqual(SC.schedule, schedule)

    @given(number_of_servers=integers(min_value=1),
           queueing_capacity=integers(min_value=0),
           class_change_prob1=floats(min_value=0.0, max_value=1.0),
           class_change_prob2=floats(min_value=0.0, max_value=1.0))
    def test_init_method_h(self, number_of_servers, queueing_capacity, class_change_prob1, class_change_prob2):
        class_change_matrix = [[class_change_prob1,
                                1 - class_change_prob1],
                               [class_change_prob2,
                                1 - class_change_prob2]]
        schedule = None
        SC = ciw.ServiceCentre(number_of_servers, queueing_capacity, class_change_matrix, schedule)
        self.assertEqual(SC.number_of_servers, number_of_servers)
        self.assertEqual(SC.queueing_capacity, queueing_capacity)
        self.assertEqual(SC.class_change_matrix, class_change_matrix)
        self.assertEqual(SC.schedule, schedule)


class TestCustomerClass(unittest.TestCase):

    def test_init_method(self):
        arrival_distributions = [["Uniform", 4.0, 9.0],
                                 ["Exponential", 5],
                                 ["Gamma", 0.6, 1.2]]
        service_distributions = [["Gamma", 4.0, 9.0],
                                 ["Uniform", 0.6, 1.2],
                                 ["Exponential", 5]]
        transition_matrix = [[.2, .6, .2], [0, 0, 0], [.5, 0, 0]]

        CC = ciw.CustomerClass(arrival_distributions, service_distributions, transition_matrix)
        self.assertEqual(CC.arrival_distributions, arrival_distributions)
        self.assertEqual(CC.service_distributions, service_distributions)
        self.assertEqual(CC.transition_matrix, transition_matrix)



class TestNetwork(unittest.TestCase):

    def test_init_method(self):
        number_of_servers = 2
        queueing_capacity = 'Inf'
        schedule = None
        class_change_matrix = [[0.2, 0.8],
                               [1.0, 0.0]]
        arrival_distributions = [["Uniform", 4.0, 9.0],
                                 ["Exponential", 5.0],
                                 ["Gamma", 0.6, 1.2]]
        service_distributions = [["Gamma", 4.0, 9.0],
                                 ["Uniform", 0.6, 1.2],
                                 ["Exponential", 5]]
        transition_matrix = [[0.2, 0.6, 0.2],
                             [0.0, 0.0, 0.0],
                             [0.5, 0.0, 0.0]]
        service_centres = [ciw.ServiceCentre(number_of_servers, queueing_capacity, class_change_matrix, schedule) for i in xrange(4)]
        customer_classes = [ciw.CustomerClass(arrival_distributions, service_distributions, transition_matrix) for i in xrange(2)]
        N = ciw.Network(service_centres, customer_classes)
        self.assertEqual(N.service_centres, service_centres)
        self.assertEqual(N.customer_classes, customer_classes)
        self.assertEqual(N.number_of_service_centres, 4)
        self.assertEqual(N.number_of_customer_classes, 2)


    def test_network_from_dictionary(self):
        params = {'Arrival_distributions': {'Class 0': [['Exponential', 3.0]]},
                  'Service_distributions': {'Class 0': [['Exponential', 7.0]]},
                  'Number_of_servers': [9],
                  'Number_of_classes': 1,
                  'Transition_matrices': {'Class 0': [[0.5]]},
                  'Number_of_nodes': 1,
                  'Queue_capacities': ['Inf']}
        N = ciw.Network_From_Dictionary(params)
        
        self.assertEqual(N.number_of_service_centres, 1)
        self.assertEqual(N.number_of_customer_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, 'Inf')
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertEqual(N.customer_classes[0].arrival_distributions, [['Exponential', 3.0]])
        self.assertEqual(N.customer_classes[0].service_distributions, [['Exponential', 7.0]])
        self.assertEqual(N.customer_classes[0].transition_matrix, [[0.5]])


        params = {'Arrival_distributions': [['Exponential', 3.0],
                                            ['Uniform', 0.2, 0.6]],
                  'Service_distributions': [['Exponential', 7.0],
                                            ['Deterministic', 0.7]],
                  'Number_of_servers': ['my_amazing_schedule', 3],
                  'Transition_matrices': [[0.5, 0.2],
                                          [0.0, 0.0]],
                  'Queue_capacities': [10, 'Inf'],
                  'my_amazing_schedule': [[20, 1],
                                          [50, 4]]}
        N = ciw.Network_From_Dictionary(params)
        self.assertEqual(N.number_of_service_centres, 2)
        self.assertEqual(N.number_of_customer_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, 10)
        self.assertEqual(N.service_centres[0].number_of_servers, 'schedule')
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].schedule, [[20, 1], [50, 4]])
        self.assertEqual(N.service_centres[1].queueing_capacity, 'Inf')
        self.assertEqual(N.service_centres[1].number_of_servers, 3)
        self.assertEqual(N.service_centres[1].class_change_matrix, None)
        self.assertEqual(N.service_centres[1].schedule, None)
        self.assertEqual(N.customer_classes[0].arrival_distributions, [['Exponential', 3.0], ['Uniform', 0.2, 0.6]])
        self.assertEqual(N.customer_classes[0].service_distributions, [['Exponential', 7.0], ['Deterministic', 0.7]])
        self.assertEqual(N.customer_classes[0].transition_matrix, [[0.5, 0.2], [0.0, 0.0]])


        params = {'Arrival_distributions': {'Class 0': [['Exponential', 3.0]],
                                            'Class 1': [['Exponential', 4.0]]},
                  'Service_distributions': {'Class 0': [['Exponential', 7.0]],
                                            'Class 1': [['Uniform', 0.4, 1.2]]},
                  'Number_of_servers': [9],
                  'Transition_matrices': {'Class 0': [[0.5]],
                                          'Class 1': [[0.0]]},
                  'Number_of_nodes': 1,
                  'Queue_capacities': ['Inf'],
                  'Class_change_matrices': {'Node 1': [[0.0, 1.0],
                                                       [0.2, 0.8]]}}
        N = ciw.Network_From_Dictionary(params)
        self.assertEqual(N.number_of_service_centres, 1)
        self.assertEqual(N.number_of_customer_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, 'Inf')
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].class_change_matrix, [[0.0, 1.0], [0.2, 0.8]])
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertEqual(N.customer_classes[0].arrival_distributions, [['Exponential', 3.0]])
        self.assertEqual(N.customer_classes[0].service_distributions, [['Exponential', 7.0]])
        self.assertEqual(N.customer_classes[0].transition_matrix, [[0.5]])
        self.assertEqual(N.customer_classes[1].arrival_distributions, [['Exponential', 4.0]])
        self.assertEqual(N.customer_classes[1].service_distributions, [['Uniform', 0.4, 1.2]])
        self.assertEqual(N.customer_classes[1].transition_matrix, [[0.0]])


    def test_network_from_file(self):
        N = ciw.Network_From_File(
          'ciw/tests/testing_parameters/params.yml')
        self.assertEqual(N.number_of_service_centres, 4)
        self.assertEqual(N.number_of_customer_classes, 3)
        self.assertEqual(N.service_centres[0].queueing_capacity, 20)
        self.assertEqual(N.service_centres[1].queueing_capacity, 'Inf')
        self.assertEqual(N.service_centres[2].queueing_capacity, 30)
        self.assertEqual(N.service_centres[3].queueing_capacity, 'Inf')
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[1].number_of_servers, 10)
        self.assertEqual(N.service_centres[2].number_of_servers, 8)
        self.assertEqual(N.service_centres[3].number_of_servers, 8)
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[1].class_change_matrix, None)
        self.assertEqual(N.service_centres[2].class_change_matrix, None)
        self.assertEqual(N.service_centres[3].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertEqual(N.service_centres[1].schedule, None)
        self.assertEqual(N.service_centres[2].schedule, None)
        self.assertEqual(N.service_centres[3].schedule, None)
        self.assertEqual(N.customer_classes[0].arrival_distributions, [['Exponential', 3.0], ['Exponential', 7.0], ['Exponential', 4.0], ['Exponential', 1.0]])
        self.assertEqual(N.customer_classes[1].arrival_distributions, [['Exponential', 2.0], ['Exponential', 3.0], ['Exponential', 6.0], ['Exponential', 4.0]])
        self.assertEqual(N.customer_classes[2].arrival_distributions, [['Exponential', 2.0], ['Exponential', 1.0], ['Exponential', 2.0], ['Exponential', 0.5]])
        self.assertEqual(N.customer_classes[0].service_distributions, [['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]])
        self.assertEqual(N.customer_classes[1].service_distributions, [['Exponential', 7.0], ['Triangular', 0.1, 0.85, 0.8], ['Exponential', 8.0], ['Exponential', 5.0]])
        self.assertEqual(N.customer_classes[2].service_distributions, [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]])
        self.assertEqual(N.customer_classes[0].transition_matrix, [[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]])
        self.assertEqual(N.customer_classes[1].transition_matrix, [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]])
        self.assertEqual(N.customer_classes[2].transition_matrix, [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]])