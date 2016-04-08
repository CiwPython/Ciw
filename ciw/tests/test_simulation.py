import unittest
import ciw
from random import seed
from hypothesis import given
from hypothesis.strategies import floats, integers, lists, random_module
import os
import copy
from numpy import random as nprandom
from decimal import Decimal
import networkx as nx


def set_seed(x):
    seed(x)
    nprandom.seed(x)

class TestSimulation(unittest.TestCase):

    def test_repr_method(self):
        params1 = ciw.load_parameters(
          'ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml')
        Q = ciw.Simulation(params1)
        self.assertEqual(str(Q), 'Simulation')

        params2 = ciw.load_parameters(
          'ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml')
        params2['Name'] = 'My special simulation instance!'
        Q = ciw.Simulation(params2)
        self.assertEqual(str(Q), 'My special simulation instance!')

    def test_init_method_from_dict(self):
        Q = ciw.Simulation(ciw.load_parameters(
          'ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
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
                                 ['Triangular', 0.1, 0.85, 0.8],
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
        self.assertEqual([str(obs) for obs in Q.nodes],
          ['Arrival Node',
           'Node 1',
           'Node 2',
           'Node 3',
           'Node 4',
           'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 150)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])

        Q = ciw.Simulation(ciw.load_parameters(
          'ciw/tests/datafortesting/logs_test_for_dynamic_classes/parameters.yml'))
        self.assertEqual(Q.class_change_matrix,
          [[[0.5, 0.5], [0.5, 0.5]],
           [[1.0, 0.0], [0.0, 1.0]]])

        Q = ciw.Simulation(ciw.load_parameters(
          'ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
        self.assertEqual(Q.schedules, [True, False])


    def test_init_method_from_kws(self):
        # Define parameters
        Arrival_distributions = {'Class 0': [['Exponential', 3.0],
                                             ['Exponential', 7.0],
                                             ['Exponential', 4.0],
                                             ['Exponential', 1.0]],
                                 'Class 1': [['Exponential', 2.0],
                                             ['Exponential', 3.0],
                                             ['Exponential', 6.0],
                                             ['Exponential', 4.0]],
                                 'Class 2': [['Exponential', 2.0],
                                             ['Exponential', 1.0],
                                             ['Exponential', 2.0],
                                             ['Exponential', 0.5]]}
        Service_distributions = {'Class 0': [['Exponential', 7.0],
                                             ['Exponential', 7.0],
                                             ['Gamma', 0.4, 0.6],
                                             ['Deterministic', 0.5]],
                                  'Class 1':[['Exponential', 7.0],
                                             ['Triangular', 0.1, 0.85, 0.8],
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
        Detect_deadlock = False
        Simulation_time = 150
        Number_of_classes = 3
        Number_of_nodes = 4
        Class_change_matrices = {'Node 0': [[0.7, 0.3, 0.0],
                                            [0.2, 0.7, 0.1],
                                            [0.2, 0.7, 0.1]],
                                 'Node 1': [[1.0, 0.0, 0.0],
                                            [0.0, 1.0, 0.0],
                                            [0.0, 0.0, 1.0]],
                                 'Node 2': [[0.7, 0.3, 0.0],
                                            [0.2, 0.7, 0.1],
                                            [0.2, 0.7, 0.1]],
                                 'Node 3': [[1.0, 0.0, 0.0],
                                            [0.0, 1.0, 0.0],
                                            [0.0, 0.0, 1.0]]}
        schedule_1 = [[0, 1], [30, 2], [60, 1], [90, 3]]
        Cycle_length = 100
        Queue_capacities = [20, 'Inf', 30, 'Inf']

        Q = ciw.Simulation(Arrival_distributions = Arrival_distributions,
                           Simulation_time = Simulation_time,
                           Queue_capacities = Queue_capacities,
                           Service_distributions = Service_distributions,
                           Number_of_servers = Number_of_servers,
                           Transition_matrices = Transition_matrices,
                           Number_of_classes = Number_of_classes,
                           Number_of_nodes = Number_of_nodes,
                           Detect_deadlock = Detect_deadlock)
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
                                 ['Triangular', 0.1, 0.85, 0.8],
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
        self.assertEqual([str(obs) for obs in Q.nodes],
          ['Arrival Node',
           'Node 1',
           'Node 2',
           'Node 3',
           'Node 4',
           'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 150)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])
        self.assertEqual(Q.queue_capacities, [20, 'Inf', 30, 'Inf'])

        Q = ciw.Simulation(Arrival_distributions = Arrival_distributions,
                           Simulation_time = Simulation_time,
                           Service_distributions = Service_distributions,
                           Number_of_servers = Number_of_servers,
                           Transition_matrices = Transition_matrices)
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
                                 ['Triangular', 0.1, 0.85, 0.8],
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
        self.assertEqual([str(obs) for obs in Q.nodes],
          ['Arrival Node',
           'Node 1',
           'Node 2',
           'Node 3',
           'Node 4',
           'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 150)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])
        self.assertEqual(Q.queue_capacities, ['Inf', 'Inf', 'Inf', 'Inf'])

        Q = ciw.Simulation(Arrival_distributions = Arrival_distributions,
                           Simulation_time = Simulation_time,
                           Queue_capacities = Queue_capacities,
                           Service_distributions = Service_distributions,
                           Number_of_servers = Number_of_servers,
                           Transition_matrices = Transition_matrices,
                           Number_of_classes = Number_of_classes,
                           Number_of_nodes = Number_of_nodes,
                           Detect_deadlock = Detect_deadlock,
                           Class_change_matrices = Class_change_matrices)
        self.assertEqual(Q.class_change_matrix, [[[0.7, 0.3, 0.0],
                                                  [0.2, 0.7, 0.1],
                                                  [0.2, 0.7, 0.1]],
                                                 [[1.0, 0.0, 0.0],
                                                  [0.0, 1.0, 0.0],
                                                  [0.0, 0.0, 1.0]],
                                                 [[0.7, 0.3, 0.0],
                                                  [0.2, 0.7, 0.1],
                                                  [0.2, 0.7, 0.1]],
                                                 [[1.0, 0.0, 0.0],
                                                  [0.0, 1.0, 0.0],
                                                  [0.0, 0.0, 1.0]]])

        Q = ciw.Simulation(Arrival_distributions = Arrival_distributions,
                           Simulation_time = Simulation_time,
                           Queue_capacities = Queue_capacities,
                           Service_distributions = Service_distributions,
                           Number_of_servers = Number_of_servers2,
                           Transition_matrices = Transition_matrices,
                           Number_of_classes = Number_of_classes,
                           Number_of_nodes = Number_of_nodes,
                           Detect_deadlock = Detect_deadlock,
                           Class_change_matrices = Class_change_matrices,
                           schedule_1 = schedule_1,
                           Cycle_length = Cycle_length)
        self.assertEqual(Q.schedules, [False, False, True, False])

        Q = ciw.Simulation(
            Arrival_distributions = {'Class 2': [['Exponential', 2.0],
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
            Detect_deadlock = False,
            Simulation_time = 150,
            Number_of_servers = [9, 10, 8, 8],
            Queue_capacities = [20, 'Inf', 30, 'Inf'],
            Number_of_classes = 3,
            Service_distributions = {'Class 2': [['Deterministic', 0.3],
                                                 ['Deterministic', 0.2],
                                                 ['Exponential', 8.0],
                                                 ['Exponential', 9.0]],
                                     'Class 1': [['Exponential', 7.0],
                                                 ['Triangular', 0.1, 0.85, 0.8],
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
        self.assertEqual(Q.parameters, {
            'Arrival_distributions': {'Class 2': [['Exponential', 2.0],
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
            'Simulation_time': 150,
            'Detect_deadlock': False,
            'Exact': False,
            'Name': 'Simulation',
            'Number_of_servers': [9, 10, 8, 8],
            'Queue_capacities': [20, 'Inf', 30, 'Inf'],
            'Number_of_classes': 3,
            'Service_distributions': {'Class 2': [['Deterministic', 0.3],
                                                  ['Deterministic', 0.2],
                                                  ['Exponential', 8.0],
                                                  ['Exponential', 9.0]],
                                      'Class 1': [['Exponential', 7.0],
                                                  ['Triangular', 0.1, 0.85, 0.8],
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

    @given(arrival_rate = floats(min_value = 0.1, max_value = 100),
           service_rate = floats(min_value = 0.1, max_value = 100),
           number_of_servers = integers(min_value = 1, max_value = 30),
           Simulation_time = floats(min_value = 1.0, max_value = 10.0),
           rm = random_module())
    def test_simple_init_method(self,
                                arrival_rate,
                                service_rate,
                                number_of_servers,
                                Simulation_time,
                                rm):
        params = {'Arrival_distributions': [['Exponential', arrival_rate]],
                  'Service_distributions': [['Exponential', service_rate]],
                  'Number_of_servers': [number_of_servers],
                  'Simulation_time': Simulation_time,
                  'Transition_matrices': [[0.0]]}

        Q = ciw.Simulation(params)

        expected_dictionary = {
            'Arrival_distributions': {'Class 0': [['Exponential', arrival_rate]]},
            'Service_distributions': {'Class 0': [['Exponential', service_rate]]},
            'Transition_matrices': {'Class 0': [[0.0]]},
            'Number_of_servers': [number_of_servers],
            'Number_of_nodes': 1,
            'Number_of_classes': 1,
            'Name': 'Simulation',
            'Queue_capacities': ['Inf'],
            'Simulation_time': Simulation_time,
            'Detect_deadlock': False,
            'Exact': False
        }
        self.assertEqual(Q.parameters, expected_dictionary)
        self.assertEqual(Q.lmbda, [[['Exponential', arrival_rate]]])
        self.assertEqual(Q.mu, [[['Exponential', service_rate]]])
        self.assertEqual(Q.c, [number_of_servers])
        self.assertEqual(Q.transition_matrix, [[[0.0]]])
        self.assertEqual([str(obs) for obs in Q.nodes],
          ['Arrival Node', 'Node 1', 'Exit Node'])
        self.assertEqual(Q.max_simulation_time, Simulation_time)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False])

    @given(arrival_rate = floats(min_value = 0.1, max_value = 100),
           service_rate = floats(min_value = 0.1, max_value = 100),
           number_of_servers = integers(min_value = 1, max_value = 30),
           Simulation_time = floats(min_value = 1.0, max_value = 10.0),
           rm=random_module())
    def test_build_mmc_parameters(self,
                                  arrival_rate,
                                  service_rate,
                                  number_of_servers,
                                  Simulation_time,
                                  rm):
        params = {'Arrival_distributions': [['Exponential', arrival_rate]],
                  'Service_distributions': [['Exponential', service_rate]],
                  'Number_of_servers': [number_of_servers],
                  'Simulation_time': Simulation_time,
                  'Transition_matrices': [[0.0]]}
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
            'Detect_deadlock': False,
            'Exact': False,
            'Name': 'Simulation'
        }
        self.assertEqual(Q.build_parameters(params), expected_dictionary)

    def test_find_next_active_node_method(self):
        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        i = 0
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i += 1
        self.assertEqual(str(Q.find_next_active_node()), 'Arrival Node')

        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        i = 10
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i -= 1
        self.assertEqual(str(Q.find_next_active_node()), 'Node 4')

    def test_simulate_until_max_time_method(self):
        set_seed(2)
        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        Q.simulate_until_max_time()
        L = Q.get_all_individuals()
        self.assertEqual(round(
            L[300].data_records.values()[0][0].service_start_date, 8), 8.89002862)

        set_seed(60)
        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_dynamic_classes/parameters.yml'))
        Q.simulate_until_max_time()
        L = Q.get_all_individuals()
        drl = []
        for dr in L[0].data_records[1]:
            drl.append((dr.customer_class, dr.service_time))
        self.assertEqual(drl, [(1, 10.0), (0, 5.0), (0, 5.0)])

    def test_simulate_until_deadlock_method(self):
        set_seed(3)
        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        Q.simulate_until_deadlock()
        self.assertEqual(round(Q.times_to_deadlock[((0, 0), (0, 0))], 8), 31.26985409)

    def test_detect_deadlock_method(self):
        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        nodes = ['A', 'B', 'C', 'D', 'E']
        connections = [('A', 'D'), ('A', 'B'), ('B', 'E'), ('C', 'B'), ('E', 'C')]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), True)

        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        nodes = ['A', 'B', 'C', 'D']
        connections = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D')]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), False)

        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        nodes = ['A', 'B']
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), False)
        connections = [('A', 'A')]
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), True)

    def test_mm1_from_file(self):
        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_mm1/parameters.yml'))
        self.assertEqual(Q.transition_matrix, [[[0.0]]])

    @given(arrival_rate = floats(min_value = 0.1, max_value = 100),
           service_rate = floats(min_value = 0.1, max_value = 100),
           Simulation_time = floats(min_value = 1.0, max_value = 10.0),
           rm=random_module())
    def test_mminf_node(self, arrival_rate, service_rate, Simulation_time, rm):
        params = {'Arrival_distributions': [['Exponential', arrival_rate]],
                  'Service_distributions': [['Exponential', service_rate]],
                  'Number_of_servers': ['Inf'],
                  'Simulation_time': Simulation_time,
                  'Transition_matrices': [[0.0]]}

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
                  'Detect_deadlock': False}
        params_list = [copy.deepcopy(params) for i in range(28)]

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
        params_list[5]['Detect_deadlock'] = 'No'
        self.assertRaises(ValueError, ciw.Simulation, params_list[5])
        params_list[6]['Queue_capacities'] = ['Inf', 1, 2]
        self.assertRaises(ValueError, ciw.Simulation, params_list[6])
        params_list[7]['Queue_capacities'] = [-2]
        self.assertRaises(ValueError, ciw.Simulation, params_list[7])
        params_list[8]['Arrival_distributions'] = {'Class 0':[['Exponential', 3.2]],
                                                   'Class 1':[['Exponential', 2.1]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[8])
        params_list[9]['Arrival_distributions'] = {'Patient 0':[['Exponential', 11.5]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[9])
        params_list[10]['Arrival_distributions']['Class 0'] = [['Exponential', 3.1],
                                                               ['Exponential', 2.4]]
        self.assertRaises(ValueError, ciw.Simulation, params_list[10])
        params_list[11]['Service_distributions'] = {'Class 0':[['Exponential', 3.2]],
                                                    'Class 1':[['Exponential', 2.1]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[11])
        params_list[12]['Service_distributions'] = {'Patient 0':[['Exponential', 11.5]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[12])
        params_list[13]['Service_distributions']['Class 0'] = [['Exponential', 3.1],
                                                               ['Exponential', 2.4]]
        self.assertRaises(ValueError, ciw.Simulation, params_list[13])
        params_list[14]['Transition_matrices'] = {'Class 0':[[0.2]],
                                                  'Class 1':[[0.3]]}
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
        Q = ciw.Simulation(params_list[20])
        self.assertRaises(ValueError, Q.simulate_until_max_time,)
        del(params_list[21]['Simulation_time'])
        Q = ciw.Simulation(params_list[21])
        self.assertRaises(ValueError, Q.simulate_until_max_time,)
        params_list[22]['Class_change_matrices'] = {'Node 0':[[0.0]],
                                                    'Node 1':[[0.0]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[22])
        params_list[23]['Class_change_matrices'] = {'Patient 0':[[0.0]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[23])
        params_list[24]['Class_change_matrices'] = {'Node 0':[[0.1], [0.2]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[24])
        params_list[25]['Class_change_matrices'] = {'Node 0':[[0.0, 0.3]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[25])
        params_list[26]['Class_change_matrices'] = {'Node 0':[[-0.4]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[26])
        params_list[27]['Class_change_matrices'] = {'Node 0':[[1.5]]}
        self.assertRaises(ValueError, ciw.Simulation, params_list[27])

    def test_writing_data_files(self):
        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        Q.max_simulation_time = 50
        Q.simulate_until_max_time()
        files = [x for x in os.walk(
            'ciw/tests/datafortesting/logs_test_for_simulation/')][0][2]
        self.assertEqual('data.csv' in files, False)
        Q.write_records_to_file(
            'ciw/tests/datafortesting/logs_test_for_simulation/data.csv')
        files = [x for x in os.walk(
            'ciw/tests/datafortesting/logs_test_for_simulation/')][0][2]
        self.assertEqual('data.csv' in files, True)
        os.remove('ciw/tests/datafortesting/logs_test_for_simulation/data.csv')

        Q = ciw.Simulation(ciw.load_parameters(
            'ciw/tests/datafortesting/logs_test_for_mm1/parameters.yml'))
        Q.max_simulation_time = 50
        Q.simulate_until_max_time()
        files = [x for x in os.walk(
            'ciw/tests/datafortesting/logs_test_for_mm1/')][0][2]
        self.assertEqual('data_1.csv' in files, False)
        Q.write_records_to_file(
            'ciw/tests/datafortesting/logs_test_for_mm1/data_1.csv', False)
        files = [x for x in os.walk(
            'ciw/tests/datafortesting/logs_test_for_mm1/')][0][2]
        self.assertEqual('data_1.csv' in files, True)
        os.remove('ciw/tests/datafortesting/logs_test_for_mm1/data_1.csv')

    def test_simultaneous_events_example(self):
        Arrival_distributions = [['Deterministic', 10.0], 'NoArrivals']
        Service_distributions = [['Deterministic', 5.0], ['Deterministic', 5.0]]
        Transition_matrices = [[1.0, 0.0], [0.0, 0.0]]
        Simulation_time = 36
        Number_of_servers = [2, 1]
        Q = ciw.Simulation(Arrival_distributions = Arrival_distributions,
                           Service_distributions = Service_distributions,
                           Transition_matrices = Transition_matrices,
                           Simulation_time = Simulation_time,
                           Number_of_servers = Number_of_servers)
        Q.simulate_until_max_time()
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 3)
        self.assertTrue(all([x[6] == 5.0 for x in recs[1:]]))

    def test_exactness(self):
        set_seed(777)
        Arrival_distributions = [['Exponential', 20]]
        Service_distributions = [['Deterministic', 0.01]]
        Transition_matrices = [[0.0]]
        Simulation_time = 10
        Number_of_servers = ['server_schedule']
        Cycle_length = 3
        server_schedule = [[0.0, 0], [0.5, 1], [0.55, 0]]
        Q = ciw.Simulation(Arrival_distributions = Arrival_distributions,
                           Service_distributions = Service_distributions,
                           Transition_matrices = Transition_matrices,
                           Simulation_time = Simulation_time,
                           Number_of_servers = Number_of_servers,
                           Cycle_length = Cycle_length,
                           server_schedule = server_schedule)
        Q.simulate_until_max_time()
        recs = Q.get_all_records(headers = False)
        mod_service_starts = [obs%Cycle_length for obs in [r[5] for r in recs]]
        self.assertNotEqual(set(mod_service_starts), set([0.50, 0.51, 0.52, 0.53, 0.54]))

        set_seed(777)
        Arrival_distributions = [['Exponential', 20]]
        Service_distributions = [['Deterministic', 0.01]]
        Transition_matrices = [[0.0]]
        Simulation_time = 10
        Number_of_servers = ['server_schedule']
        Cycle_length = 3
        server_schedule = [[0.0, 0], [0.5, 1], [0.55, 0]]
        Q = ciw.Simulation(Arrival_distributions = Arrival_distributions,
                           Service_distributions = Service_distributions,
                           Transition_matrices = Transition_matrices,
                           Simulation_time = Simulation_time,
                           Number_of_servers = Number_of_servers,
                           Cycle_length = Cycle_length,
                           server_schedule = server_schedule,
                           Exact = 14)
        Q.simulate_until_max_time()
        recs = Q.get_all_records(headers=False)
        mod_service_starts = [obs%Cycle_length for obs in [r[5] for r in recs]]
        expected_set = set([Decimal(k) for k in ['0.50', '0.51', '0.52', '0.53', '0.54']])
        self.assertEqual(set(mod_service_starts), expected_set)
