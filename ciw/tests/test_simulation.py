import unittest
import ciw
from random import seed, getstate, setstate
from hypothesis import given
from hypothesis.strategies import floats, integers, composite, lists, fixed_dictionaries, random_module
import os
import copy
from numpy import random as nprandom


def set_seed(x):
    seed(x)
    nprandom.seed(x)



class TestSimulation(unittest.TestCase):

    def test_init_method_from_dict(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        self.assertEqual(Q.lmbda, [[['Exponential', 3.0],
                                    ['Exponential', 7.0],
                                    ['Exponential', 4.0],
                                    ['Exponential', 1.0]],
                                   [['Exponential', 2.0],
                                    ['Exponential', 3.0],
                                    ['Exponential', 6.0],
                                    ['Exponential', 4.0]],
                                   [['Exponential', 2.0],
                                    ['Exponential', 1.0],
                                    ['Exponential', 2.0],
                                    ['Exponential', 0.5]]])
        self.assertEqual(Q.mu, [[['Exponential', 7.0],
                                 ['Exponential', 7.0],
                                 ['Gamma', 0.4, 0.6],
                                 ['Deterministic', 0.5]],
                                [['Exponential', 7.0],
                                 ['Triangular', 0.1, 0.8, 0.85],
                                 ['Exponential', 8.0],
                                 ['Exponential', 5.0]],
                                [['Deterministic', 0.3],
                                 ['Deterministic', 0.2],
                                 ['Exponential', 8.0],
                                 ['Exponential', 9.0]]])
        self.assertEqual(Q.c, [9, 10, 8, 8])
        self.assertEqual(Q.transition_matrix, [[[0.1, 0.2, 0.1, 0.4],
                                                [0.2, 0.2, 0.0, 0.1],
                                                [0.0, 0.8, 0.1, 0.1],
                                                [0.4, 0.1, 0.1, 0.0]],
                                               [[0.6, 0.0, 0.0, 0.2],
                                                [0.1, 0.1, 0.2, 0.2],
                                                [0.9, 0.0, 0.0, 0.0],
                                                [0.2, 0.1, 0.1, 0.1]],
                                               [[0.0, 0.0, 0.4, 0.3],
                                                [0.1, 0.1, 0.1, 0.1],
                                                [0.1, 0.3, 0.2, 0.2],
                                                [0.0, 0.0, 0.0, 0.3]]])
        self.assertEqual([str(obs) for obs in Q.nodes], ['Arrival Node', 'Node 1', 'Node 2', 'Node 3', 'Node 4', 'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 2500)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])


        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_dynamic_classes/parameters.yml'))
        self.assertEqual(Q.class_change_matrix, [[[0.5, 0.5], [0.5, 0.5]], [[1.0, 0.0], [0.0, 1.0]]])


        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
        self.assertEqual(Q.schedules, [True, False])

    def test_init_method_from_kws(self):
        # Define parameters
        Arrival_distributions = {'Class 0':[['Exponential', 3.0],
                                    ['Exponential', 7.0],
                                    ['Exponential', 4.0],
                                    ['Exponential', 1.0]],
                         'Class 1':[['Exponential', 2.0],
                                    ['Exponential', 3.0],
                                    ['Exponential', 6.0],
                                    ['Exponential', 4.0]],
                         'Class 2':[['Exponential', 2.0],
                                    ['Exponential', 1.0],
                                    ['Exponential', 2.0],
                                    ['Exponential', 0.5]]}
        Service_distributions = {'Class 0':[['Exponential', 7.0],
                                            ['Exponential', 7.0],
                                            ['Gamma', 0.4, 0.6],
                                            ['Deterministic', 0.5]],
                                 'Class 1':[['Exponential', 7.0],
                                            ['Triangular', 0.1, 0.8, 0.85],
                                            ['Exponential', 8.0],
                                            ['Exponential', 5.0]],
                                 'Class 2':[['Deterministic', 0.3],
                                            ['Deterministic', 0.2],
                                            ['Exponential', 8.0],
                                            ['Exponential', 9.0]]}
        Number_of_servers = [9, 10, 8, 8]
        Number_of_servers2 = [9, 10, 'schedule_1', 8]
        Transition_matrices = {'Class 0': [[0.1, 0.2, 0.1, 0.4],
                                           [0.2, 0.2, 0.0, 0.1],
                                           [0.0, 0.8, 0.1, 0.1],
                                           [0.4, 0.1, 0.1, 0.0]],
                               'Class 1': [[0.6, 0.0, 0.0, 0.2],
                                           [0.1, 0.1, 0.2, 0.2],
                                           [0.9, 0.0, 0.0, 0.0],
                                           [0.2, 0.1, 0.1, 0.1]],
                                'Class 2':[[0.0, 0.0, 0.4, 0.3],
                                           [0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.3, 0.2, 0.2],
                                           [0.0, 0.0, 0.0, 0.3]]}
        detect_deadlock = False
        Simulation_time = 2500
        Number_of_classes = 3
        Number_of_nodes = 4
        Class_change_matrices = {'Node 0':[[0.7, 0.3, 0.0],
                                           [0.2, 0.7, 0.1],
                                           [0.2, 0.7, 0.1]],
                                 'Node 1':[[1.0, 0.0, 0.0],
                                           [0.0, 1.0, 0.0],
                                           [0.0, 0.0, 1.0]],
                                 'Node 2':[[0.7, 0.3, 0.0],
                                           [0.2, 0.7, 0.1],
                                           [0.2, 0.7, 0.1]],
                                 'Node 3':[[1.0, 0.0, 0.0],
                                           [0.0, 1.0, 0.0],
                                           [0.0, 0.0, 1.0]]}
        schedule_1 = [[0, 1], [30, 2], [60, 1], [90, 3]]
        cycle_length=100
        Queue_capacities = [20, 'Inf', 30, 'Inf']


        # The tests
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Simulation_time=Simulation_time,
                           Queue_capacities=Queue_capacities,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Number_of_classes=Number_of_classes,
                           Number_of_nodes=Number_of_nodes,
                           detect_deadlock=detect_deadlock)
        self.assertEqual(Q.lmbda, [[['Exponential', 3.0],
                                    ['Exponential', 7.0],
                                    ['Exponential', 4.0],
                                    ['Exponential', 1.0]],
                                   [['Exponential', 2.0],
                                    ['Exponential', 3.0],
                                    ['Exponential', 6.0],
                                    ['Exponential', 4.0]],
                                   [['Exponential', 2.0],
                                    ['Exponential', 1.0],
                                    ['Exponential', 2.0],
                                    ['Exponential', 0.5]]])
        self.assertEqual(Q.mu, [[['Exponential', 7.0],
                                 ['Exponential', 7.0],
                                 ['Gamma', 0.4, 0.6],
                                 ['Deterministic', 0.5]],
                                [['Exponential', 7.0],
                                 ['Triangular', 0.1, 0.8, 0.85],
                                 ['Exponential', 8.0],
                                 ['Exponential', 5.0]],
                                [['Deterministic', 0.3],
                                 ['Deterministic', 0.2],
                                 ['Exponential', 8.0],
                                 ['Exponential', 9.0]]])
        self.assertEqual(Q.c, [9, 10, 8, 8])
        self.assertEqual(Q.transition_matrix, [[[0.1, 0.2, 0.1, 0.4],
                                                [0.2, 0.2, 0.0, 0.1],
                                                [0.0, 0.8, 0.1, 0.1],
                                                [0.4, 0.1, 0.1, 0.0]],
                                               [[0.6, 0.0, 0.0, 0.2],
                                                [0.1, 0.1, 0.2, 0.2],
                                                [0.9, 0.0, 0.0, 0.0],
                                                [0.2, 0.1, 0.1, 0.1]],
                                               [[0.0, 0.0, 0.4, 0.3],
                                                [0.1, 0.1, 0.1, 0.1],
                                                [0.1, 0.3, 0.2, 0.2],
                                                [0.0, 0.0, 0.0, 0.3]]])
        self.assertEqual([str(obs) for obs in Q.nodes], ['Arrival Node', 'Node 1', 'Node 2', 'Node 3', 'Node 4', 'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 2500)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])
        self.assertEqual(Q.queue_capacities, [20, 'Inf', 30, 'Inf'])

        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Simulation_time=Simulation_time,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices)
        self.assertEqual(Q.lmbda, [[['Exponential', 3.0],
                                    ['Exponential', 7.0],
                                    ['Exponential', 4.0],
                                    ['Exponential', 1.0]],
                                   [['Exponential', 2.0],
                                    ['Exponential', 3.0],
                                    ['Exponential', 6.0],
                                    ['Exponential', 4.0]],
                                   [['Exponential', 2.0],
                                    ['Exponential', 1.0],
                                    ['Exponential', 2.0],
                                    ['Exponential', 0.5]]])
        self.assertEqual(Q.mu, [[['Exponential', 7.0],
                                 ['Exponential', 7.0],
                                 ['Gamma', 0.4, 0.6],
                                 ['Deterministic', 0.5]],
                                [['Exponential', 7.0],
                                 ['Triangular', 0.1, 0.8, 0.85],
                                 ['Exponential', 8.0],
                                 ['Exponential', 5.0]],
                                [['Deterministic', 0.3],
                                 ['Deterministic', 0.2],
                                 ['Exponential', 8.0],
                                 ['Exponential', 9.0]]])
        self.assertEqual(Q.c, [9, 10, 8, 8])
        self.assertEqual(Q.transition_matrix, [[[0.1, 0.2, 0.1, 0.4],
                                                [0.2, 0.2, 0.0, 0.1],
                                                [0.0, 0.8, 0.1, 0.1],
                                                [0.4, 0.1, 0.1, 0.0]],
                                               [[0.6, 0.0, 0.0, 0.2],
                                                [0.1, 0.1, 0.2, 0.2],
                                                [0.9, 0.0, 0.0, 0.0],
                                                [0.2, 0.1, 0.1, 0.1]],
                                               [[0.0, 0.0, 0.4, 0.3],
                                                [0.1, 0.1, 0.1, 0.1],
                                                    [0.1, 0.3, 0.2, 0.2],
                                            [0.0, 0.0, 0.0, 0.3]]])
        self.assertEqual([str(obs) for obs in Q.nodes], ['Arrival Node', 'Node 1', 'Node 2', 'Node 3', 'Node 4', 'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 2500)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])
        self.assertEqual(Q.queue_capacities, ['Inf', 'Inf', 'Inf', 'Inf'])

        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Simulation_time=Simulation_time,
                           Queue_capacities=Queue_capacities,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Number_of_classes=Number_of_classes,
                           Number_of_nodes=Number_of_nodes,
                           detect_deadlock=detect_deadlock,
                           Class_change_matrices=Class_change_matrices)
        self.assertEqual(Q.class_change_matrix, [[[0.7, 0.3, 0.0],
                                                  [0.2, 0.7, 0.1],
                                                  [0.2, 0.7, 0.1]],
                                                 [[1.0, 0.0, 0.0],
                                                  [0.0, 1.0, 0.0],
                                                  [0.0, 0.0, 1.0]],
                                                 [[0.7, 0.3, 0.0],
                                                  [0.2, 0.7, 0.1],
                                                  [0.2, 0.7,0.1]],
                                                 [[1.0, 0.0, 0.0],
                                                  [0.0, 1.0, 0.0],
                                                  [0.0, 0.0, 1.0]]])

        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Simulation_time=Simulation_time,
                           Queue_capacities=Queue_capacities,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers2,
                           Transition_matrices=Transition_matrices,
                           Number_of_classes=Number_of_classes,
                           Number_of_nodes=Number_of_nodes,
                           detect_deadlock=detect_deadlock,
                           Class_change_matrices=Class_change_matrices,
                           schedule_1=schedule_1,
                           cycle_length=cycle_length)
        self.assertEqual(Q.schedules, [False, False, True, False])

        Q = ciw.Simulation(Arrival_distributions = {'Class 2': [['Exponential', 2.0],
                                                        ['Exponential', 1.0],
                                                        ['Exponential', 2.0],
                                                        ['Exponential', 0.5]],
                                            'Class 1': [['Exponential', 2.0],
                                                        ['Exponential', 3.0],
                                                        ['Exponential', 6.0],
                                                        ['Exponential', 4.0]],
                                            'Class 0': [['Exponential', 3.0],
                                                        ['Exponential', 7.0],
                                                        ['Exponential', 4.0],
                                                        ['Exponential', 1.0]]},
                           Number_of_nodes = 4,
                           detect_deadlock = False,
                           Simulation_time = 2500,
                           Number_of_servers = [9, 10, 8, 8],
                           Queue_capacities = [20, 'Inf', 30, 'Inf'],
                           Number_of_classes = 3,
                           Service_distributions = {'Class 2': [['Deterministic', 0.3],
                                                        ['Deterministic', 0.2],
                                                        ['Exponential', 8.0],
                                                        ['Exponential', 9.0]],
                                            'Class 1': [['Exponential', 7.0],
                                                        ['Triangular', 0.1, 0.8, 0.85],
                                                        ['Exponential', 8.0],
                                                        ['Exponential', 5.0]],
                                            'Class 0': [['Exponential', 7.0],
                                                        ['Exponential', 7.0],
                                                        ['Gamma', 0.4, 0.6],
                                                        ['Deterministic', 0.5]]},
                            Transition_matrices = {'Class 2': [[0.0, 0.0, 0.4, 0.3],
                                                               [0.1, 0.1, 0.1, 0.1],
                                                               [0.1, 0.3, 0.2, 0.2],
                                                               [0.0, 0.0, 0.0, 0.3]],
                                                   'Class 1': [[0.6, 0.0, 0.0, 0.2],
                                                               [0.1, 0.1, 0.2, 0.2],
                                                               [0.9, 0.0, 0.0, 0.0],
                                                               [0.2, 0.1, 0.1, 0.1]],
                                                   'Class 0': [[0.1, 0.2, 0.1, 0.4],
                                                               [0.2, 0.2, 0.0, 0.1],
                                                               [0.0, 0.8, 0.1, 0.1],
                                                               [0.4, 0.1, 0.1, 0.0]]})
        self.assertEqual(Q.parameters, {'Arrival_distributions': {'Class 2': [['Exponential', 2.0],
                                                                      ['Exponential', 1.0],
                                                                      ['Exponential', 2.0],
                                                                      ['Exponential', 0.5]],
                                                          'Class 1': [['Exponential', 2.0],
                                                                      ['Exponential', 3.0],
                                                                      ['Exponential', 6.0],
                                                                      ['Exponential', 4.0]],
                                                          'Class 0': [['Exponential', 3.0],
                                                                      ['Exponential', 7.0],
                                                                      ['Exponential', 4.0],
                                                                      ['Exponential', 1.0]]},
                                        'Number_of_nodes': 4,
                                        'Simulation_time': 2500,
                                        'detect_deadlock': False,
                                        'Number_of_servers': [9, 10, 8, 8],
                                        'Queue_capacities': [20, 'Inf', 30, 'Inf'],
                                        'Number_of_classes': 3,
                                        'Service_distributions': {'Class 2': [['Deterministic', 0.3],
                                                                              ['Deterministic', 0.2],
                                                                              ['Exponential', 8.0],
                                                                              ['Exponential', 9.0]],
                                                                  'Class 1': [['Exponential', 7.0],
                                                                              ['Triangular', 0.1, 0.8, 0.85],
                                                                              ['Exponential', 8.0],
                                                                              ['Exponential', 5.0]],
                                                                  'Class 0': [['Exponential', 7.0],
                                                                              ['Exponential', 7.0],
                                                                              ['Gamma', 0.4, 0.6],
                                                                              ['Deterministic', 0.5]]},
                                        'Transition_matrices': {'Class 2': [[0.0, 0.0, 0.4, 0.3],
                                                                            [0.1, 0.1, 0.1, 0.1],
                                                                            [0.1, 0.3, 0.2, 0.2],
                                                                            [0.0, 0.0, 0.0, 0.3]],
                                                                'Class 1': [[0.6, 0.0, 0.0, 0.2],
                                                                            [0.1, 0.1, 0.2, 0.2],
                                                                            [0.9, 0.0, 0.0, 0.0],
                                                                            [0.2, 0.1, 0.1, 0.1]],
                                                                'Class 0': [[0.1, 0.2, 0.1, 0.4],
                                                                            [0.2, 0.2, 0.0, 0.1],
                                                                            [0.0, 0.8, 0.1, 0.1],
                                                                            [0.4, 0.1, 0.1, 0.0]]}})

    @given(arrival_rate=floats(min_value=0.1, max_value=100),
           service_rate=floats(min_value=0.1, max_value=100),
           number_of_servers=integers(min_value=1),
           Simulation_time=floats(min_value=1.0, max_value=10.0),
           rm=random_module())
    def test_simple_init_method(self, arrival_rate, service_rate, number_of_servers, Simulation_time, rm):
        """
        Test for creating M/M/c queues
        """
        params = {'Arrival_distributions':[['Exponential', arrival_rate]],
                  'Service_distributions':[['Exponential', service_rate]],
                  'Number_of_servers':[number_of_servers],
                  'Simulation_time':Simulation_time,
                  'Transition_matrices':[[0.0]]}

        Q = ciw.Simulation(params)

        expected_dictionary = {
            'Arrival_distributions': {'Class 0': [['Exponential', arrival_rate]]},
            'Service_distributions': {'Class 0': [['Exponential', service_rate]]},
            'Transition_matrices': {'Class 0': [[0.0]]},
            'Number_of_servers': [number_of_servers],
            'Number_of_nodes': 1,
            'Number_of_classes': 1,
            'Queue_capacities': ['Inf'],
            'Simulation_time': Simulation_time,
            'detect_deadlock': False
        }
        self.assertEqual(Q.parameters, expected_dictionary)
        self.assertEqual(Q.lmbda, [[['Exponential', arrival_rate]]])
        self.assertEqual(Q.mu, [[['Exponential', service_rate]]])
        self.assertEqual(Q.c, [number_of_servers])
        self.assertEqual(Q.transition_matrix, [[[0.0]]])
        self.assertEqual([str(obs) for obs in Q.nodes], ['Arrival Node', 'Node 1', 'Exit Node'])
        self.assertEqual(Q.max_simulation_time, Simulation_time)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False])

    @given(arrival_rate=floats(min_value=0.1, max_value=100),
           service_rate=floats(min_value=0.1, max_value=100),
           number_of_servers=integers(min_value=1),
           Simulation_time=floats(min_value=1.0, max_value=10.0),
           rm=random_module())
    def test_build_mmc_parameters(self, arrival_rate, service_rate, number_of_servers, Simulation_time, rm):
        params = {'Arrival_distributions':[['Exponential', arrival_rate]],
                  'Service_distributions':[['Exponential', service_rate]],
                  'Number_of_servers':[number_of_servers],
                  'Simulation_time':Simulation_time,
                  'Transition_matrices':[[0.0]]}

        Q = ciw.Simulation(params)

        expected_dictionary = {
            'Arrival_distributions': {'Class 0': [['Exponential', arrival_rate]]},
            'Service_distributions': {'Class 0': [['Exponential', service_rate]]},
            'Transition_matrices': {'Class 0': [[0.0]]},
            'Number_of_servers': [number_of_servers],
            'Number_of_nodes': 1,
            'Number_of_classes': 1,
            'Queue_capacities': ['Inf'],
            'Simulation_time': Simulation_time,
            'detect_deadlock': False
        }
        self.assertEqual(Q.build_parameters(params), expected_dictionary)

    def test_find_next_active_node_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        i = 0
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i += 1
        self.assertEqual(str(Q.find_next_active_node()), 'Arrival Node')

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        i = 10
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i -= 1
        self.assertEqual(str(Q.find_next_active_node()), 'Node 4')

    def test_custom_pdf_method(self):
        set_seed(45)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 10.7)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 10.7)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 9.5)

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_custom_dist/parameters.yml'))
        self.assertEqual(Q.service_times[1][0](), 5.0)
        self.assertEqual(Q.service_times[1][0](), 6.0)
        self.assertEqual(Q.service_times[1][0](), 6.0)
        self.assertEqual(Q.service_times[1][1](), 5.0)
        self.assertEqual(Q.service_times[1][1](), 5.0)
        self.assertEqual(Q.service_times[1][1](), 6.0)
        self.assertEqual(Q.service_times[2][1](), 1.3)
        self.assertEqual(Q.service_times[2][1](), 1.3)
        self.assertEqual(Q.service_times[2][1](), 2.1)
        self.assertEqual(Q.service_times[2][1](), 1.9)
        self.assertEqual(Q.service_times[2][1](), 1.5)
        self.assertEqual(Q.service_times[2][1](), 2.1)
        self.assertEqual(Q.service_times[2][1](), 1.9)

    def test_simulate_until_max_time_method(self):
        set_seed(2)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        Q.max_simulation_time = 600
        Q.simulate_until_max_time()
        L = Q.get_all_individuals()
        self.assertEqual(round(L[300].data_records.values()[0][0].service_start_date, 8), 8.8086502)

        set_seed(60)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_dynamic_classes/parameters.yml'))
        Q.simulate_until_max_time()
        L = Q.get_all_individuals()
        drl = []
        for dr in L[0].data_records[1]:
            drl.append((dr.customer_class, dr.service_time))
        self.assertEqual(drl, [(1, 10.0), (0, 5.0), (0, 5.0)])

    def test_simulate_until_deadlock_method(self):
        set_seed(3)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        times = Q.simulate_until_deadlock()
        self.assertEqual(round(times[((0, 0), (0, 0))], 8), 0.27861044)

    def test_detect_deadlock_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        nodes = ['A', 'B', 'C', 'D', 'E']
        connections = [('A', 'D'), ('A', 'B'), ('B', 'E'), ('C', 'B'), ('E', 'C')]
        for nd in nodes:
            Q.digraph.add_node(nd)
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), True)

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        nodes = ['A', 'B', 'C', 'D']
        connections = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D')]
        for nd in nodes:
            Q.digraph.add_node(nd)
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), False)

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        nodes = ['A', 'B']
        for nd in nodes:
            Q.digraph.add_node(nd)
        self.assertEqual(Q.detect_deadlock(), False)
        connections = [('A', 'A')]
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), True)

    def test_mm1_from_file(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_mm1/parameters.yml'))
        self.assertEqual(Q.transition_matrix, [[[0.0]]])

    @given(arrival_rate=floats(min_value=0.1, max_value=100),
           service_rate=floats(min_value=0.1, max_value=100),
           Simulation_time=floats(min_value=1.0, max_value=10.0),
           rm=random_module())
    def test_mminf_node(self, arrival_rate, service_rate, Simulation_time, rm):
        params = {'Arrival_distributions':[['Exponential', arrival_rate]],
                  'Service_distributions':[['Exponential', service_rate]],
                  'Number_of_servers':['Inf'],
                  'Simulation_time':Simulation_time,
                  'Transition_matrices':[[0.0]]}

        Q = ciw.Simulation(params)
        Q.simulate_until_max_time()
        inds = Q.get_all_individuals()
        waits = [ind.data_records[1][0].wait for ind in inds]
        self.assertEqual(sum(waits), 0.0)

    def test_raising_errors(self):
        params = {'Arrival_distributions': {'Class 0':[['Exponential', 3.0]]},
                  'Service_distributions': {'Class 0':[['Exponential', 7.0]]},
                  'Number_of_servers': [9],
                  'Number_of_classes': 1,
                  'Transition_matrices': {'Class 0': [[0.5]]},
                  'Simulation_time': 400,
                  'Number_of_nodes': 1,
                  'Queue_capacities': ['Inf'],
                  'detect_deadlock': False}

        params_list = [copy.deepcopy(params) for i in range(27)]

        params_list[0]['Number_of_classes'] = -2
        self.assertRaises(ValueError, ciw.Simulation, params_list[0])
        params_list[1]['Number_of_nodes'] = -2
        self.assertRaises(ValueError, ciw.Simulation, params_list[1])
        params_list[2]['Number_of_servers'] = [5, 6, 7]
        self.assertRaises(ValueError, ciw.Simulation, params_list[2])
        params_list[3]['Number_of_servers'] = [-3]
        self.assertRaises(ValueError, ciw.Simulation, params_list[3])
        params_list[4]['Number_of_servers'] = ['my_missing_schedule']
        self.assertRaises(ValueError, ciw.Simulation, params_list[4])
        params_list[5]['detect_deadlock'] = 'No'
        self.assertRaises(ValueError, ciw.Simulation, params_list[5])
        params_list[6]['Queue_capacities'] = ['Inf', 1, 2]
        self.assertRaises(ValueError, ciw.Simulation, params_list[6])
        params_list[7]['Queue_capacities'] = [-2]
        self.assertRaises(ValueError, ciw.Simulation, params_list[7])
        params_list[8]['Arrival_distributions'] = {'Class 0':[['Exponential', 3.2]], 'Class 1':[['Exponential', 2.1]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[8])
        params_list[9]['Arrival_distributions'] = {'Patient 0':[['Exponential', 11.5]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[9])
        params_list[10]['Arrival_distributions']['Class 0'] = [['Exponential', 3.1], ['Exponential', 2.4]]
        self.assertRaises(ValueError, ciw.Simulation, params_list[10])
        params_list[11]['Service_distributions'] = {'Class 0':[['Exponential', 3.2]], 'Class 1':[['Exponential', 2.1]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[11])
        params_list[12]['Service_distributions'] = {'Patient 0':[['Exponential', 11.5]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[12])
        params_list[13]['Service_distributions']['Class 0'] = [['Exponential', 3.1], ['Exponential', 2.4]]
        self.assertRaises(ValueError, ciw.Simulation, params_list[13])
        params_list[14]['Transition_matrices'] = {'Class 0':[[0.2]], 'Class 1':[[0.3]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[14])
        params_list[15]['Transition_matrices'] = {'Patient 0':[[0.5]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[15])
        params_list[16]['Transition_matrices']['Class 0'] = [[0.2], [0.1]]
        self.assertRaises(ValueError, ciw.Simulation, params_list[16])
        params_list[17]['Transition_matrices']['Class 0'] = [[0.2, 0.1]]
        self.assertRaises(ValueError, ciw.Simulation, params_list[17])
        params_list[18]['Transition_matrices']['Class 0'] = [[-0.6]]
        self.assertRaises(ValueError, ciw.Simulation, params_list[18])
        params_list[19]['Transition_matrices']['Class 0'] = [[1.4]]
        self.assertRaises(ValueError, ciw.Simulation, params_list[19])
        params_list[20]['Simulation_time'] = -2000
        self.assertRaises(ValueError, ciw.Simulation, params_list[20])
        params_list[21]['Class_change_matrices'] = {'Node 0':[[0.0]], 'Node 1':[[0.0]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[21])
        params_list[22]['Class_change_matrices'] = {'Patient 0':[[0.0]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[22])
        params_list[23]['Class_change_matrices'] = {'Node 0':[[0.1], [0.2]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[23])
        params_list[24]['Class_change_matrices'] = {'Node 0':[[0.0, 0.3]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[24])
        params_list[25]['Class_change_matrices'] = {'Node 0':[[-0.4]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[25])
        params_list[26]['Class_change_matrices'] = {'Node 0':[[1.5]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[26])

    def test_sampling_service_times(self):
        my_empirical_dist = [8.0, 8.0, 8.0, 8.8, 8.8, 12.3]
        Arrival_distributions = {'Class 0': [['Uniform', 2.2, 3.3],
                                     ['Deterministic', 4.4],
                                     ['Triangular', 1.1, 6.6, 1.5],
                                     ['Exponential', 4.4],
                                     ['Gamma', 0.6, 1.2],
                                     ['Lognormal', 0.8, 0.2],
                                     ['Weibull', 0.9, 0.8],
                                     'NoArrivals',
                                     ['Empirical', 'ciw/tests/datafortesting/sample_empirical_dist.csv']]}
        Service_distributions = {'Class 0':[['Uniform', 2.2, 3.3],
                                            ['Deterministic', 4.4],
                                            ['Triangular', 1.1, 6.6, 1.5],
                                            ['Exponential', 4.4],
                                            ['Gamma', 0.6, 1.2],
                                            ['Lognormal', 0.8, 0.2],
                                            ['Weibull', 0.9, 0.8],
                                            ['testerror', 9],
                                            ['Empirical', my_empirical_dist]]}
        Number_of_servers = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        Transition_matrices = {'Class 0': [[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]]}
        Simulation_time = [2222]

        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nu = Q.transitive_nodes[0]
        Nd = Q.transitive_nodes[1]
        Nt = Q.transitive_nodes[2]
        Ne = Q.transitive_nodes[3]
        Ng = Q.transitive_nodes[4]
        Nl = Q.transitive_nodes[5]
        Nw = Q.transitive_nodes[6]
        Nf = Q.transitive_nodes[7]
        Nem = Q.transitive_nodes[8]
        set_seed(5)

        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 2.89)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 3.02)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 3.07)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 3.24)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 3.01)

        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)

        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 5.12)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 1.35)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 2.73)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 5.34)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 3.46)

        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.53)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.03)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.14)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.06)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.18)

        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 0.66)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 0.13)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 2.12)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 0.08)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 0.06)

        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 2.61)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 2.66)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 3.14)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 2.40)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 2.00)

        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 0.11)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 0.09)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 0.03)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 0.25)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 0.82)

        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.0)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.8)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.0)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.0)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.8)


        self.assertEqual(Q.service_times[8][0], False)

        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.73)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.55)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.73)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.98)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.26)

        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)

        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 5.76)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 1.32)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 3.95)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 4.51)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 1.30)

        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.35)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.10)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.20)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.00)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.01)

        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.11)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.28)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.04)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.01)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.03)

        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 3.54)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.28)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.06)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.13)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.68)

        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.48)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.42)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.03)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 2.80)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.01)

        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.7)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.2)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.7)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.1)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.3)

        self.assertEqual(Nf.simulation.inter_arrival_times[Nf.id_number][0](), 'Inf')

    @given(u=lists(floats(min_value=0.0, max_value=10000), min_size=2, max_size=2, unique=True).map(sorted),
           d=floats(min_value=0.0, max_value=10000),
           t=lists(floats(min_value=0.0, max_value=10000), min_size=3, max_size=3, unique=True).map(sorted),
           e=floats(min_value=0.001, max_value=10000),
           ga=floats(min_value=0.001, max_value=10000),
           gb=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_service_times_hypothesis_1(self, u, d, t, e, ga, gb, rm):
        ul, uh = u[0], u[1]
        tl, tm, th = t[0], t[1], t[2]
        Arrival_distributions = {'Class 0': [['Uniform', ul, uh],
                                             ['Deterministic', d],
                                             ['Triangular', tl, th, tm],
                                             ['Exponential', e],
                                             ['Gamma', ga, gb]]}
        Service_distributions = {'Class 0':[['Uniform', ul, uh],
                                            ['Deterministic', d],
                                            ['Triangular', tl, th, tm],
                                            ['Exponential', e],
                                            ['Gamma', ga, gb]]}
        Number_of_servers = [1, 1, 1, 1, 1]
        Transition_matrices = {'Class 0': [[0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1]]}
        Simulation_time = [2222]
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nu = Q.transitive_nodes[0]
        Nd = Q.transitive_nodes[1]
        Nt = Q.transitive_nodes[2]
        Ne = Q.transitive_nodes[3]
        Ng = Q.transitive_nodes[4]

        # The tests
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(ul <= Nu.simulation.service_times[Nu.id_number][0]() <= uh)
            self.assertEqual(Nd.simulation.service_times[Nd.id_number][0](), d)
            self.assertTrue(tl <= Nt.simulation.service_times[Nt.id_number][0]() <= th)
            self.assertTrue(Ne.simulation.service_times[Ne.id_number][0]() >= 0.0)
            self.assertTrue(Ng.simulation.service_times[Ng.id_number][0]() >= 0.0)

            self.assertTrue(ul <= Nu.simulation.inter_arrival_times[Nu.id_number][0]() <= uh)
            self.assertEqual(Nd.simulation.inter_arrival_times[Nd.id_number][0](), d)
            self.assertTrue(tl <= Nt.simulation.inter_arrival_times[Nt.id_number][0]() <= th)
            self.assertTrue(Ne.simulation.inter_arrival_times[Ne.id_number][0]() >= 0.0)
            self.assertTrue(Ng.simulation.inter_arrival_times[Ng.id_number][0]() >= 0.0)

    @given(lm=floats(min_value=-200, max_value=200),
           lsd=floats(min_value=0.001, max_value=80),
           wa=floats(min_value=0.01, max_value=200),
           wb=floats(min_value=0.01, max_value=200),
           custs=lists(floats(min_value=0.001, max_value=10000), unique=True, min_size=2),
           terr=floats(),
           dist=lists(floats(min_value=0.001, max_value=10000), min_size=1, max_size=20),
           rm=random_module())
    def test_sampling_service_times_hypothesis_2(self, lm, lsd, wa, wb, custs, terr, dist, rm):
        my_empirical_dist = dist
        Arrival_distributions = {'Class 0':[['Lognormal', lm, lsd],
                                            ['Weibull', wa, wb],
                                             'NoArrivals',
                                            ['Custom', 'my_custom_dist'],
                                            ['Empirical', my_empirical_dist]]}
        Service_distributions = {'Class 0':[['Lognormal', lm, lsd],
                                            ['Weibull', wa, wb],
                                            ['testerror', terr],
                                            ['Custom', 'my_custom_dist'],
                                            ['Empirical', 'ciw/tests/datafortesting/sample_empirical_dist.csv']]}
        Number_of_servers = [1, 1, 1, 1, 1]
        Transition_matrices = {'Class 0': [[0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1]]}
        Simulation_time = [2222]
        cust_vals = [round(i, 10) for i in custs]
        numprobs = len(cust_vals)
        probs = [1.0/numprobs for i in range(numprobs)]
        my_custom_dist = [list(i) for i in (zip(probs, cust_vals))]
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time,
                           my_custom_dist=my_custom_dist)
        Nl = Q.transitive_nodes[0]
        Nw = Q.transitive_nodes[1]
        Nf = Q.transitive_nodes[2]
        Nc = Q.transitive_nodes[3]
        Nem = Q.transitive_nodes[4]

        # The tests
        for itr in range(10): # Because repition happens in the simulation
            self.assertEqual(round(sum(probs), 10), 1.0)
            self.assertTrue(Nl.simulation.service_times[Nl.id_number][0]() >= 0.0)
            self.assertTrue(Nw.simulation.service_times[Nw.id_number][0]() >= 0.0)
            self.assertEqual(Nf.simulation.service_times[Nf.id_number][0], False)
            self.assertTrue(Nc.simulation.service_times[Nc.id_number][0]() in set(cust_vals))
            self.assertTrue(Nem.simulation.service_times[Nem.id_number][0]() in set([7.0, 7.1, 7.2, 7.3, 7.7, 7.8]))

            self.assertTrue(Nl.simulation.inter_arrival_times[Nl.id_number][0]() >= 0.0)
            self.assertTrue(Nw.simulation.inter_arrival_times[Nw.id_number][0]() >= 0.0)
            self.assertEqual(Nf.simulation.inter_arrival_times[Nf.id_number][0](), 'Inf')
            self.assertTrue(Nc.simulation.inter_arrival_times[Nc.id_number][0]() in set(cust_vals))
            self.assertTrue(Nem.simulation.inter_arrival_times[Nem.id_number][0]() in set(my_empirical_dist))

    def test_writing_data_files(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        Q.max_simulation_time = 500
        Q.simulate_until_max_time()
        files = [x for x in os.walk('ciw/tests/datafortesting/logs_test_for_simulation/')][0][2]
        self.assertEqual('data.csv' in files, False)
        Q.write_records_to_file('ciw/tests/datafortesting/logs_test_for_simulation/data.csv')
        files = [x for x in os.walk('ciw/tests/datafortesting/logs_test_for_simulation/')][0][2]
        self.assertEqual('data.csv' in files, True)
        os.remove('ciw/tests/datafortesting/logs_test_for_simulation/data.csv')

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_mm1/parameters.yml'))
        Q.max_simulation_time = 500
        Q.simulate_until_max_time()
        files = [x for x in os.walk('ciw/tests/datafortesting/logs_test_for_mm1/')][0][2]
        self.assertEqual('data_1.csv' in files, False)
        Q.write_records_to_file('ciw/tests/datafortesting/logs_test_for_mm1/data_1.csv', False)
        files = [x for x in os.walk('ciw/tests/datafortesting/logs_test_for_mm1/')][0][2]
        self.assertEqual('data_1.csv' in files, True)
        os.remove('ciw/tests/datafortesting/logs_test_for_mm1/data_1.csv')

