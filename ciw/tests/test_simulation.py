import unittest
import ciw
from random import seed
from hypothesis import given
from hypothesis.strategies import floats, integers, random_module
import os
from numpy import random as nprandom
from numpy import mean
from decimal import Decimal
import networkx as nx
import csv


def set_seed(x):
    seed(x)
    nprandom.seed(x)

class TestSimulation(unittest.TestCase):

    def test_repr_method(self):
        N1 = ciw.create_network(
          'ciw/tests/testing_parameters/params.yml')
        Q1 = ciw.Simulation(N1)
        self.assertEqual(str(Q1), 'Simulation')

        N2 = ciw.create_network(
          'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(N2, name='My special simulation instance!')
        self.assertEqual(str(Q), 'My special simulation instance!')

    def test_init_method(self):
        N = ciw.create_network(
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

        Q = ciw.Simulation(ciw.create_network(params))

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
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params.yml'))
        i = 0
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i += 1
        self.assertEqual(str(Q.find_next_active_node()), 'Arrival Node')

        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params.yml'))
        i = 10
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i -= 1
        self.assertEqual(str(Q.find_next_active_node()), 'Node 4')

    def test_simulate_until_max_time_method(self):
        set_seed(2)
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params.yml'))
        Q.simulate_until_max_time(150)
        L = Q.get_all_records()
        self.assertEqual(round(
            L[300].service_start_date, 8), 2.43854666)

        set_seed(60)
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_change_class.yml'))
        Q.simulate_until_max_time(50)
        L = Q.get_all_individuals()
        drl = []
        for dr in L[0].data_records:
            drl.append((dr.customer_class, dr.service_time))
        self.assertEqual(drl, [(1, 10.0), (0, 5.0), (0, 5.0)])

    def test_simulate_until_deadlock_method(self):
        set_seed(3)
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector='StateDigraph')
        Q.simulate_until_deadlock()
        self.assertEqual(round(Q.times_to_deadlock[((0, 0), (0, 0))], 8), 23.92401469)

    def test_detect_deadlock_method(self):
        Q = ciw.Simulation(ciw.create_network(
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

        Q = ciw.Simulation(ciw.create_network(
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

        Q = ciw.Simulation(ciw.create_network(
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
        Q = ciw.Simulation(ciw.create_network(
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

        Q = ciw.Simulation(ciw.create_network(params))
        Q.simulate_until_max_time(5)
        recs = Q.get_all_records()
        waits = [rec.waiting_time for rec in recs]
        self.assertEqual(sum(waits), 0.0)

    def test_writing_data_files(self):
        expected_headers = ['I.D. Number',
                            'Customer Class',
                            'Node',
                            'Arrival Date',
                            'Waiting Time',
                            'Service Start Date',
                            'Service Time',
                            'Service End Date',
                            'Time Blocked',
                            'Exit Date',
                            'Destination',
                            'Queue Size at Arrival',
                            'Queue Size at Departure']
        Q = ciw.Simulation(ciw.create_network(
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
        data = []
        data_file = open('ciw/tests/testing_parameters/data.csv', 'r')
        rdr = csv.reader(data_file)
        for row in rdr:
            data.append(row)
        data_file.close()
        self.assertEqual(data[0], expected_headers)
        self.assertEqual(len(data[0]), len(ciw.simulation.Record._fields))
        os.remove('ciw/tests/testing_parameters/data.csv')

        Q = ciw.Simulation(ciw.create_network(
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
        data = []
        data_file = open('ciw/tests/testing_parameters/data_1.csv', 'r')
        rdr = csv.reader(data_file)
        for row in rdr:
            data.append(row)
        data_file.close()
        self.assertNotEqual(data[0], expected_headers)
        os.remove('ciw/tests/testing_parameters/data_1.csv')

        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_mm1.yml'))
        Q.simulate_until_max_time(50)
        files = [x for x in os.walk(
            'ciw/tests/testing_parameters/')][0][2]
        self.assertEqual('data_2.csv' in files, False)
        Q.write_records_to_file(
            'ciw/tests/testing_parameters/data_2.csv', True)
        files = [x for x in os.walk(
            'ciw/tests/testing_parameters/')][0][2]
        self.assertEqual('data_2.csv' in files, True)
        data = []
        data_file = open('ciw/tests/testing_parameters/data_2.csv', 'r')
        rdr = csv.reader(data_file)
        for row in rdr:
            data.append(row)
        data_file.close()
        self.assertEqual(data[0], expected_headers)
        self.assertEqual(len(data[0]), len(ciw.simulation.Record._fields))
        os.remove('ciw/tests/testing_parameters/data_2.csv')


    def test_simultaneous_events_example(self):
        # This should yield 3 or 2 customers finishing service.
        # Due to randomly choosing the order of events, the seed has
        # a big affect on this.

        params = {'Arrival_distributions': [['Deterministic', 10.0], 'NoArrivals'],
                  'Service_distributions': [['Deterministic', 5.0], ['Deterministic', 5.0]],
                  'Transition_matrices': [[1.0, 0.0], [0.0, 0.0]],
                  'Number_of_servers': [2, 1]}


        set_seed(36)
        Q = ciw.Simulation(ciw.create_network(params))
        Q.simulate_until_max_time(36)
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 2)
        self.assertTrue(all([x[6] == 5.0 for x in recs[1:]]))

        set_seed(40)
        Q = ciw.Simulation(ciw.create_network(params))
        Q.simulate_until_max_time(36)
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 3)
        self.assertTrue(all([x[6] == 5.0 for x in recs[1:]]))

        completed_inds = []
        for _ in range(1000):
            Q = ciw.Simulation(ciw.create_network(params))
            Q.simulate_until_max_time(36)
            inds = Q.get_all_individuals()
            completed_inds.append(len(inds))
        self.assertAlmostEqual(completed_inds.count(2) / float(1000), 1 / 4.0, places=1)

    def test_exactness(self):
        params = {'Arrival_distributions': [['Exponential', 20]],
                  'Service_distributions': [['Deterministic', 0.01]],
                  'Transition_matrices': [[0.0]],
                  'Number_of_servers': ['server_schedule'],
                  'server_schedule': [[0.5, 0], [0.55, 1], [3.0, 0]]}

        set_seed(777)
        Q = ciw.Simulation(ciw.create_network(params))
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        mod_service_starts = [obs%3 for obs in [r[5] for r in recs]]
        self.assertNotEqual(set(mod_service_starts), set([0.50, 0.51, 0.52, 0.53, 0.54]))

        set_seed(777)
        Q = ciw.Simulation(ciw.create_network(params), exact=14)
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        mod_service_starts = [obs%3 for obs in [r[5] for r in recs]]
        expected_set = set([Decimal(k) for k in ['0.50', '0.51', '0.52', '0.53', '0.54']])
        self.assertEqual(set(mod_service_starts), expected_set)

    def test_setting_classes(self):
        class DummyNode(ciw.Node):
            pass

        class DummyArrivalNode(ciw.ArrivalNode):
            pass

        params = {'Arrival_distributions': [['Exponential', 20]],
                  'Service_distributions': [['Deterministic', 0.01]],
                  'Transition_matrices': [[0.0]],
                  'Number_of_servers': ['server_schedule'],
                  'server_schedule': [[0.5, 0], [0.55, 1], [3.0, 0]]}
        Q = ciw.Simulation(ciw.create_network(params))
        self.assertEqual(Q.NodeType, ciw.Node)
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)

        Q.set_classes(None, None)
        self.assertEqual(Q.NodeType, ciw.Node)
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)

        Q.set_classes(DummyNode, None)
        self.assertEqual(Q.NodeType, DummyNode)
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)

        Q.set_classes(None, DummyArrivalNode)
        self.assertEqual(Q.NodeType, ciw.Node)
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)

        Q.set_classes(DummyNode, DummyArrivalNode)
        self.assertEqual(Q.NodeType, DummyNode)
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)

    def test_setting_classes_in_init(self):
        class DummyNode(ciw.Node):
            pass

        class DummyArrivalNode(ciw.ArrivalNode):
            pass

        params = {'Arrival_distributions': [['Exponential', 20]],
                  'Service_distributions': [['Deterministic', 0.01]],
                  'Transition_matrices': [[0.0]],
                  'Number_of_servers': ['server_schedule'],
                  'server_schedule': [[0.5, 0], [0.55, 1], [3.0, 0]]}

        Q = ciw.Simulation(ciw.create_network(params), node_class=None, arrival_node_class=None)
        self.assertEqual(Q.NodeType, ciw.Node)
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[0], ciw.ArrivalNode)
        self.assertFalse(isinstance(Q.nodes[1], DummyNode))
        self.assertFalse(isinstance(Q.nodes[0], DummyArrivalNode))

        Q = ciw.Simulation(ciw.create_network(params), node_class=DummyNode, arrival_node_class=None)
        self.assertEqual(Q.NodeType, DummyNode)
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[1], DummyNode)
        self.assertIsInstance(Q.nodes[0], ciw.ArrivalNode)
        self.assertFalse(isinstance(Q.nodes[0], DummyArrivalNode))

        Q = ciw.Simulation(ciw.create_network(params), node_class=None, arrival_node_class=DummyArrivalNode)
        self.assertEqual(Q.NodeType, ciw.Node)
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[0], DummyArrivalNode)
        self.assertFalse(isinstance(Q.nodes[1], DummyNode))

        Q = ciw.Simulation(ciw.create_network(params), node_class=DummyNode, arrival_node_class=DummyArrivalNode)
        self.assertEqual(Q.NodeType, DummyNode)
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertIsInstance(Q.nodes[1], DummyNode)
        self.assertIsInstance(Q.nodes[0], DummyArrivalNode)

    def test_get_all_records(self):
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params.yml'))
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        for row in recs:
            self.assertIsInstance(row, ciw.simulation.Record)
            self.assertEqual(len(row), len(ciw.simulation.Record._fields))

    def test_namedtuple_record(self):
        expected_fields = ('id_number', 'customer_class', 'node', 'arrival_date', 'waiting_time', 'service_start_date', 'service_time', 'service_end_date', 'time_blocked', 'exit_date', 'destination', 'queue_size_at_arrival', 'queue_size_at_departure')
        self.assertEqual(ciw.simulation.Record._fields, expected_fields)
        self.assertEqual(ciw.simulation.Record.__name__, 'Record')

    def test_priority_output(self):

        params_dict = {'Arrival_distributions': {'Class 0': [['Deterministic', 1.0]],
                                                 'Class 1': [['Deterministic', 1.0]]},
                       'Service_distributions': {'Class 0': [['Deterministic', 0.75]],
                                                 'Class 1': [['Deterministic', 0.75]]},
                       'Transition_matrices': {'Class 0': [[0.0]],
                                               'Class 1': [[0.0]]},
                       'Number_of_servers': [1],
                       'Priority_classes': {'Class 0': 0,
                                            'Class 1': 1}
                       }

        set_seed(36)
        Q = ciw.Simulation(ciw.create_network(params_dict))
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        waits = [sum([r.waiting_time for r in recs if r.customer_class == cls]) for cls in range(2)]
        # Because of high traffic intensity: the low
        # priority individuals have a large wait
        self.assertEqual(sorted(waits), [15, 249])

        params_dict = {'Arrival_distributions': {'Class 0': [['Deterministic', 1.0]],
                                                 'Class 1': [['Deterministic', 1.0]]},
                       'Service_distributions': {'Class 0': [['Deterministic', 0.75]],
                                                 'Class 1': [['Deterministic', 0.75]]},
                       'Transition_matrices': {'Class 0': [[0.0]],
                                               'Class 1': [[0.0]]},
                       'Number_of_servers': [1]
                       }

        set_seed(36)
        Q = ciw.Simulation(ciw.create_network(params_dict))
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        waits = [sum([r.waiting_time for r in recs if r.customer_class == cls]) for cls in range(2)]
        # Both total waits are now comparable. Total wait is higher
        # because more more individuals have gone through the system.
        self.assertEqual(sorted(waits), [264, 272])

    def test_priority_system_compare_literature(self):
        params_dict = {
               'Arrival_distributions': {'Class 0': [['Exponential', 0.2]],
                                         'Class 1': [['Exponential', 0.6]]},
               'Service_distributions': {'Class 0': [['Exponential', 1.0]],
                                         'Class 1': [['Exponential', 1.0]]},
               'Transition_matrices': {'Class 0': [[0.0]],
                                       'Class 1': [[0.0]]},
               'Number_of_servers': [1],
               'Priority_classes': {'Class 0': 0,
                                    'Class 1': 1}

               }
        Q = ciw.Simulation(ciw.create_network(params_dict))
        # Results expected from analytical queueing theory are:
        # expected_throughput_class0 = 2.0, and expected_throughput_class1 = 6.0
        # Althought these results seem far from the theoretical, longer runs and
        # more runs give the desired results. A compromise was reached here to
        # reduce test suite runtime.
        throughput_class0 = []
        throughput_class1 = []

        set_seed(3231)
        for iteration in range(60):
            Q.simulate_until_max_time(200)
            recs = Q.get_all_records()
            throughput_class0.append(mean([r.waiting_time + r.service_time for r in recs if r.customer_class==0 if r.arrival_date > 70]))
            throughput_class1.append(mean([r.waiting_time + r.service_time for r in recs if r.customer_class==1 if r.arrival_date > 70]))

        self.assertEqual(round(mean(throughput_class0), 5), 2.12461)
        self.assertEqual(round(mean(throughput_class1), 5), 5.34970)

    def test_balking(self):
        def my_balking_function(n):
            if n < 3:
                return 0.0
            return 1.0

        params_dict = {
            'Arrival_distributions': [['Deterministic', 5.0]],
            'Service_distributions': [['Deterministic', 21.0]],
            'Transition_matrices': [[0.0]],
            'Number_of_servers': [1],
            'Balking_functions': [my_balking_function]
        }

        Q = ciw.Simulation(ciw.create_network(params_dict))
        Q.simulate_until_max_time(51)
        recs = Q.get_all_records()
        self.assertEqual(Q.balked_dict, {1:{0:[20.0, 25.0, 35.0, 40.0, 45.0]}})
        self.assertEqual([r.id_number for r in recs], [1, 2])
        self.assertEqual([r.arrival_date for r in recs], [5.0, 10.0])
        self.assertEqual([r.waiting_time for r in recs], [0.0, 16.0])
        self.assertEqual([r.service_start_date for r in recs], [5.0, 26.0])
        self.assertEqual([r.service_end_date for r in recs], [26.0, 47.0])


        params_dict = {
            'Arrival_distributions': [['Deterministic', 5.0], ['Deterministic', 23.0]],
            'Service_distributions': [['Deterministic', 21.0], ['Deterministic', 1.5]],
            'Transition_matrices': [[0.0, 0.0], [1.0, 0.0]],
            'Number_of_servers': [1, 1],
            'Balking_functions': [my_balking_function, None]
        }

        Q = ciw.Simulation(ciw.create_network(params_dict))
        Q.simulate_until_max_time(51)
        recs = Q.get_all_records()
        self.assertEqual(Q.balked_dict, {1:{0:[20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]}, 2:{0:[]}})
        self.assertEqual(sorted([r.id_number for r in recs]), [1, 2, 5, 11])
        self.assertEqual(sorted([r.arrival_date for r in recs]), [5.0, 10.0, 23.0, 46.0])
        self.assertEqual(sorted([r.waiting_time for r in recs]), [0.0, 0.0, 0.0, 16.0])
        self.assertEqual(sorted([r.service_start_date for r in recs]), [5.0, 23.0, 26.0, 46.0])
        self.assertEqual(sorted([r.service_end_date for r in recs]), [24.5, 26.0, 47.0, 47.5])