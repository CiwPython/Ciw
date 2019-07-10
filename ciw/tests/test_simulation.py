import unittest
import ciw
from hypothesis import given
from hypothesis.strategies import floats, integers, random_module
import os
from decimal import Decimal
import networkx as nx
import csv
from itertools import cycle


class TestSimulation(unittest.TestCase):
    def test_repr_method(self):
        N1 = ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml')
        Q1 = ciw.Simulation(N1)
        self.assertEqual(str(Q1), 'Simulation')

        N2 = ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(N2, name='My special simulation instance!')
        self.assertEqual(str(Q), 'My special simulation instance!')

    def test_init_method(self):
        N = ciw.create_network_from_yml(
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
        params = {'arrival_distributions': [ciw.dists.Exponential(arrival_rate)],
                  'service_distributions': [ciw.dists.Exponential(service_rate)],
                  'number_of_servers': [number_of_servers]}

        Q = ciw.Simulation(ciw.create_network(**params))

        self.assertEqual(len(Q.transitive_nodes), 1)
        self.assertEqual(len(Q.nodes), 3)
        self.assertEqual(str(Q.nodes[0]), 'Arrival Node')
        self.assertEqual(str(Q.nodes[-1]), 'Exit Node')
        self.assertEqual([str(n) for n in Q.transitive_nodes], ['Node 1'])
        self.assertEqual(len(Q.inter_arrival_times), 1)
        self.assertEqual(len(Q.inter_arrival_times[1]), 1)
        self.assertEqual(len(Q.service_times), 1)
        self.assertEqual(len(Q.service_times[1]), 1)
        self.assertEqual([str(obs) for obs in Q.nodes],
          ['Arrival Node', 'Node 1', 'Exit Node'])

    def test_find_next_active_node_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        i = 0
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i += 1
        self.assertEqual(str(Q.find_next_active_node()), 'Arrival Node')

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        i = 10
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i -= 1
        self.assertEqual(str(Q.find_next_active_node()), 'Node 4')

    def test_simulate_until_max_time_method(self):
        ciw.seed(2)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        Q.simulate_until_max_time(150)
        L = Q.get_all_records()
        self.assertEqual(round(
            L[300].service_start_date, 8), 1.92388895)

        ciw.seed(60)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_change_class.yml'))
        Q.simulate_until_max_time(50)
        L = Q.get_all_individuals()
        drl = []
        for dr in L[0].data_records:
            drl.append((dr.customer_class, dr.service_time))
        self.assertEqual(drl, [(1, 10.0), (0, 5.0), (0, 5.0)])

    def test_simulate_until_max_time_with_pbar_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        Q.simulate_until_max_time(150, progress_bar=True)
        self.assertEqual(Q.progress_bar.total, 150)
        self.assertEqual(Q.progress_bar.n, 150)

    def test_simulate_until_max_customers_finish(self):
        params = {
            'arrival_distributions': [ciw.dists.Exponential(1.0)],
            'service_distributions': [ciw.dists.Exponential(0.5)],
            'number_of_servers': [1],
            'routing': [[0.0]],
            'queue_capacities': [3]
        }
        N = ciw.create_network(**params)

        # Test default method, 'Finish'
        ciw.seed(2)
        Q1 = ciw.Simulation(N)
        Q1.simulate_until_max_customers(10, method='Finish')
        self.assertEqual(Q1.nodes[-1].number_of_individuals, 10)
        self.assertEqual(len(Q1.nodes[-1].all_individuals), 10)

        # Test 'Finish' method
        ciw.seed(2)
        Q2 = ciw.Simulation(N)
        Q2.simulate_until_max_customers(10)
        self.assertEqual(Q2.nodes[-1].number_of_individuals, 10)
        self.assertEqual(len(Q2.nodes[-1].all_individuals), 10)

        next_active_node = Q2.find_next_active_node()
        end_time_finish = next_active_node.next_event_date

        # Test 'Arrive' method
        ciw.seed(2)
        Q3 = ciw.Simulation(N)
        Q3.simulate_until_max_customers(10, method='Arrive')
        self.assertEqual(Q3.nodes[0].number_of_individuals, 10)
        all_inds = sum([len(nd.all_individuals) for nd in Q3.nodes[1:]])
        number_of_losses = sum(
            [len(Q3.rejection_dict[nd][cls]) for nd in
            range(1, Q3.network.number_of_nodes + 1) for cls in
            range(Q3.network.number_of_classes)])
        self.assertEqual(all_inds + number_of_losses, 10)
        self.assertEqual(number_of_losses, 5)

        next_active_node = Q3.find_next_active_node()
        end_time_arrive = next_active_node.next_event_date

        # Test 'Accept' method
        ciw.seed(2)
        Q4 = ciw.Simulation(N)
        Q4.simulate_until_max_customers(10, method='Accept')
        self.assertEqual(Q4.nodes[0].number_accepted_individuals, 10)
        all_inds = sum([len(nd.all_individuals) for nd in Q4.nodes[1:]])
        self.assertEqual(all_inds, 10)

        next_active_node = Q4.find_next_active_node()
        end_time_accept = next_active_node.next_event_date

        # Assert that finish time of finish > accept > arrive
        self.assertGreater(end_time_finish, end_time_accept)
        self.assertGreater(end_time_accept, end_time_arrive)
        self.assertGreater(end_time_finish, end_time_arrive)

        # Test raise error if anything else
        ciw.seed(2)
        Q5 = ciw.Simulation(N)
        self.assertRaises(ValueError,
            lambda x: Q5.simulate_until_max_customers(10, method=x),
            'Jibberish')

    def test_simulate_until_max_customers_with_pbar_method(self):
        N = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        max_custs = 250

        ciw.seed(1)
        Q1 = ciw.Simulation(N)
        Q1.simulate_until_max_customers(max_custs, progress_bar=True, method='Finish')
        self.assertEqual(Q1.progress_bar.total, max_custs)
        self.assertEqual(Q1.progress_bar.n, max_custs)

        ciw.seed(1)
        Q2 = ciw.Simulation(N)
        Q2.simulate_until_max_customers(max_custs, progress_bar=True, method='Arrive')
        self.assertEqual(Q2.progress_bar.total, max_custs)
        self.assertEqual(Q2.progress_bar.n, max_custs)

        ciw.seed(1)
        Q3 = ciw.Simulation(N)
        Q3.simulate_until_max_customers(max_custs, progress_bar=True, method='Accept')
        self.assertEqual(Q3.progress_bar.total, max_custs)
        self.assertEqual(Q3.progress_bar.n, max_custs)

    def test_simulate_until_deadlock_method(self):
        ciw.seed(3)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector=ciw.deadlock.StateDigraph(),
             tracker=ciw.trackers.NaiveTracker())
        Q.simulate_until_deadlock()
        self.assertEqual(round(Q.times_to_deadlock[((0, 0), (0, 0))], 8), 53.88526441)

    def test_detect_deadlock_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector=ciw.deadlock.StateDigraph())
        nodes = ['A', 'B', 'C', 'D', 'E']
        connections = [('A', 'D'), ('A', 'B'), ('B', 'E'), ('C', 'B'), ('E', 'C')]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), True)

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector=ciw.deadlock.StateDigraph())
        nodes = ['A', 'B', 'C', 'D']
        connections = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D')]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), False)

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
             deadlock_detector=ciw.deadlock.StateDigraph())
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
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_mm1.yml'))
        self.assertEqual(Q.nodes[1].transition_row, [[0.0]])

    @given(arrival_rate=floats(min_value=0.1, max_value=10),
           service_rate=floats(min_value=0.1, max_value=10),
           rm=random_module())
    def test_mminf_node(self, arrival_rate, service_rate, rm):
        params = {'arrival_distributions': [ciw.dists.Exponential(arrival_rate)],
                  'service_distributions': [ciw.dists.Exponential(service_rate)],
                  'number_of_servers': [float('inf')],
                  'routing': [[0.0]]}

        Q = ciw.Simulation(ciw.create_network(**params))
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
        Q = ciw.Simulation(ciw.create_network_from_yml(
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
        self.assertEqual(len(data[0]), len(ciw.data_record.DataRecord._fields))
        os.remove('ciw/tests/testing_parameters/data.csv')

        Q = ciw.Simulation(ciw.create_network_from_yml(
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

        Q = ciw.Simulation(ciw.create_network_from_yml(
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
        self.assertEqual(len(data[0]), len(ciw.data_record.DataRecord._fields))
        os.remove('ciw/tests/testing_parameters/data_2.csv')

    def test_simultaneous_events_example(self):
        # This should yield 3 or 2 customers finishing service.
        # Due to randomly choosing the order of events, the seed has
        # a big affect on this.
        params = {'arrival_distributions': [ciw.dists.Deterministic(10.0),
                                            ciw.dists.NoArrivals()],
                  'service_distributions': [ciw.dists.Deterministic(5.0),
                                            ciw.dists.Deterministic(5.0)],
                  'routing': [[1.0, 0.0], [0.0, 0.0]],
                  'number_of_servers': [2, 1]}

        ciw.seed(36)
        Q = ciw.Simulation(ciw.create_network(**params))
        Q.simulate_until_max_time(36)
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 3)
        self.assertTrue(all([x[6] == 5.0 for x in recs[1:]]))

        ciw.seed(35)
        Q = ciw.Simulation(ciw.create_network(**params))
        Q.simulate_until_max_time(36)
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 2)
        self.assertTrue(all([x[6] == 5.0 for x in recs[1:]]))

        completed_inds = []
        for _ in range(1000):
            Q = ciw.Simulation(ciw.create_network(**params))
            Q.simulate_until_max_time(36)
            inds = Q.get_all_individuals()
            completed_inds.append(len(inds))
        self.assertAlmostEqual(
            completed_inds.count(2) / float(1000), 1 / 4.0, places=1)

    def test_exactness(self):
        params = {'arrival_distributions': [ciw.dists.Exponential(20)],
                  'service_distributions': [ciw.dists.Deterministic(0.01)],
                  'routing': [[0.0]],
                  'number_of_servers': [[[0, 0.5], [1, 0.55], [0, 3.0]]]
                  }
        ciw.seed(777)
        Q = ciw.Simulation(ciw.create_network(**params))
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        mod_service_starts = [obs%3 for obs in [r[5] for r in recs]]
        self.assertNotEqual(set(mod_service_starts),
                            set([0.50, 0.51, 0.52, 0.53, 0.54]))

        ciw.seed(777)
        Q = ciw.Simulation(ciw.create_network(**params), exact=14)
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        mod_service_starts = [obs%3 for obs in [r[5] for r in recs]]
        expected_set = set([Decimal(k) for k in
            ['0.50', '0.51', '0.52', '0.53', '0.54']])
        self.assertEqual(set(mod_service_starts), expected_set)

    def test_setting_classes(self):
        class DummyNode(ciw.Node):
            pass

        class DummyArrivalNode(ciw.ArrivalNode):
            pass

        params = {'arrival_distributions': [ciw.dists.Exponential(20)],
                  'service_distributions': [ciw.dists.Deterministic(0.01)],
                  'routing': [[0.0]],
                  'number_of_servers': [[[0, 0.5], [1, 0.55], [0, 3.0]]]
                  }
        Q = ciw.Simulation(ciw.create_network(**params))
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

        params = {'arrival_distributions': [ciw.dists.Exponential(20)],
                  'service_distributions': [ciw.dists.Deterministic(0.01)],
                  'routing': [[0.0]],
                  'number_of_servers': [[[0, 0.5], [1, 0.55], [0, 3.0]]]
                  }
        Q = ciw.Simulation(ciw.create_network(**params),
            node_class=None, arrival_node_class=None)
        self.assertEqual(Q.NodeType, ciw.Node)
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[0], ciw.ArrivalNode)
        self.assertFalse(isinstance(Q.nodes[1], DummyNode))
        self.assertFalse(isinstance(Q.nodes[0], DummyArrivalNode))

        Q = ciw.Simulation(ciw.create_network(**params),
            node_class=DummyNode, arrival_node_class=None)
        self.assertEqual(Q.NodeType, DummyNode)
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[1], DummyNode)
        self.assertIsInstance(Q.nodes[0], ciw.ArrivalNode)
        self.assertFalse(isinstance(Q.nodes[0], DummyArrivalNode))

        Q = ciw.Simulation(ciw.create_network(**params),
            node_class=None, arrival_node_class=DummyArrivalNode)
        self.assertEqual(Q.NodeType, ciw.Node)
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[0], DummyArrivalNode)
        self.assertFalse(isinstance(Q.nodes[1], DummyNode))

        Q = ciw.Simulation(ciw.create_network(**params),
            node_class=DummyNode, arrival_node_class=DummyArrivalNode)
        self.assertEqual(Q.NodeType, DummyNode)
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertIsInstance(Q.nodes[1], DummyNode)
        self.assertIsInstance(Q.nodes[0], DummyArrivalNode)

    def test_get_all_records(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        for row in recs:
            self.assertIsInstance(row, ciw.data_record.DataRecord)
            self.assertEqual(len(row), len(ciw.data_record.DataRecord._fields))

    def test_namedtuple_record(self):
        expected_fields = ('id_number',
            'customer_class',
            'node',
            'arrival_date',
            'waiting_time',
            'service_start_date',
            'service_time',
            'service_end_date',
            'time_blocked',
            'exit_date',
            'destination',
            'queue_size_at_arrival',
            'queue_size_at_departure')
        self.assertEqual(ciw.data_record.DataRecord._fields, expected_fields)
        self.assertEqual(ciw.data_record.DataRecord.__name__, 'Record')

    def test_priority_output(self):
        params_dict = {'arrival_distributions': {'Class 0': [ciw.dists.Deterministic(1.0)],
                                                 'Class 1': [ciw.dists.Deterministic(1.0)]},
                       'service_distributions': {'Class 0': [ciw.dists.Deterministic(0.75)],
                                                 'Class 1': [ciw.dists.Deterministic(0.75)]},
                       'routing': {'Class 0': [[0.0]],
                                   'Class 1': [[0.0]]},
                       'number_of_servers': [1],
                       'priority_classes': {'Class 0': 0,
                                            'Class 1': 1}
                       }

        ciw.seed(36)
        Q = ciw.Simulation(ciw.create_network(**params_dict))
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        waits = [sum([r.waiting_time for r in recs if r.customer_class == cls]) for cls in range(2)]
        # Because of high traffic intensity: the low
        # priority individuals have a large wait
        self.assertEqual(sorted(waits), [18.75, 245.25])

        params_dict = {'arrival_distributions': {'Class 0': [ciw.dists.Deterministic(1.0)],
                                                 'Class 1': [ciw.dists.Deterministic(1.0)]},
                       'service_distributions': {'Class 0': [ciw.dists.Deterministic(0.75)],
                                                 'Class 1': [ciw.dists.Deterministic(0.75)]},
                       'routing': {'Class 0': [[0.0]],
                                   'Class 1': [[0.0]]},
                       'number_of_servers': [1]
                       }

        ciw.seed(36)
        Q = ciw.Simulation(ciw.create_network(**params_dict))
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        waits = [sum([r.waiting_time for r in
            recs if r.customer_class == cls]) for cls in range(2)]
        # Both total waits are now comparable. Total wait is higher
        # because more more individuals have gone through the system.
        self.assertEqual(sorted(waits), [264, 272])

    def test_priority_system_compare_literature(self):
        params_dict = {
               'arrival_distributions': {'Class 0': [ciw.dists.Exponential(0.2)],
                                         'Class 1': [ciw.dists.Exponential(0.6)]},
               'service_distributions': {'Class 0': [ciw.dists.Exponential(1.0)],
                                         'Class 1': [ciw.dists.Exponential(1.0)]},
               'routing': {'Class 0': [[0.0]],
                           'Class 1': [[0.0]]},
               'number_of_servers': [1],
               'priority_classes': {'Class 0': 0,
                                    'Class 1': 1}

               }
        # Results expected from analytical queueing theory are:
        # expected_throughput_class0 = 2.0, and expected_throughput_class1 = 6.0
        throughput_class0 = []
        throughput_class1 = []

        ciw.seed(3231)
        for iteration in range(80):
            Q = ciw.Simulation(ciw.create_network(**params_dict))
            Q.simulate_until_max_time(400)
            recs = Q.get_all_records()
            throughput_c0 = [r.waiting_time + r.service_time for
                r in recs if r.customer_class==0 if r.arrival_date > 100]
            throughput_c1 = [r.waiting_time + r.service_time for
                r in recs if r.customer_class==1 if r.arrival_date > 100]
            throughput_class0.append(sum(throughput_c0)/len(throughput_c0))
            throughput_class1.append(sum(throughput_c1)/len(throughput_c1))

        self.assertEqual(round(sum(throughput_class0)/80.0, 5), 2.02767)
        self.assertEqual(round(sum(throughput_class1)/80.0, 5), 5.39739)

    def test_baulking(self):
        def my_baulking_function(n):
            if n < 3:
                return 0.0
            return 1.0

        params_dict = {
            'arrival_distributions': [ciw.dists.Deterministic(5.0)],
            'service_distributions': [ciw.dists.Deterministic(21.0)],
            'number_of_servers': [1],
            'baulking_functions': [my_baulking_function]
        }

        Q = ciw.Simulation(ciw.create_network(**params_dict))
        Q.simulate_until_max_time(51)
        recs = Q.get_all_records()
        self.assertEqual(Q.baulked_dict, {1:{0:[20.0, 25.0, 35.0, 40.0, 45.0]}})
        self.assertEqual([r.id_number for r in recs], [1, 2])
        self.assertEqual([r.arrival_date for r in recs], [5.0, 10.0])
        self.assertEqual([r.waiting_time for r in recs], [0.0, 16.0])
        self.assertEqual([r.service_start_date for r in recs], [5.0, 26.0])
        self.assertEqual([r.service_end_date for r in recs], [26.0, 47.0])

        params_dict = {
            'arrival_distributions': [ciw.dists.Deterministic(5.0),
                                      ciw.dists.Deterministic(23.0)],
            'service_distributions': [ciw.dists.Deterministic(21.0),
                                      ciw.dists.Deterministic(1.5)],
            'routing': [[0.0, 0.0], [1.0, 0.0]],
            'number_of_servers': [1, 1],
            'baulking_functions': [my_baulking_function, None]
        }

        Q = ciw.Simulation(ciw.create_network(**params_dict))
        Q.simulate_until_max_time(51)
        recs = Q.get_all_records()
        self.assertEqual(Q.baulked_dict,
            {1:{0:[20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]}, 2:{0:[]}})
        self.assertEqual(sorted([r.id_number for r in recs]),
            [1, 2, 5, 11])
        self.assertEqual(sorted([r.arrival_date for r in recs]),
            [5.0, 10.0, 23.0, 46.0])
        self.assertEqual(sorted([r.waiting_time for r in recs]),
            [0.0, 0.0, 0.0, 16.0])
        self.assertEqual(sorted([r.service_start_date for r in recs]),
            [5.0, 23.0, 26.0, 46.0])
        self.assertEqual(sorted([r.service_end_date for r in recs]),
            [24.5, 26.0, 47.0, 47.5])

    def test_prioritys_with_classchanges(self):
        params = {
            'arrival_distributions': {'Class 0': [ciw.dists.Exponential(0.5),
                                                  ciw.dists.Exponential(0.5)],
                                      'Class 1': [ciw.dists.Exponential(0.5),
                                                  ciw.dists.Exponential(0.5)]},
            'service_distributions': {'Class 0': [ciw.dists.Uniform(0.9, 1.1),
                                                  ciw.dists.Uniform(0.9, 1.1)],
                                      'Class 1': [ciw.dists.Uniform(0.9, 1.1),
                                                  ciw.dists.Uniform(0.9, 1.1)]},
            'number_of_servers': [1, 1],
            'routing': {'Class 0': [[0.0, 1.0],
                                    [1.0, 0.0]],
                        'Class 1': [[0.0, 1.0],
                                    [1.0, 0.0]]},
            'priority_classes': {'Class 1': 0,
                                 'Class 0': 1},
            'class_change_matrices': {'Node 1': [[0.0, 1.0],
                                                 [1.0, 0.0]],
                                      'Node 2': [[0.0, 1.0],
                                                 [1.0, 0.0]]}
        }

        ciw.seed(1)
        N = ciw.create_network(**params)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(25)
        recs = Q.get_all_records()
        recs_cust1 = sorted([r for r in recs if r.id_number==1],
            key=lambda r: r.arrival_date)
        recs_cust2 = sorted([r for r in recs if r.id_number==2],
            key=lambda r: r.arrival_date)
        recs_cust3 = sorted([r for r in recs if r.id_number==3],
            key=lambda r: r.arrival_date)

        self.assertEqual([0, 1, 0, 1, 0, 1],
            [r.customer_class for r in recs_cust1])
        self.assertEqual([1, 0, 1, 0, 1],
            [r.customer_class for r in recs_cust2])
        self.assertEqual([0, 1, 0, 1],
            [r.customer_class for r in recs_cust3])

        self.assertEqual([1, 2, 1, 2, 1, 2], [r.node for r in recs_cust1])
        self.assertEqual([2, 1, 2, 1, 2], [r.node for r in recs_cust2])
        self.assertEqual([1, 2, 1, 2], [r.node for r in recs_cust3])

        self.assertEqual(set([r.customer_class for r
            in Q.nodes[1].individuals[0]]), set([1]))
        self.assertEqual(set([r.customer_class for r
            in Q.nodes[1].individuals[1]]), set([0]))
        self.assertEqual(set([r.customer_class for r
            in Q.nodes[2].individuals[0]]), set([1]))
        self.assertEqual(set([r.customer_class for r
            in Q.nodes[2].individuals[1]]), set([0]))

    def test_allow_zero_servers(self):
        params_c1 = {
            'arrival_distributions': [ciw.dists.Exponential(5)],
            'service_distributions': [ciw.dists.Deterministic(0.2)],
            'number_of_servers': [1]
        }

        params_c0 = {
            'arrival_distributions': [ciw.dists.Exponential(5)],
            'service_distributions': [ciw.dists.Deterministic(0.2)],
            'number_of_servers': [0]
        }

        ciw.seed(1)
        N = ciw.create_network(**params_c1)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(100)
        total_inds_1 = len(Q.nodes[-1].all_individuals) + len(Q.nodes[1].all_individuals)

        ciw.seed(1)
        N = ciw.create_network(**params_c0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(100)
        recs = Q.get_all_records()
        total_inds_0 = len(Q.nodes[1].all_individuals)

        self.assertEqual(recs, [])
        self.assertEqual(total_inds_0, total_inds_1)

    def test_schedules_and_blockages_work_together(self):
        N = ciw.create_network(
            arrival_distributions={
                'Class 0': [ciw.dists.Exponential(0.5),
                            ciw.dists.Exponential(0.9)],
                'Class 1': [ciw.dists.Exponential(0.6),
                            ciw.dists.Exponential(1.0)]},
            service_distributions={
                'Class 0': [ciw.dists.Exponential(0.8),
                            ciw.dists.Exponential(1.2)],
                'Class 1': [ciw.dists.Exponential(0.5),
                            ciw.dists.Exponential(1.0)]},
            number_of_servers=[([[1, 10], [0, 20], [2, 30]], True), 2],
            routing={
                'Class 0': [[0.1, 0.3], [0.2, 0.2]],
                'Class 1': [[0.0, 0.6], [0.2, 0.1]]},
            class_change_matrices={
                'Node 1': [[0.8, 0.2],
                           [0.5, 0.5]],
                'Node 2': [[1.0, 0.0],
                           [0.1, 0.9]]},
            queue_capacities=[2, 2]
        )
        ciw.seed(11)
        Q = ciw.Simulation(N, deadlock_detector=ciw.deadlock.StateDigraph(),tracker=ciw.trackers.NaiveTracker())
        Q.simulate_until_deadlock()
        ttd = Q.times_to_deadlock[((0, 0), (0, 0))]
        self.assertEqual(round(ttd, 5), 119.65819)


        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1.0), ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Deterministic(0.1), ciw.dists.Deterministic(3.0)],
            number_of_servers=[([[1, 2.5], [0, 2.8]], True), 1],
            queue_capacities=[float('inf'), 0],
            routing=[[0.0, 1.0], [0.0, 0.0]]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(3, method='Finish')
        inds = Q.nodes[-1].all_individuals
        service_times = [round(dr.service_time, 1) for ind in inds for dr in ind.data_records]
        self.assertEqual(service_times, [0.1, 3.0, 0.9, 3.0, 1.6, 3.0])

    def test_generic_deadlock_detector(self):
        DD = ciw.deadlock.NoDetection()
        self.assertEqual(DD.detect_deadlock(), False)

    def test_infinite_servers_from_file(self):
        N = ciw.create_network_from_yml('ciw/tests/testing_parameters/params_infservers.yml')
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(100, method='Finish')
        recs = Q.get_all_records()
        waits = [r.waiting_time for r in recs]
        self.assertEqual(waits, [0.0 for _ in range(100)])