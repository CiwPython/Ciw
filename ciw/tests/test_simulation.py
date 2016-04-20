import unittest
import ciw
from random import seed
from hypothesis import given
from hypothesis.strategies import floats, integers, lists, random_module
import os
from numpy import random as nprandom
from decimal import Decimal
import networkx as nx

def set_seed(x):
    seed(x)
    nprandom.seed(x)

class TestSimulation(unittest.TestCase):

    def test_repr_method(self):
        N1 = ciw.Network_From_File(
          'ciw/tests/testing_parameters/params.yml')
        Q1 = ciw.Simulation(N1)
        self.assertEqual(str(Q1), 'Simulation')

        N2 = ciw.Network_From_File(
          'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(N2, name='My special simulation instance!')
        self.assertEqual(str(Q), 'My special simulation instance!')

    def test_init_method(self):
        N = ciw.Network_From_File(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(N)

        self.assertEqual(len(Q.transitive_nodes), 4)
        self.assertEqual(len(Q.nodes), 6)
        self.assertEqual(str(Q.nodes[0]), 'Arrival Node')
        self.assertEqual(str(Q.nodes[-1]), 'Exit Node')
        self.assertEqual([str(n) for n in Q.transitive_nodes],
            ['Node 1', 'Node 2', 'Node 3', 'Node 4'])
        self.assertEqual(len(Q.inter_arrival_times), 4)
        self.assertEqual(len(Q.inter_arrival_times[1]), 3)
        self.assertEqual(len(Q.service_times), 4)
        self.assertEqual(len(Q.service_times[1]), 3)


    @given(arrival_rate=floats(min_value=0.1, max_value=100),
           service_rate=floats(min_value=0.1, max_value=100),
           number_of_servers=integers(min_value=1, max_value=30),
           rm=random_module())
    def test_init_method_h(self,
                           arrival_rate,
                           service_rate,
                           number_of_servers,
                           rm):
        params = {'Arrival_distributions': [['Exponential', arrival_rate]],
                  'Service_distributions': [['Exponential', service_rate]],
                  'Number_of_servers': [number_of_servers],
                  'Transition_matrices': [[0.0]]}

        Q = ciw.Simulation(ciw.Network_From_Dictionary(params))
        
        self.assertEqual(len(Q.transitive_nodes), 1)
        self.assertEqual(len(Q.nodes), 3)
        self.assertEqual(str(Q.nodes[0]), 'Arrival Node')
        self.assertEqual(str(Q.nodes[-1]), 'Exit Node')
        self.assertEqual([str(n) for n in Q.transitive_nodes],
            ['Node 1'])
        self.assertEqual(len(Q.inter_arrival_times), 1)
        self.assertEqual(len(Q.inter_arrival_times[1]), 1)
        self.assertEqual(len(Q.service_times), 1)
        self.assertEqual(len(Q.service_times[1]), 1)
        self.assertEqual([str(obs) for obs in Q.nodes],
          ['Arrival Node', 'Node 1', 'Exit Node'])

    def test_find_next_active_node_method(self):
        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params.yml'))
        i = 0
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i += 1
        self.assertEqual(str(Q.find_next_active_node()), 'Arrival Node')

        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params.yml'))
        i = 10
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i -= 1
        self.assertEqual(str(Q.find_next_active_node()), 'Node 4')

    def test_simulate_until_max_time_method(self):
        set_seed(2)
        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params.yml'))
        Q.simulate_until_max_time(150)
        L = Q.get_all_individuals()
        self.assertEqual(round(
            L[300].data_records.values()[0][0].service_start_date, 8), 8.89002862)

        set_seed(60)
        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params_change_class.yml'))
        Q.simulate_until_max_time(50)
        L = Q.get_all_individuals()
        drl = []
        for dr in L[0].data_records[1]:
            drl.append((dr.customer_class, dr.service_time))
        self.assertEqual(drl, [(1, 10.0), (0, 5.0), (0, 5.0)])

    def test_simulate_until_deadlock_method(self):
        set_seed(3)
        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector='StateDigraph')
        Q.simulate_until_deadlock()
        self.assertEqual(round(Q.times_to_deadlock[((0, 0), (0, 0))], 8), 31.26985409)

    def test_detect_deadlock_method(self):
        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector='StateDigraph')
        nodes = ['A', 'B', 'C', 'D', 'E']
        connections = [('A', 'D'), ('A', 'B'), ('B', 'E'), ('C', 'B'), ('E', 'C')]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), True)

        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector='StateDigraph')
        nodes = ['A', 'B', 'C', 'D']
        connections = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D')]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), False)

        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector='StateDigraph')
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
        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params_mm1.yml'))
        self.assertEqual(Q.nodes[1].transition_row, [[0.0]])

    @given(arrival_rate=floats(min_value=0.1, max_value=10),
           service_rate=floats(min_value=0.1, max_value=10),
           rm=random_module())
    def test_mminf_node(self, arrival_rate, service_rate, rm):
        params = {'Arrival_distributions': [['Exponential', arrival_rate]],
                  'Service_distributions': [['Exponential', service_rate]],
                  'Number_of_servers': ['Inf'],
                  'Transition_matrices': [[0.0]]}

        Q = ciw.Simulation(ciw.Network_From_Dictionary(params))
        Q.simulate_until_max_time(5)
        inds = Q.get_all_individuals()
        waits = [ind.data_records[1][0].wait for ind in inds]
        self.assertEqual(sum(waits), 0.0)

    def test_writing_data_files(self):
        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params.yml'))
        Q.simulate_until_max_time(50)
        files = [x for x in os.walk(
            'ciw/tests/testing_parameters/')][0][2]
        self.assertEqual('data.csv' in files, False)
        Q.write_records_to_file(
            'ciw/tests/testing_parameters/data.csv')
        files = [x for x in os.walk(
            'ciw/tests/testing_parameters/')][0][2]
        self.assertEqual('data.csv' in files, True)
        os.remove('ciw/tests/testing_parameters/data.csv')

        Q = ciw.Simulation(ciw.Network_From_File(
            'ciw/tests/testing_parameters/params_mm1.yml'))
        Q.simulate_until_max_time(50)
        files = [x for x in os.walk(
            'ciw/tests/testing_parameters/')][0][2]
        self.assertEqual('data_1.csv' in files, False)
        Q.write_records_to_file(
            'ciw/tests/testing_parameters/data_1.csv', False)
        files = [x for x in os.walk(
            'ciw/tests/testing_parameters/')][0][2]
        self.assertEqual('data_1.csv' in files, True)
        os.remove('ciw/tests/testing_parameters/data_1.csv')

    def test_simultaneous_events_example(self):
        # This should yield 3 or 2 customers finishing service.
        # Due to randomly choosing the order of events, the seed has
        # a big affect on this.

        set_seed(73)
        params = {'Arrival_distributions': [['Deterministic', 10.0], 'NoArrivals'],
                  'Service_distributions': [['Deterministic', 5.0], ['Deterministic', 5.0]],
                  'Transition_matrices': [[1.0, 0.0], [0.0, 0.0]],
                  'Number_of_servers': [2, 1]}
        Q = ciw.Simulation(ciw.Network_From_Dictionary(params))
        Q.simulate_until_max_time(36)
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 2)
        self.assertTrue(all([x[6] == 5.0 for x in recs[1:]]))


        set_seed(74)
        params = {'Arrival_distributions': [['Deterministic', 10.0], 'NoArrivals'],
                  'Service_distributions': [['Deterministic', 5.0], ['Deterministic', 5.0]],
                  'Transition_matrices': [[1.0, 0.0], [0.0, 0.0]],
                  'Number_of_servers': [2, 1]}
        Q = ciw.Simulation(ciw.Network_From_Dictionary(params))
        Q.simulate_until_max_time(36)
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 3)
        self.assertTrue(all([x[6] == 5.0 for x in recs[1:]]))

    def test_exactness(self):
        set_seed(777)
        params = {'Arrival_distributions': [['Exponential', 20]],
                  'Service_distributions': [['Deterministic', 0.01]],
                  'Transition_matrices': [[0.0]],
                  'Number_of_servers': ['server_schedule'],
                  'server_schedule': [[0.5, 0], [0.55, 1], [3.0, 0]]}
        Q = ciw.Simulation(ciw.Network_From_Dictionary(params))
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records(headers=False)
        mod_service_starts = [obs%3 for obs in [r[5] for r in recs]]
        self.assertNotEqual(set(mod_service_starts), set([0.50, 0.51, 0.52, 0.53, 0.54]))

        set_seed(777)
        params = {'Arrival_distributions': [['Exponential', 20]],
                  'Service_distributions': [['Deterministic', 0.01]],
                  'Transition_matrices': [[0.0]],
                  'Number_of_servers': ['server_schedule'],
                  'server_schedule': [[0.5, 0], [0.55, 1], [3.0, 0]]}
        Q = ciw.Simulation(ciw.Network_From_Dictionary(params), exact=14)
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records(headers=False)
        mod_service_starts = [obs%3 for obs in [r[5] for r in recs]]
        expected_set = set([Decimal(k) for k in ['0.50', '0.51', '0.52', '0.53', '0.54']])
        self.assertEqual(set(mod_service_starts), expected_set)
