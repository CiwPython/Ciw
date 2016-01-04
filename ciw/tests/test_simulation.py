import unittest
import ciw
from random import seed, getstate, setstate
from hypothesis import given
from hypothesis.strategies import floats, integers, composite, lists, fixed_dictionaries
import os

class TestSimulation(unittest.TestCase):

    def test_init_method_from_dict(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        self.assertEqual(Q.lmbda, [[3.0, 7.0, 4.0, 1.0],
                                   [2.0, 3.0, 6.0, 4.0],
                                   [2.0, 1.0, 2.0, 0.5]])
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


        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_dynamic_classes/'))
        self.assertEqual(Q.class_change_matrix, [[[0.7, 0.3], [0.2, 0.8]], [[1.0, 0.0], [0.0, 1.0]]])


        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/'))
        self.assertEqual(Q.schedules, [True, False])


    def test_init_method_from_kws(self):
        # Define parameters
        Arrival_rates = {'Class 0':[3.0, 7.0, 4.0, 1.0],
                         'Class 1':[2.0, 3.0, 6.0, 4.0],
                         'Class 2':[2.0, 1.0, 2.0, 0.5]}
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
        Q = ciw.Simulation(Arrival_rates=Arrival_rates,
                           Simulation_time=Simulation_time,
                           Queue_capacities=Queue_capacities,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Number_of_classes=Number_of_classes,
                           Number_of_nodes=Number_of_nodes,
                           detect_deadlock=detect_deadlock)
        self.assertEqual(Q.lmbda, [[3.0, 7.0, 4.0, 1.0],
                                   [2.0, 3.0, 6.0, 4.0],
                                   [2.0, 1.0, 2.0, 0.5]])
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

        Q = ciw.Simulation(Arrival_rates=Arrival_rates,
                           Simulation_time=Simulation_time,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices)
        self.assertEqual(Q.lmbda, [[3.0, 7.0, 4.0, 1.0],
                                   [2.0, 3.0, 6.0, 4.0],
                                   [2.0, 1.0, 2.0, 0.5]])
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

        Q = ciw.Simulation(Arrival_rates=Arrival_rates,
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

        Q = ciw.Simulation(Arrival_rates=Arrival_rates,
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

        Q = ciw.Simulation(Arrival_rates = {'Class 2': [2.0, 1.0, 2.0, 0.5],
                                            'Class 1': [2.0, 3.0, 6.0, 4.0],
                                            'Class 0': [3.0, 7.0, 4.0, 1.0]},
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
        self.assertEqual(Q.parameters, {'Arrival_rates': {'Class 2': [2.0, 1.0, 2.0, 0.5],
                                                          'Class 1': [2.0, 3.0, 6.0, 4.0],
                                                          'Class 0': [3.0, 7.0, 4.0, 1.0]},
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


    @given(arrival_rate=floats(min_value=0.0, max_value=999.99),
           service_rate=floats(min_value=0.01, max_value=999.99),
           number_of_servers=integers(min_value=1),
           Simulation_time=floats(min_value=1, max_value=999.99),
           myseed=integers())
    def test_simple_init_method(self, arrival_rate,
                                service_rate,
                                number_of_servers,
                                Simulation_time,
                                myseed):
        """
        Test for creating M/M/c queues
        """
        try:
            # Stuff to make random work with hypothesis
            state = getstate()
            seed(myseed)

            Q = ciw.Simulation(arrival_rate=arrival_rate,
                               service_rate=service_rate,
                               number_of_servers=number_of_servers,
                               Simulation_time=Simulation_time)

            expected_dictionary = {
                'Arrival_rates': {'Class 0': [arrival_rate]},
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
            self.assertEqual(Q.lmbda, [[arrival_rate]])
            self.assertEqual(Q.mu, [[['Exponential', service_rate]]])
            self.assertEqual(Q.c, [number_of_servers])
            self.assertEqual(Q.transition_matrix, [[[0.0]]])
            self.assertEqual([str(obs) for obs in Q.nodes], ['Arrival Node', 'Node 1', 'Exit Node'])
            self.assertEqual(Q.max_simulation_time, Simulation_time)
            self.assertEqual(Q.class_change_matrix, 'NA')
            self.assertEqual(Q.schedules, [False])
        finally:
            setstate(state)


    @given(arrival_rate=floats(min_value=0.0, max_value=999.99),
           service_rate=floats(min_value=0.01, max_value=999.99),
           number_of_servers=integers(min_value=1),
           Simulation_time=floats(min_value=1, max_value=999.99),
           myseed=integers())
    def test_build_mmc_parameters(self,
                                  arrival_rate,
                                  service_rate,
                                  number_of_servers,
                                  Simulation_time,
                                  myseed):
        try:
            # Stuff to make random work with hypothesis
            state = getstate()
            seed(myseed)

            Q = ciw.Simulation(arrival_rate=arrival_rate,
                               service_rate=service_rate,
                               number_of_servers=number_of_servers,
                               Simulation_time=Simulation_time)

            expected_dictionary = {
                'Arrival_rates': {'Class 0': [arrival_rate]},
                'Service_distributions': {'Class 0': [['Exponential', service_rate]]},
                'Transition_matrices': {'Class 0': [[0.0]]},
                'Number_of_servers': [number_of_servers],
                'Number_of_nodes': 1,
                'Number_of_classes': 1,
                'Queue_capacities': ['Inf'],
                'Simulation_time': Simulation_time
            }
            self.assertEqual(Q.build_mmc_parameters(arrival_rate,
                                                    service_rate,
                                                    number_of_servers,
                                                    Simulation_time),
                                                    expected_dictionary)
        finally:
            setstate(state)







    def test_find_next_active_node_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        i = 0
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i += 1
        self.assertEqual(str(Q.find_next_active_node()), 'Arrival Node')

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        i = 10
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i -= 1
        self.assertEqual(str(Q.find_next_active_node()), 'Node 4')

    def test_custom_pdf_method(self):
        seed(45)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 10.7)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 10.7)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 9.5)

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_custom_dist/'))
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
        seed(3)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        Q.simulate_until_max_time()
        L = Q.get_all_individuals()
        self.assertEqual(round(L[300].data_records.values()[0][0].service_start_date, 8), 6.04730086)

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_dynamic_classes/'))
        Q.simulate_until_max_time()
        L = Q.get_all_individuals()
        drl = []
        for dr in L[0].data_records[1]:
            drl.append((dr.customer_class, dr.service_time))
        self.assertEqual(drl, [(1, 10.0), (1, 10.0), (0, 5.0), (1, 10.0)])

    def test_simulate_until_deadlock_method(self):
        seed(3)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_deadlock_sim/'))
        times = Q.simulate_until_deadlock()
        self.assertEqual(round(times[((0, 0), (0, 0))], 8), 9.09939457)

    def test_detect_deadlock_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        nodes = ['A', 'B', 'C', 'D', 'E']
        connections = [('A', 'D'), ('A', 'B'), ('B', 'E'), ('C', 'B'), ('E', 'C')]
        for nd in nodes:
            Q.digraph.add_node(nd)
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), True)

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        nodes = ['A', 'B', 'C', 'D']
        connections = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D')]
        for nd in nodes:
            Q.digraph.add_node(nd)
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), False)

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        nodes = ['A', 'B']
        for nd in nodes:
            Q.digraph.add_node(nd)
        self.assertEqual(Q.detect_deadlock(), False)
        connections = [('A', 'A')]
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), True)

    def test_mm1_from_file(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_mm1/'))
        self.assertEqual(Q.transition_matrix, [[[0.0]]])


    @given(arrival_rate=floats(min_value=0.0, max_value=99.99),
           service_rate=floats(min_value=0.1, max_value=99.99),
           Simulation_time=floats(min_value=1, max_value=99.99),
           myseed=integers())
    def test_mminf_node(self, arrival_rate, service_rate, Simulation_time, myseed):
        try:
            # Stuff to make random work with hypothesis
            state = getstate()
            seed(myseed)

            Q = ciw.Simulation(arrival_rate=arrival_rate,
                               service_rate=service_rate,
                               number_of_servers='Inf',
                               Simulation_time=Simulation_time)
            Q.simulate_until_max_time()
            inds = Q.get_all_individuals()
            waits = [ind.data_records[1][0].wait for ind in inds]
            self.assertEqual(sum(waits), 0.0)

        finally:
            setstate(state)

    def test_raising_errors(self):
        Arrival_rates = {'Class 0':[3.0]}
        Arrival_rates2 = {'Class 0':[-3.0]}
        Service_distributions = {'Class 0':[['Exponential', 7.0]]}
        Service_distributions2 = {'Class 0':[['Exponential', 7.0], ['Lognormal', 0.5, 0.25]]}
        Number_of_servers = [9]
        Number_of_servers2 = [9, 10]
        Transition_matrices = {'Class 0': [[0.5]]}
        Transition_matrices3 = {'Class 0': [[1.2]]}
        Transition_matrices2 = {'Class 0': [[0.1, 0.2, 0.1, 0.4],
                                           [0.2, 0.2, 0.0, 0.1],
                                           [0.0, 0.8, 0.1, 0.1],
                                           [0.4, 0.1, 0.1, 0.0]]}
        Simulation_time = 400
        Simulation_time2 = -30
        Number_of_nodes = 1
        Queue_capacities = ['Inf']

        self.assertRaises(ValueError, ciw.Simulation, Arrival_rates=Arrival_rates,
                                                      Service_distributions=Service_distributions,
                                                      Number_of_servers=Number_of_servers2,
                                                      Transition_matrices=Transition_matrices,
                                                      Simulation_time=Simulation_time,
                                                      Number_of_nodes=Number_of_nodes,
                                                      Queue_capacities=Queue_capacities)
        self.assertRaises(ValueError, ciw.Simulation, Arrival_rates=Arrival_rates,
                                                      Service_distributions=Service_distributions2,
                                                      Number_of_servers=Number_of_servers,
                                                      Transition_matrices=Transition_matrices,
                                                      Simulation_time=Simulation_time,
                                                      Number_of_nodes=Number_of_nodes,
                                                      Queue_capacities=Queue_capacities)
        self.assertRaises(ValueError, ciw.Simulation, Arrival_rates=Arrival_rates,
                                                      Service_distributions=Service_distributions,
                                                      Number_of_servers=Number_of_servers,
                                                      Transition_matrices=Transition_matrices2,
                                                      Simulation_time=Simulation_time,
                                                      Number_of_nodes=Number_of_nodes,
                                                      Queue_capacities=Queue_capacities)
        self.assertRaises(ValueError, ciw.Simulation, Arrival_rates=Arrival_rates2,
                                                      Service_distributions=Service_distributions,
                                                      Number_of_servers=Number_of_servers,
                                                      Transition_matrices=Transition_matrices,
                                                      Simulation_time=Simulation_time,
                                                      Number_of_nodes=Number_of_nodes,
                                                      Queue_capacities=Queue_capacities)
        self.assertRaises(ValueError, ciw.Simulation, Arrival_rates=Arrival_rates,
                                                      Service_distributions=Service_distributions,
                                                      Number_of_servers=Number_of_servers,
                                                      Transition_matrices=Transition_matrices3,
                                                      Simulation_time=Simulation_time,
                                                      Number_of_nodes=Number_of_nodes,
                                                      Queue_capacities=Queue_capacities)
        self.assertRaises(ValueError, ciw.Simulation, Arrival_rates=Arrival_rates,
                                                      Service_distributions=Service_distributions,
                                                      Number_of_servers=Number_of_servers,
                                                      Transition_matrices=Transition_matrices,
                                                      Simulation_time=Simulation_time2,
                                                      Number_of_nodes=Number_of_nodes,
                                                      Queue_capacities=Queue_capacities)

    def test_sampling_service_times(self):
        Arrival_rates = {'Class 0': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}
        Service_distributions = {'Class 0':[['Uniform', 2.2, 3.3],
                                            ['Deterministic', 4.4],
                                            ['Triangular', 1.1, 6.6, 1.5],
                                            ['Exponential', 4.4],
                                            ['Gamma', 0.6, 1.2],
                                            ['Lognormal', 0.8, 0.2],
                                            ['Weibull', 0.9, 0.8],
                                            ['testerror', 9]]}
        Number_of_servers = [1, 1, 1, 1, 1, 1, 1, 1]
        Transition_matrices = {'Class 0': [[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                           [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]]}
        Simulation_time = [2222]

        Q = ciw.Simulation(Arrival_rates=Arrival_rates,
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
        seed(5)

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

        self.assertEqual(Q.service_times[8][0], False)


    def test_writing_data_files(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        Q.simulate_until_max_time()
        files = [x for x in os.walk('ciw/tests/datafortesting/logs_test_for_simulation/')][0][2]
        self.assertEqual('data.csv' in files, False)
        Q.write_records_to_file('ciw/tests/datafortesting/logs_test_for_simulation/data.csv')
        files = [x for x in os.walk('ciw/tests/datafortesting/logs_test_for_simulation/')][0][2]
        self.assertEqual('data.csv' in files, True)
        os.remove('ciw/tests/datafortesting/logs_test_for_simulation/data.csv')

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_mm1/'))
        Q.simulate_until_max_time()
        files = [x for x in os.walk('ciw/tests/datafortesting/logs_test_for_mm1/')][0][2]
        self.assertEqual('data_1.csv' in files, False)
        Q.write_records_to_file('ciw/tests/datafortesting/logs_test_for_mm1/data_1.csv', False)
        files = [x for x in os.walk('ciw/tests/datafortesting/logs_test_for_mm1/')][0][2]
        self.assertEqual('data_1.csv' in files, True)
        os.remove('ciw/tests/datafortesting/logs_test_for_mm1/data_1.csv')

