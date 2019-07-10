import unittest
import ciw
import copy
import random
from hypothesis import given
from hypothesis.strategies import floats, integers, lists, random_module

def example_baulking_function(n):
    if n < 5:
        return 0.0
    return 1.0

class TestServiceCentre(unittest.TestCase):
    def test_init_method(self):
        number_of_servers = 2
        queueing_capacity = float('inf')
        class_change_matrix = [[0.2, 0.8],
                               [1.0, 0.0]]
        schedule = None
        SC = ciw.ServiceCentre(number_of_servers, queueing_capacity, class_change_matrix, schedule)
        self.assertEqual(SC.number_of_servers, number_of_servers)
        self.assertEqual(SC.queueing_capacity, queueing_capacity)
        self.assertEqual(SC.class_change_matrix, class_change_matrix)
        self.assertEqual(SC.schedule, schedule)
        self.assertFalse(SC.preempt)

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
        self.assertFalse(SC.preempt)


class TestCustomerClass(unittest.TestCase):
    def test_init_method(self):
        arrival_distributions = [ciw.dists.Uniform(4.0, 9.0),
                                 ciw.dists.Exponential(5),
                                 ciw.dists.Gamma(0.6, 1.2)]
        service_distributions = [ciw.dists.Gamma(4.0, 9.0),
                                 ciw.dists.Uniform(0.6, 1.2),
                                 ciw.dists.Exponential(5)]
        routing = [[.2, .6, .2], [0, 0, 0], [.5, 0, 0]]
        priority_class = 2
        baulking_functions = [None, None, example_baulking_function]
        batching_distributions = [ciw.dists.Deterministic(1),
                                  ciw.dists.Deterministic(1),
                                  ciw.dists.Deterministic(1)]

        CC = ciw.CustomerClass(arrival_distributions, service_distributions, routing, priority_class, baulking_functions, batching_distributions)
        self.assertEqual(CC.arrival_distributions, arrival_distributions)
        self.assertEqual(CC.service_distributions, service_distributions)
        self.assertEqual(CC.batching_distributions, batching_distributions)
        self.assertEqual(CC.routing, routing)
        self.assertEqual(CC.priority_class, priority_class)

        # check baulking function works
        self.assertEqual(CC.baulking_functions[2](0), 0.0)
        self.assertEqual(CC.baulking_functions[2](1), 0.0)
        self.assertEqual(CC.baulking_functions[2](2), 0.0)
        self.assertEqual(CC.baulking_functions[2](3), 0.0)
        self.assertEqual(CC.baulking_functions[2](4), 0.0)
        self.assertEqual(CC.baulking_functions[2](5), 1.0)
        self.assertEqual(CC.baulking_functions[2](6), 1.0)
        self.assertEqual(CC.baulking_functions[2](7), 1.0)
        self.assertEqual(CC.baulking_functions[2](8), 1.0)


class TestNetwork(unittest.TestCase):
    def test_init_method(self):
        number_of_servers = 2
        queueing_capacity = float('inf')
        schedule = None
        class_change_matrix = [[0.2, 0.8],
                               [1.0, 0.0]]
        arrival_distributions = [ciw.dists.Uniform(4.0, 9.0),
                                 ciw.dists.Exponential(5.0),
                                 ciw.dists.Gamma(0.6, 1.2)]
        service_distributions = [ciw.dists.Gamma(4.0, 9.0),
                                 ciw.dists.Uniform(0.6, 1.2),
                                 ciw.dists.Exponential(5)]
        routing = [[0.2, 0.6, 0.2],
                             [0.0, 0.0, 0.0],
                             [0.5, 0.0, 0.0]]
        priority_class = 0
        batching_distributions = [ciw.dists.Deterministic(1),
                                  ciw.dists.Deterministic(1),
                                  ciw.dists.Deterministic(1)]
        baulking_functions = [None, None, example_baulking_function]
        service_centres = [ciw.ServiceCentre(number_of_servers,
                                             queueing_capacity,
                                             class_change_matrix,
                                             schedule) for i in range(4)]
        customer_classes = [ciw.CustomerClass(arrival_distributions,
                                              service_distributions,
                                              routing,
                                              priority_class,
                                              baulking_functions,
                                              batching_distributions) for i in range(2)]
        N = ciw.Network(service_centres, customer_classes)
        self.assertEqual(N.service_centres, service_centres)
        self.assertEqual(N.customer_classes, customer_classes)
        self.assertEqual(N.number_of_nodes, 4)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {0:0, 1:0})


    def test_create_network_from_dictionary(self):
        params = {'arrival_distributions': {'Class 0': [ciw.dists.Exponential(3.0)]},
                  'service_distributions': {'Class 0': [ciw.dists.Exponential(7.0)]},
                  'number_of_servers': [9],
                  'routing': {'Class 0': [[0.5]]},
                  'queue_capacities': [float('inf')]}
        N = ciw.create_network_from_dictionary(params)
        
        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5]])
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {0:0})


        params = {'arrival_distributions': [ciw.dists.Exponential(3.0),
                                            ciw.dists.Uniform(0.2, 0.6)],
                  'service_distributions': [ciw.dists.Exponential(7.0),
                                            ciw.dists.Deterministic(0.7)],
                  'number_of_servers': [[[1, 20], [4, 50]], 3],
                  'routing': [[0.5, 0.2],
                              [0.0, 0.0]],
                  'queue_capacities': [10, float('inf')]
                  }
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 2)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, 10)
        self.assertEqual(N.service_centres[0].number_of_servers, 'schedule')
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].schedule, [[1, 20], [4, 50]])
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual(N.service_centres[1].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[1].number_of_servers, 3)
        self.assertEqual(N.service_centres[1].class_change_matrix, None)
        self.assertEqual(N.service_centres[1].schedule, None)
        self.assertFalse(N.service_centres[1].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0', 'Uniform: 0.2, 0.6'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0', 'Deterministic: 0.7'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5, 0.2], [0.0, 0.0]])
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {0:0})


        params = {'arrival_distributions': {'Class 0': [ciw.dists.Exponential(3.0)],
                                            'Class 1': [ciw.dists.Exponential(4.0)]},
                  'service_distributions': {'Class 0': [ciw.dists.Exponential(7.0)],
                                            'Class 1': [ciw.dists.Uniform(0.4, 1.2)]},
                  'number_of_servers': [9],
                  'routing': {'Class 0': [[0.5]],
                              'Class 1': [[0.0]]},
                  'queue_capacities': [float('inf')],
                  'class_change_matrices': {'Node 1': [[0.0, 1.0],
                                                       [0.2, 0.8]]}}
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].class_change_matrix, [[0.0, 1.0], [0.2, 0.8]])
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5]])
        self.assertEqual([str(d) for d in N.customer_classes[1].arrival_distributions], ['Exponential: 4.0'])
        self.assertEqual([str(d) for d in N.customer_classes[1].service_distributions], ['Uniform: 0.4, 1.2'])
        self.assertEqual(N.customer_classes[1].routing, [[0.0]])
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {0:0, 1:0})


        params = {'arrival_distributions': {'Class 0': [ciw.dists.Exponential(3.0)],
                                            'Class 1': [ciw.dists.Exponential(4.0)]},
                  'service_distributions': {'Class 0': [ciw.dists.Exponential(7.0)],
                                            'Class 1': [ciw.dists.Uniform(0.4, 1.2)]},
                  'number_of_servers': [9],
                  'routing': {'Class 0': [[0.5]],
                              'Class 1': [[0.0]]},
                  'queue_capacities': [float('inf')],
                  'priority_classes': {'Class 0': 1,
                                       'Class 1': 0}}
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5]])
        self.assertEqual([str(d) for d in N.customer_classes[1].arrival_distributions], ['Exponential: 4.0'])
        self.assertEqual([str(d) for d in N.customer_classes[1].service_distributions], ['Uniform: 0.4, 1.2'])
        self.assertEqual(N.customer_classes[1].routing, [[0.0]])
        self.assertEqual(N.customer_classes[0].priority_class, 1)
        self.assertEqual(N.customer_classes[1].priority_class, 0)
        self.assertEqual(N.number_of_priority_classes, 2)
        self.assertEqual(N.priority_class_mapping, {0:1, 1:0})


        params = {'arrival_distributions': [ciw.dists.Exponential(3.0), ciw.dists.Exponential(4.0), ciw.dists.Exponential(2.0)],
                  'service_distributions': [ciw.dists.Exponential(7.0), ciw.dists.Uniform(0.4, 1.2), ciw.dists.Deterministic(5.33)],
                  'number_of_servers': [9, 2, 4],
                  'routing': [[0.5, 0.0, 0.1],
                              [0.2, 0.1, 0.0],
                              [0.0, 0.0, 0.0]],
                  'queue_capacities': [float('inf'), float('inf'), float('inf')],
                  'baulking_functions': [None, None, example_baulking_function]}
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 3)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual(N.service_centres[1].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[1].number_of_servers, 2)
        self.assertEqual(N.service_centres[1].schedule, None)
        self.assertFalse(N.service_centres[1].preempt)
        self.assertEqual(N.service_centres[2].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[2].number_of_servers, 4)
        self.assertEqual(N.service_centres[2].schedule, None)
        self.assertFalse(N.service_centres[2].preempt)

        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0', 'Exponential: 4.0', 'Exponential: 2.0'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0', 'Uniform: 0.4, 1.2', 'Deterministic: 5.33'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5, 0.0, 0.1],
                                                         [0.2, 0.1, 0.0],
                                                         [0.0, 0.0, 0.0]])
        self.assertEqual(N.customer_classes[0].baulking_functions, [None, None, example_baulking_function])
        self.assertEqual(N.number_of_priority_classes, 1)

    def test_create_network_from_yml(self):
        N = ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml')
        self.assertEqual(N.number_of_nodes, 4)
        self.assertEqual(N.number_of_classes, 3)
        self.assertEqual(N.service_centres[0].queueing_capacity, 20)
        self.assertEqual(N.service_centres[1].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[2].queueing_capacity, 30)
        self.assertEqual(N.service_centres[3].queueing_capacity, float('inf'))
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
        self.assertFalse(N.service_centres[0].preempt)
        self.assertFalse(N.service_centres[1].preempt)
        self.assertFalse(N.service_centres[2].preempt)
        self.assertFalse(N.service_centres[3].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0', 'Exponential: 7.0', 'Exponential: 4.0', 'Exponential: 1.0'])
        self.assertEqual([str(d) for d in N.customer_classes[1].arrival_distributions], ['Exponential: 2.0', 'Exponential: 3.0', 'Exponential: 6.0', 'Exponential: 4.0'])
        self.assertEqual([str(d) for d in N.customer_classes[2].arrival_distributions], ['Exponential: 2.0', 'Exponential: 1.0', 'Exponential: 2.0', 'Exponential: 0.5'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0', 'Exponential: 7.0', 'Gamma: 0.4, 0.6', 'Deterministic: 0.5'])
        self.assertEqual([str(d) for d in N.customer_classes[1].service_distributions], ['Exponential: 7.0', 'Triangular: 0.1, 0.8, 0.85', 'Exponential: 8.0', 'Exponential: 5.0'])
        self.assertEqual([str(d) for d in N.customer_classes[2].service_distributions], ['Deterministic: 0.3', 'Deterministic: 0.2', 'Exponential: 8.0', 'Exponential: 9.0'])
        self.assertEqual(N.customer_classes[0].routing, [[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]])
        self.assertEqual(N.customer_classes[1].routing, [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]])
        self.assertEqual(N.customer_classes[2].routing, [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]])

    def test_raising_errors(self):
        params = {'arrival_distributions': {'Class 0':[['Exponential', 3.0]]},
                  'service_distributions': {'Class 0':[['Exponential', 7.0]]},
                  'number_of_servers': [9],
                  'number_of_classes': 1,
                  'routing': {'Class 0': [[0.5]]},
                  'number_of_nodes': 1,
                  'queue_capacities': [float('inf')],
                  'detect_deadlock': False}
        params_list = [copy.deepcopy(params) for i in range(23)]

        params_list[0]['number_of_classes'] = -2
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[0])
        params_list[1]['number_of_nodes'] = -2
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[1])
        params_list[2]['number_of_servers'] = [5, 6, 7]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[2])
        params_list[3]['number_of_servers'] = [-3]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[3])
        params_list[4]['number_of_servers'] = ['my_missing_schedule']
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[4])
        params_list[5]['queue_capacities'] = ['Inf', 1, 2]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[5])
        params_list[6]['queue_capacities'] = [-2]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[6])
        params_list[7]['arrival_distributions'] = {'Class 0':[['Exponential', 3.2]],
                                                   'Class 1':[['Exponential', 2.1]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[7])
        params_list[8]['arrival_distributions'] = {'Patient 0':[['Exponential', 11.5]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[8])
        params_list[9]['arrival_distributions']['Class 0'] = [['Exponential', 3.1],
                                                              ['Exponential', 2.4]]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[9])
        params_list[10]['service_distributions'] = {'Class 0':[['Exponential', 3.2]],
                                                    'Class 1':[['Exponential', 2.1]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[10])
        params_list[11]['service_distributions'] = {'Patient 0':[['Exponential', 11.5]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[11])
        params_list[12]['service_distributions']['Class 0'] = [['Exponential', 3.1],
                                                               ['Exponential', 2.4]]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[12])
        params_list[13]['routing'] = {'Class 0':[[0.2]],
                                      'Class 1':[[0.3]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[13])
        params_list[14]['routing'] = {'Patient 0':[[0.5]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[14])
        params_list[15]['routing']['Class 0'] = [[0.2], [0.1]]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[15])
        params_list[16]['routing']['Class 0'] = [[0.2, 0.1]]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[16])
        params_list[17]['routing']['Class 0'] = [[-0.6]]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[17])
        params_list[18]['routing']['Class 0'] = [[1.4]]
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[18])
        params_list[19]['class_change_matrices'] = {'Node 1':[[0.0]],
                                                    'Node 2':[[0.0]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[19])
        params_list[20]['class_change_matrices'] = {'Patient 0':[[0.0]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[20])
        params_list[21]['class_change_matrices'] = {'Node 1':[[-0.4]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[21])
        params_list[22]['class_change_matrices'] = {'Node 1':[[1.5]]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params_list[22])


class TestImportNoMatrix(unittest.TestCase):

    def test_optional_transition_matrix(self):
        params = {'arrival_distributions': [ciw.dists.Exponential(1.0)],
                  'service_distributions': [ciw.dists.Exponential(2.0)],
                  'number_of_servers': [1]}
        N = ciw.create_network(**params)
        self.assertEqual([c.routing for c in N.customer_classes], [[[0.0]]])

        N = ciw.create_network(
                arrival_distributions={'Class 0': [ciw.dists.Exponential(1.0)],
                                       'Class 1': [ciw.dists.Exponential(1.0)]},
                service_distributions={'Class 0': [ciw.dists.Exponential(2.0)],
                                       'Class 1': [ciw.dists.Exponential(1.0)]},
                number_of_servers=[1]
            )

        self.assertEqual([c.routing for c in N.customer_classes], [[[0.0]], [[0.0]]])

        params = {'arrival_distributions': [ciw.dists.Exponential(1.0), ciw.dists.Exponential(1.0)],
                  'service_distributions': [ciw.dists.Exponential(2.0), ciw.dists.Exponential(2.0)],
                  'number_of_servers': [1, 2]}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params)


class TestCreateNetworkKwargs(unittest.TestCase):
    def test_network_from_kwargs(self):
        N = ciw.create_network(
                arrival_distributions={'Class 0': [ciw.dists.Exponential(3.0)]},
                service_distributions={'Class 0': [ciw.dists.Exponential(7.0)]},
                number_of_servers=[9],
                routing={'Class 0': [[0.5]]},
                queue_capacities=[float('inf')]
            )
        
        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5]])
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {0:0})


        N = ciw.create_network(
                arrival_distributions=[ciw.dists.Exponential(3.0),
                                       ciw.dists.Uniform(0.2, 0.6)],
                service_distributions=[ciw.dists.Exponential(7.0),
                                       ciw.dists.Deterministic(0.7)],
                number_of_servers=[[[1, 20], [4, 50]], 3],
                routing=[[0.5, 0.2],
                         [0.0, 0.0]],
                queue_capacities=[10, float('inf')]
            )

        self.assertEqual(N.number_of_nodes, 2)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, 10)
        self.assertEqual(N.service_centres[0].number_of_servers, 'schedule')
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].schedule, [[1, 20], [4, 50]])
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual(N.service_centres[1].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[1].number_of_servers, 3)
        self.assertEqual(N.service_centres[1].class_change_matrix, None)
        self.assertEqual(N.service_centres[1].schedule, None)
        self.assertFalse(N.service_centres[1].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0', 'Uniform: 0.2, 0.6'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0', 'Deterministic: 0.7'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5, 0.2], [0.0, 0.0]])
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {0:0})


        N = ciw.create_network(
                arrival_distributions={'Class 0': [ciw.dists.Exponential(3.0)],
                                       'Class 1': [ciw.dists.Exponential(4.0)]},
                service_distributions={'Class 0': [ciw.dists.Exponential(7.0)],
                                       'Class 1': [ciw.dists.Uniform(0.4, 1.2)]},
                number_of_servers=[9],
                routing={'Class 0': [[0.5]],
                         'Class 1': [[0.0]]},
                queue_capacities=[float('inf')],
                class_change_matrices={'Node 1': [[0.0, 1.0],
                                                  [0.2, 0.8]]}
            )

        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].class_change_matrix, [[0.0, 1.0], [0.2, 0.8]])
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5]])
        self.assertEqual([str(d) for d in N.customer_classes[1].arrival_distributions], ['Exponential: 4.0'])
        self.assertEqual([str(d) for d in N.customer_classes[1].service_distributions], ['Uniform: 0.4, 1.2'])
        self.assertEqual(N.customer_classes[1].routing, [[0.0]])
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {0:0, 1:0})


        N = ciw.create_network(
                arrival_distributions={'Class 0': [ciw.dists.Exponential(3.0)],
                                       'Class 1': [ciw.dists.Exponential(4.0)]},
                service_distributions={'Class 0': [ciw.dists.Exponential(7.0)],
                                       'Class 1': [ciw.dists.Uniform(0.4, 1.2)]},
                number_of_servers=[9],
                routing={'Class 0': [[0.5]],
                         'Class 1': [[0.0]]},
                queue_capacities=['Inf'],
                priority_classes={'Class 0': 1,
                                  'Class 1': 0}
            )

        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5]])
        self.assertEqual([str(d) for d in N.customer_classes[1].arrival_distributions], ['Exponential: 4.0'])
        self.assertEqual([str(d) for d in N.customer_classes[1].service_distributions], ['Uniform: 0.4, 1.2'])
        self.assertEqual(N.customer_classes[1].routing, [[0.0]])
        self.assertEqual(N.customer_classes[0].priority_class, 1)
        self.assertEqual(N.customer_classes[1].priority_class, 0)
        self.assertEqual(N.number_of_priority_classes, 2)
        self.assertEqual(N.priority_class_mapping, {0:1, 1:0})


        N = ciw.create_network(
                arrival_distributions=[ciw.dists.Exponential(3.0),
                                       ciw.dists.Exponential(4.0),
                                       ciw.dists.Exponential(2.0)],
                service_distributions=[ciw.dists.Exponential(7.0),
                                       ciw.dists.Uniform(0.4, 1.2),
                                       ciw.dists.Deterministic(5.33)],
                number_of_servers=[9, 2, 4],
                routing=[[0.5, 0.0, 0.1],
                         [0.2, 0.1, 0.0],
                         [0.0, 0.0, 0.0]],
                queue_capacities=[float('inf'), float('inf'), float('inf')],
                baulking_functions=[None, None, example_baulking_function]
            )

        self.assertEqual(N.number_of_nodes, 3)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].schedule, None)
        self.assertFalse(N.service_centres[0].preempt)
        self.assertEqual(N.service_centres[1].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[1].number_of_servers, 2)
        self.assertEqual(N.service_centres[1].schedule, None)
        self.assertFalse(N.service_centres[1].preempt)
        self.assertEqual(N.service_centres[2].queueing_capacity, float('inf'))
        self.assertEqual(N.service_centres[2].number_of_servers, 4)
        self.assertEqual(N.service_centres[2].schedule, None)
        self.assertFalse(N.service_centres[2].preempt)

        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Exponential: 3.0', 'Exponential: 4.0', 'Exponential: 2.0'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Exponential: 7.0', 'Uniform: 0.4, 1.2', 'Deterministic: 5.33'])
        self.assertEqual(N.customer_classes[0].routing, [[0.5, 0.0, 0.1],
                                                         [0.2, 0.1, 0.0],
                                                         [0.0, 0.0, 0.0]])
        self.assertEqual(N.customer_classes[0].baulking_functions, [None, None, example_baulking_function])
        self.assertEqual(N.number_of_priority_classes, 1)


    def test_error_no_arrivals_servers_services(self):
        with self.assertRaises(ValueError):
            ciw.create_network()
        with self.assertRaises(ValueError):
            ciw.create_network(arrival_distributions=[ciw.dists.Exponential(0.2)])
        with self.assertRaises(ValueError):
            ciw.create_network(service_distributions=[ciw.dists.Exponential(0.2)])
        with self.assertRaises(ValueError):
            ciw.create_network(number_of_servers=[1])
        with self.assertRaises(ValueError):
            ciw.create_network(arrival_distributions=[ciw.dists.Exponential(0.2)], number_of_servers=[1])
        with self.assertRaises(ValueError):
            ciw.create_network(arrival_distributions=[ciw.dists.Exponential(0.2)], service_distributions=[ciw.dists.Exponential(0.2)])
        with self.assertRaises(ValueError):
            ciw.create_network(service_distributions=[ciw.dists.Exponential(0.2)], number_of_servers=[1])

    def test_error_extra_args(self):
        params = {'arrival_distributions': [ciw.dists.Exponential(3.0)],
                  'service_distributions': [ciw.dists.Exponential(7.0)],
                  'number_of_servers': [4],
                  'something_else': 56
                  }
        with self.assertRaises(TypeError):
            ciw.create_network(**params)

    def test_raise_error_wrong_batch_dist(self):
        params = {'arrival_distributions': [ciw.dists.Exponential(3.0)],
                  'service_distributions': [ciw.dists.Exponential(7.0)],
                  'number_of_servers': [4],
                  'batching_distributions': [ciw.dists.Exponential(1.3)]
                  }
        N = ciw.create_network(**params)
        with self.assertRaises(ValueError):
           Q = ciw.Simulation(N)
           Q.simulate_until_max_time(10)

    def test_read_dists_from_yml(self):
        N = ciw.create_network_from_yml('ciw/tests/testing_parameters/params_dists.yml')
        self.assertEqual([str(d) for d in N.customer_classes[0].arrival_distributions], ['Uniform: 1.4, 2.3', 'Deterministic: 3.0', 'Triangular: 0.5, 0.9, 1.4'])
        self.assertEqual([str(d) for d in N.customer_classes[1].arrival_distributions], ['Exponential: 0.4', 'Gamma: 8.8, 9.9', 'NoArrivals'])
        self.assertEqual([str(d) for d in N.customer_classes[0].service_distributions], ['Lognormal: 5.5, 3.6', 'Weibull: 5.0, 8.4', 'Distribution'])
        self.assertEqual([str(d) for d in N.customer_classes[1].service_distributions], ['Exponential: 0.5', 'Pmf', 'Normal: 5.0, 0.6'])
