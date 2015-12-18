import unittest
import ciw
from random import seed
from hypothesis import given
from hypothesis.strategies import floats, integers, composite, lists, fixed_dictionaries



class TestSimulation(unittest.TestCase):

    def test_init_method_from_dict(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        self.assertEqual(Q.lmbda, [[3.0, 7.0, 4.0, 1.0], [2.0, 3.0, 6.0, 4.0], [2.0, 1.0, 2.0, 0.5]])
        self.assertEqual(Q.mu, [[['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]], [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]]])
        self.assertEqual(Q.c, [9, 10, 8, 8])
        self.assertEqual(Q.transition_matrix, [[[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]], [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]]])
        self.assertEqual([str(obs) for obs in Q.nodes], ['Arrival Node', 'Node 1', 'Node 2', 'Node 3', 'Node 4', 'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 2500)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_dynamic_classes/'))
        self.assertEqual(Q.class_change_matrix, [[[0.7, 0.3], [0.2, 0.8]], [[1.0, 0.0], [0.0, 1.0]]])

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/'))
        self.assertEqual(Q.schedules, [True, False])

        Q = ciw.Simulation(Arrival_rates = {'Class 2': [2.0, 1.0, 2.0, 0.5], 'Class 1': [2.0, 3.0, 6.0, 4.0], 'Class 0': [3.0, 7.0, 4.0, 1.0]}, Number_of_nodes = 4, detect_deadlock = False, Simulation_time = 2500, Number_of_servers = [9, 10, 8, 8], Queue_capacities = [20, 'Inf', 30, 'Inf'], Number_of_classes = 3, Service_rates = {'Class 2': [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]], 'Class 1': [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], 'Class 0': [['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]]}, Transition_matrices = {'Class 2': [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]], 'Class 1': [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], 'Class 0': [[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]]})
        self.assertEqual(Q.parameters, {'Arrival_rates': {'Class 2': [2.0, 1.0, 2.0, 0.5], 'Class 1': [2.0, 3.0, 6.0, 4.0], 'Class 0': [3.0, 7.0, 4.0, 1.0]}, 'Number_of_nodes': 4, 'Simulation_time': 2500, 'detect_deadlock': False, 'Number_of_servers': [9, 10, 8, 8], 'Queue_capacities': [20, 'Inf', 30, 'Inf'], 'Number_of_classes': 3, 'Service_rates': {'Class 2': [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]], 'Class 1': [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], 'Class 0': [['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]]}, 'Transition_matrices': {'Class 2': [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]], 'Class 1': [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], 'Class 0': [[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]]}})

    def test_init_method_from_kws(self):
        Arrival_rates = {'Class 0':[3.0, 7.0, 4.0, 1.0], 'Class 1':[2.0, 3.0, 6.0, 4.0], 'Class 2':[2.0, 1.0, 2.0, 0.5]}
        Service_rates = {'Class 0':[['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]], 'Class 1':[['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], 'Class 2':[['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]]}
        Number_of_servers = [9, 10, 8, 8]
        Number_of_servers2 = [9, 10, 'schedule_1', 8]
        Transition_matrices = {'Class 0':[[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]], 'Class 1': [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], 'Class 2':[[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]]}
        detect_deadlock = False
        Simulation_time = 2500
        Number_of_classes = 3
        Number_of_nodes = 4
        Class_change_matrices = {'Node 0':[[0.7, 0.3, 0.0], [0.2, 0.7, 0.1], [0.2, 0.7, 0.1]], 'Node 1':[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], 'Node 2':[[0.7, 0.3, 0.0], [0.2, 0.7, 0.1], [0.2, 0.7, 0.1]], 'Node 3':[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]}
        schedule_1 = [[0, 1], [30, 2], [60, 1], [90, 3]]
        cycle_length=100
        Queue_capacities = [20, 'Inf', 30, 'Inf']

        Q = ciw.Simulation(Arrival_rates=Arrival_rates, Simulation_time=Simulation_time, Queue_capacities=Queue_capacities, Service_rates=Service_rates,
                           Number_of_servers=Number_of_servers, Transition_matrices=Transition_matrices,
                           Number_of_classes=Number_of_classes, Number_of_nodes=Number_of_nodes, detect_deadlock=detect_deadlock)
        self.assertEqual(Q.lmbda, [[3.0, 7.0, 4.0, 1.0], [2.0, 3.0, 6.0, 4.0], [2.0, 1.0, 2.0, 0.5]])
        self.assertEqual(Q.mu, [[['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]], [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]]])
        self.assertEqual(Q.c, [9, 10, 8, 8])
        self.assertEqual(Q.transition_matrix, [[[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]], [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]]])
        self.assertEqual([str(obs) for obs in Q.nodes], ['Arrival Node', 'Node 1', 'Node 2', 'Node 3', 'Node 4', 'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 2500)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])

        Q = ciw.Simulation(Arrival_rates=Arrival_rates, Simulation_time=Simulation_time, Queue_capacities=Queue_capacities, Service_rates=Service_rates,
                           Number_of_servers=Number_of_servers, Transition_matrices=Transition_matrices,
                           Number_of_classes=Number_of_classes, Number_of_nodes=Number_of_nodes, detect_deadlock=detect_deadlock,
                           Class_change_matrices=Class_change_matrices)
        self.assertEqual(Q.class_change_matrix, [[[0.7, 0.3, 0.0], [0.2, 0.7, 0.1], [0.2, 0.7, 0.1]], [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], [[0.7, 0.3, 0.0], [0.2, 0.7, 0.1], [0.2, 0.7,0.1]], [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]])

        Q = ciw.Simulation(Arrival_rates=Arrival_rates, Simulation_time=Simulation_time, Queue_capacities=Queue_capacities, Service_rates=Service_rates,
                           Number_of_servers=Number_of_servers2, Transition_matrices=Transition_matrices,
                           Number_of_classes=Number_of_classes, Number_of_nodes=Number_of_nodes, detect_deadlock=detect_deadlock,
                           Class_change_matrices=Class_change_matrices, schedule_1=schedule_1, cycle_length=cycle_length)
        self.assertEqual(Q.schedules, [False, False, True, False])

        Q = ciw.Simulation(Arrival_rates = {'Class 2': [2.0, 1.0, 2.0, 0.5], 'Class 1': [2.0, 3.0, 6.0, 4.0], 'Class 0': [3.0, 7.0, 4.0, 1.0]}, Number_of_nodes = 4, detect_deadlock = False, Simulation_time = 2500, Number_of_servers = [9, 10, 8, 8], Queue_capacities = [20, 'Inf', 30, 'Inf'], Number_of_classes = 3, Service_rates = {'Class 2': [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]], 'Class 1': [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], 'Class 0': [['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]]}, Transition_matrices = {'Class 2': [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]], 'Class 1': [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], 'Class 0': [[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]]})
        self.assertEqual(Q.parameters, {'Arrival_rates': {'Class 2': [2.0, 1.0, 2.0, 0.5], 'Class 1': [2.0, 3.0, 6.0, 4.0], 'Class 0': [3.0, 7.0, 4.0, 1.0]}, 'Number_of_nodes': 4, 'Simulation_time': 2500, 'detect_deadlock': False, 'Number_of_servers': [9, 10, 8, 8], 'Queue_capacities': [20, 'Inf', 30, 'Inf'], 'Number_of_classes': 3, 'Service_rates': {'Class 2': [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]], 'Class 1': [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], 'Class 0': [['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]]}, 'Transition_matrices': {'Class 2': [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]], 'Class 1': [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], 'Class 0': [[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]]}})


    @given(arrival_rate=floats(min_value=0.0, max_value=999.99),
           service_rate=floats(min_value=0.0, max_value=999.99),
           number_of_servers=integers(min_value=1),
           Simulation_time=floats(min_value=1, max_value=728.88))
    def test_simple_init_method(self, arrival_rate,
                                service_rate,
                                number_of_servers,
                                Simulation_time):
        """
        Test for creating M/M/c queues
        """
        Q = ciw.Simulation(arrival_rate=arrival_rate,
                           service_rate=service_rate,
                           number_of_servers=number_of_servers,
                           Simulation_time=Simulation_time)

        expected_dictionary = {
            'Arrival_rates' : {'Class 0' : [arrival_rate]},
            'Service_rates' : {'Class 0' : [['Exponential', service_rate]]},
            'Transition_matrices' : {'Class 0' : [[0.0]]},
            'Number_of_servers' : [number_of_servers],
            'Number_of_nodes' : 1,
            'Number_of_classes' : 1,
            'Queue_capacities' : ['Inf'],
            'Simulation_time' : Simulation_time
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


    @given(arrival_rate=floats(min_value=0.0, max_value=999.99),
           service_rate=floats(min_value=0.0, max_value=999.99),
           number_of_servers=integers(min_value=1),
           Simulation_time=floats(min_value=1, max_value=728.88))
    def test_build_mmc_parameters(self,
                                  arrival_rate,
                                  service_rate,
                                  number_of_servers,
                                  Simulation_time):

        Q = ciw.Simulation(arrival_rate=arrival_rate,
                            service_rate=service_rate,
                            number_of_servers=number_of_servers,
                            Simulation_time=Simulation_time)

        expected_dictionary = {
            'Arrival_rates' : {'Class 0' : [arrival_rate]},
            'Service_rates' : {'Class 0' : [['Exponential', service_rate]]},
            'Transition_matrices' : {'Class 0' : [[0.0]]},
            'Number_of_servers' : [number_of_servers],
            'Number_of_nodes' : 1,
            'Number_of_classes' : 1,
            'Queue_capacities' : ['Inf'],
            'Simulation_time' : Simulation_time
        }
        self.assertEqual(Q.build_mmc_parameters(arrival_rate,
                                                service_rate,
                                                number_of_servers,
                                                Simulation_time),
                         expected_dictionary)






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
