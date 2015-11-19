import unittest
import asq
from random import seed

class TestSimulation(unittest.TestCase):

    def test_init_method(self):
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        self.assertEqual(Q.lmbda, [[3.0, 7.0, 4.0, 1.0], [2.0, 3.0, 6.0, 4.0], [2.0, 1.0, 2.0, 0.5]])
        self.assertEqual(Q.mu, [[['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]], [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]]])
        self.assertEqual(Q.c, [9, 10, 8, 8])
        self.assertEqual(Q.transition_matrix, [[[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]], [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]]])
        self.assertEqual([str(obs) for obs in Q.nodes], ['Arrival Node', 'Node 1', 'Node 2', 'Node 3', 'Node 4', 'Exit Node'])
        self.assertEqual(Q.max_simulation_time, 2500)
        self.assertEqual(Q.class_change_matrix, 'NA')
        self.assertEqual(Q.schedules, [False, False, False, False])

        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_dynamic_classes/'))
        self.assertEqual(Q.class_change_matrix, [[[0.7, 0.3], [0.2, 0.8]], [[1.0, 0.0], [0.0, 1.0]]])

        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_server_schedule/'))
        self.assertEqual(Q.schedules, [True, False])

    def test_find_next_active_node_method(self):
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        i = 0
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i += 1
        self.assertEqual(str(Q.find_next_active_node()), 'Arrival Node')

        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        i = 10
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i -= 1
        self.assertEqual(str(Q.find_next_active_node()), 'Node 4')

    def test_custom_pdf_method(self):
        seed(45)
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 10.7)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 10.7)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 14.6)
        self.assertEqual(Q.custom_pdf([0.1, 0.4, 1.0], [9.5, 10.7, 14.6]), 9.5)

        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_custom_dist/'))
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
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        Q.simulate_until_max_time()
        L = Q.get_all_individuals()
        self.assertEqual(round(L[300].data_records.values()[0][0].service_start_date, 8), 6.04730086)

        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_dynamic_classes/'))
        Q.simulate_until_max_time()
        L = Q.get_all_individuals()
        drl = []
        for dr in L[0].data_records[1]:
            drl.append((dr.customer_class, dr.service_time))
        self.assertEqual(drl, [(1, 10.0), (1, 10.0), (0, 5.0), (1, 10.0)])

    def test_simulate_until_deadlock_method(self):
        seed(3)
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_deadlock_sim/'))
        times = Q.simulate_until_deadlock()
        self.assertEqual(round(times[((0, 0), (0, 0))], 8), 9.09939457)

    def test_detect_deadlock_method(self):
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        nodes = ['A', 'B', 'C', 'D', 'E']
        connections = [('A', 'D'), ('A', 'B'), ('B', 'E'), ('C', 'B'), ('E', 'C')]
        for nd in nodes:
            Q.digraph.add_node(nd)
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), True)

        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        nodes = ['A', 'B', 'C', 'D']
        connections = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D')]
        for nd in nodes:
            Q.digraph.add_node(nd)
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), False)

        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        nodes = ['A', 'B']
        for nd in nodes:
            Q.digraph.add_node(nd)
        self.assertEqual(Q.detect_deadlock(), False)
        connections = [('A', 'A')]
        for cnctn in connections:
            Q.digraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.detect_deadlock(), True)