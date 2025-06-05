import unittest
import ciw
from hypothesis import given
from hypothesis.strategies import floats, integers, random_module
import os
from decimal import Decimal
import networkx as nx
import csv
from itertools import cycle
import types
import math

N_params = ciw.create_network(
    arrival_distributions={
        "Class 0": [
            ciw.dists.Exponential(3.0),
            ciw.dists.Exponential(7.0),
            ciw.dists.Exponential(4.0),
            ciw.dists.Exponential(1.0),
        ],
        "Class 1": [
            ciw.dists.Exponential(2.0),
            ciw.dists.Exponential(3.0),
            ciw.dists.Exponential(6.0),
            ciw.dists.Exponential(4.0),
        ],
        "Class 2": [
            ciw.dists.Exponential(2.0),
            ciw.dists.Exponential(1.0),
            ciw.dists.Exponential(2.0),
            ciw.dists.Exponential(0.5),
        ],
    },
    number_of_servers=[9, 10, 8, 8],
    queue_capacities=[20, float("Inf"), 30, float("Inf")],
    service_distributions={
        "Class 0": [
            ciw.dists.Exponential(7.0),
            ciw.dists.Exponential(7.0),
            ciw.dists.Gamma(0.4, 0.6),
            ciw.dists.Deterministic(0.5),
        ],
        "Class 1": [
            ciw.dists.Exponential(7.0),
            ciw.dists.Triangular(0.1, 0.8, 0.85),
            ciw.dists.Exponential(8.0),
            ciw.dists.Exponential(5.0),
        ],
        "Class 2": [
            ciw.dists.Deterministic(0.3),
            ciw.dists.Deterministic(0.2),
            ciw.dists.Exponential(8.0),
            ciw.dists.Exponential(9.0),
        ],
    },
    routing={
        "Class 0": [
            [0.1, 0.2, 0.1, 0.4],
            [0.2, 0.2, 0.0, 0.1],
            [0.0, 0.8, 0.1, 0.1],
            [0.4, 0.1, 0.1, 0.0],
        ],
        "Class 1": [
            [0.6, 0.0, 0.0, 0.2],
            [0.1, 0.1, 0.2, 0.2],
            [0.9, 0.0, 0.0, 0.0],
            [0.2, 0.1, 0.1, 0.1],
        ],
        "Class 2": [
            [0.0, 0.0, 0.4, 0.3],
            [0.1, 0.1, 0.1, 0.1],
            [0.1, 0.3, 0.2, 0.2],
            [0.0, 0.0, 0.0, 0.3],
        ],
    },
)

N_deadlock = ciw.create_network(
    arrival_distributions=[ciw.dists.Exponential(35.0), ciw.dists.Exponential(35.0)],
    number_of_servers=[5, 5],
    queue_capacities=[5, 5],
    service_distributions=[ciw.dists.Exponential(25.0), ciw.dists.Exponential(25.0)],
    routing=[[0.32, 0.42], [0.42, 0.32]],
)


class TestSimulation(unittest.TestCase):
    def test_repr_method(self):
        Q1 = ciw.Simulation(N_params)
        self.assertEqual(str(Q1), "Simulation")

        Q = ciw.Simulation(N_params, name="My special simulation instance!")
        self.assertEqual(str(Q), "My special simulation instance!")

    def test_init_method(self):
        Q = ciw.Simulation(N_params)
        self.assertEqual(len(Q.transitive_nodes), 4)
        self.assertEqual(len(Q.nodes), 6)
        self.assertEqual(str(Q.nodes[0]), "Arrival Node")
        self.assertEqual(str(Q.nodes[-1]), "Exit Node")
        self.assertEqual(
            [str(n) for n in Q.transitive_nodes],
            ["Node 1", "Node 2", "Node 3", "Node 4"],
        )
        self.assertEqual(len(Q.inter_arrival_times), 4)
        self.assertEqual(len(Q.inter_arrival_times[1]), 3)
        self.assertEqual(len(Q.service_times), 4)
        self.assertEqual(len(Q.service_times[1]), 3)

    @given(
        arrival_rate=floats(min_value=0.1, max_value=100),
        service_rate=floats(min_value=0.1, max_value=100),
        number_of_servers=integers(min_value=1, max_value=30),
        rm=random_module(),
    )
    def test_init_method_h(self, arrival_rate, service_rate, number_of_servers, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(arrival_rate)],
            service_distributions=[ciw.dists.Exponential(service_rate)],
            number_of_servers=[number_of_servers],
        )
        Q = ciw.Simulation(N)

        self.assertEqual(len(Q.transitive_nodes), 1)
        self.assertEqual(len(Q.nodes), 3)
        self.assertEqual(str(Q.nodes[0]), "Arrival Node")
        self.assertEqual(str(Q.nodes[-1]), "Exit Node")
        self.assertEqual([str(n) for n in Q.transitive_nodes], ["Node 1"])
        self.assertEqual(len(Q.inter_arrival_times), 1)
        self.assertEqual(len(Q.inter_arrival_times[1]), 1)
        self.assertEqual(len(Q.service_times), 1)
        self.assertEqual(len(Q.service_times[1]), 1)
        self.assertEqual(
            [str(obs) for obs in Q.nodes], ["Arrival Node", "Node 1", "Exit Node"]
        )

    def test_find_next_active_node_method(self):
        Q = ciw.Simulation(N_params)
        i = 0
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i += 1
        self.assertEqual(str(Q.find_next_active_node()), "Arrival Node")

        Q = ciw.Simulation(N_params)
        i = 10
        for node in Q.nodes[:-1]:
            node.next_event_date = i
            i -= 1
        self.assertEqual(str(Q.find_next_active_node()), "Node 4")

    def test_simulate_until_max_time_method(self):
        ciw.seed(2)
        Q = ciw.Simulation(N_params)
        Q.simulate_until_max_time(150)
        L = Q.get_all_records()
        self.assertEqual(round(L[300].service_start_date, 8), 1.92388895)

        ciw.seed(60)
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(0.05), ciw.dists.Exponential(0.04)],
                "Class 1": [ciw.dists.Exponential(0.04), ciw.dists.Exponential(0.06)],
            },
            number_of_servers=[4, 3],
            queue_capacities=[float("Inf"), 10],
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(5.0), ciw.dists.Deterministic(5.0)],
                "Class 1": [
                    ciw.dists.Deterministic(10.0),
                    ciw.dists.Deterministic(10.0),
                ],
            },
            routing={
                "Class 0": [[0.8, 0.1], [0.0, 0.0]],
                "Class 1": [[0.8, 0.1], [0.2, 0.0]],
            },
            class_change_matrices=[
                {'Class 0': {'Class 0': 0.5, 'Class 1': 0.5}, 'Class 1': {'Class 0': 0.5, 'Class 1': 0.5}},
                {'Class 0': {'Class 0': 1.0, 'Class 1': 0.0}, 'Class 1': {'Class 0': 0.0, 'Class 1': 1.0}}
            ],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(50)
        L = Q.get_all_individuals()
        drl = []
        for dr in L[0].data_records:
            drl.append((dr.customer_class, dr.service_time))
        self.assertEqual(drl, [('Class 1', 10.0), ('Class 0', 5.0), ('Class 0', 5.0)])

    def test_simulate_until_max_time_with_pbar_method(self):
        Q = ciw.Simulation(N_params)
        Q.simulate_until_max_time(150, progress_bar=True)
        self.assertEqual(Q.progress_bar.total, 150)
        self.assertEqual(Q.progress_bar.n, 150)

    def test_simulate_until_max_customers(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1.0)],
            service_distributions=[ciw.dists.Exponential(0.5)],
            number_of_servers=[1],
            routing=[[0.0]],
            queue_capacities=[3],
        )
        # Test default method, 'Complete'
        ciw.seed(2)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(10)
        self.assertEqual(Q.nodes[-1].number_of_completed_individuals, 10)
        self.assertEqual(Q.nodes[-1].number_of_individuals, 34)
        completed_records = Q.get_all_records(only=["service"])
        self.assertEqual(len(completed_records), 10)

        # Test 'Complete' method
        ciw.seed(2)
        Q0 = ciw.Simulation(N)
        Q0.simulate_until_max_customers(10, method="Complete")
        self.assertEqual(Q0.nodes[-1].number_of_completed_individuals, 10)
        self.assertEqual(Q0.nodes[-1].number_of_individuals, 34)
        completed_records = Q0.get_all_records(only=["service"])
        self.assertEqual(len(completed_records), 10)

        next_active_node = Q0.find_next_active_node()
        end_time_complete = next_active_node.next_event_date

        # Test 'Finish' method
        ciw.seed(2)
        Q2 = ciw.Simulation(N)
        Q2.simulate_until_max_customers(10, method="Finish")
        self.assertEqual(Q2.nodes[-1].number_of_completed_individuals, 3)
        self.assertEqual(Q2.nodes[-1].number_of_individuals, 10)
        completed_records = Q2.get_all_records(only=["service"])
        self.assertEqual(len(completed_records), 3)

        next_active_node = Q2.find_next_active_node()
        end_time_finish = next_active_node.next_event_date

        # Test 'Arrive' method
        ciw.seed(2)
        Q3 = ciw.Simulation(N)
        Q3.simulate_until_max_customers(10, method="Arrive")
        self.assertEqual(Q3.nodes[0].number_of_individuals, 10)
        all_inds = sum([len(nd.all_individuals) for nd in Q3.nodes[1:]])
        rejected_records = Q3.get_all_records(only=["rejection"])
        number_of_losses = len(rejected_records)
        self.assertEqual(all_inds, 10)
        self.assertEqual(number_of_losses, 5)

        next_active_node = Q3.find_next_active_node()
        end_time_arrive = next_active_node.next_event_date

        # Test 'Accept' method
        ciw.seed(2)
        Q4 = ciw.Simulation(N)
        Q4.simulate_until_max_customers(10, method="Accept")
        self.assertEqual(Q4.nodes[0].number_accepted_individuals, 10)
        all_inds = sum([len(nd.all_individuals) for nd in Q4.nodes[1:]])
        completed_services = len(Q4.get_all_records(only=["service"]))
        still_in_node = len(Q4.nodes[1].all_individuals)
        self.assertEqual(completed_services + still_in_node, 10)

        next_active_node = Q4.find_next_active_node()
        end_time_accept = next_active_node.next_event_date

        # Assert that finish time of complete > accept > finish > arrive
        self.assertGreater(end_time_complete, end_time_accept)
        self.assertGreater(end_time_complete, end_time_finish)
        self.assertGreater(end_time_complete, end_time_arrive)
        self.assertGreater(end_time_accept, end_time_finish)
        self.assertGreater(end_time_accept, end_time_arrive)
        self.assertGreater(end_time_finish, end_time_arrive)

        # Test raise error if anything else
        ciw.seed(2)
        Q5 = ciw.Simulation(N)
        self.assertRaises(
            ValueError,
            lambda x: Q5.simulate_until_max_customers(10, method=x),
            "Jibberish",
        )

    def test_simulate_until_max_customers_with_pbar_method(self):
        N = N_params
        max_custs = 250

        ciw.seed(1)
        Q1 = ciw.Simulation(N)
        Q1.simulate_until_max_customers(max_custs, progress_bar=True, method="Finish")
        self.assertEqual(Q1.progress_bar.total, max_custs)
        self.assertEqual(Q1.progress_bar.n, max_custs)

        ciw.seed(1)
        Q2 = ciw.Simulation(N)
        Q2.simulate_until_max_customers(max_custs, progress_bar=True, method="Arrive")
        self.assertEqual(Q2.progress_bar.total, max_custs)
        self.assertEqual(Q2.progress_bar.n, max_custs)

        ciw.seed(1)
        Q3 = ciw.Simulation(N)
        Q3.simulate_until_max_customers(max_custs, progress_bar=True, method="Accept")
        self.assertEqual(Q3.progress_bar.total, max_custs)
        self.assertEqual(Q3.progress_bar.n, max_custs)

    def test_simulate_until_deadlock_method(self):
        # NaiveBlocking tracker
        ciw.seed(3)
        Q = ciw.Simulation(
            N_deadlock,
            deadlock_detector=ciw.deadlock.StateDigraph(),
            tracker=ciw.trackers.NaiveBlocking(),
        )
        Q.simulate_until_deadlock()
        self.assertEqual(round(Q.times_to_deadlock[((0, 0), (0, 0))], 8), 4.95885434)

        # SystemPopulation tracker
        ciw.seed(3)
        Q = ciw.Simulation(
            N_deadlock,
            deadlock_detector=ciw.deadlock.StateDigraph(),
            tracker=ciw.trackers.SystemPopulation(),
        )
        Q.simulate_until_deadlock()
        self.assertEqual(round(Q.times_to_deadlock[0], 8), 4.95885434)

        # NodePopulation tracker
        ciw.seed(3)
        Q = ciw.Simulation(
            N_deadlock,
            deadlock_detector=ciw.deadlock.StateDigraph(),
            tracker=ciw.trackers.NodePopulation(),
        )
        Q.simulate_until_deadlock()
        self.assertEqual(round(Q.times_to_deadlock[(0, 0)], 8), 4.95885434)

        # NodeClassMatrix tracker
        ciw.seed(3)
        Q = ciw.Simulation(
            N_deadlock,
            deadlock_detector=ciw.deadlock.StateDigraph(),
            tracker=ciw.trackers.NodeClassMatrix(),
        )
        Q.simulate_until_deadlock()
        self.assertEqual(round(Q.times_to_deadlock[((0,), (0,))], 8), 4.95885434)

    def test_detect_deadlock_method(self):
        Q = ciw.Simulation(N_deadlock, deadlock_detector=ciw.deadlock.StateDigraph())
        nodes = ["A", "B", "C", "D", "E"]
        connections = [("A", "D"), ("A", "B"), ("B", "E"), ("C", "B"), ("E", "C")]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), True)

        Q = ciw.Simulation(N_deadlock, deadlock_detector=ciw.deadlock.StateDigraph())
        nodes = ["A", "B", "C", "D"]
        connections = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D")]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), False)

        Q = ciw.Simulation(N_deadlock, deadlock_detector=ciw.deadlock.StateDigraph())
        nodes = ["A", "B"]
        Q.deadlock_detector.statedigraph = nx.DiGraph()
        for nd in nodes:
            Q.deadlock_detector.statedigraph.add_node(nd)
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), False)
        connections = [("A", "A")]
        for cnctn in connections:
            Q.deadlock_detector.statedigraph.add_edge(cnctn[0], cnctn[1])
        self.assertEqual(Q.deadlock_detector.detect_deadlock(), True)

    @given(
        arrival_rate=floats(min_value=0.1, max_value=10),
        service_rate=floats(min_value=0.1, max_value=10),
        rm=random_module(),
    )
    def test_mminf_node(self, arrival_rate, service_rate, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(arrival_rate)],
            service_distributions=[ciw.dists.Exponential(service_rate)],
            number_of_servers=[float("inf")],
            routing=[[0.0]],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(5)
        recs = Q.get_all_records()
        waits = [rec.waiting_time for rec in recs]
        self.assertEqual(sum(waits), 0.0)

    def test_simultaneous_events_example(self):
        # This should yield 3 or 2 customers finishing service.
        # Due to randomly choosing the order of events, the seed has
        # a big affect on this.
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(10.0), None],
            service_distributions=[
                ciw.dists.Deterministic(5.0),
                ciw.dists.Deterministic(5.0),
            ],
            routing=[[1.0, 0.0], [0.0, 0.0]],
            number_of_servers=[2, 1],
        )
        ciw.seed(36)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(36)
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 3)
        self.assertTrue(all([x[7] == 5.0 for x in recs[1:]]))

        ciw.seed(35)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(36)
        inds = Q.get_all_individuals()
        recs = Q.get_all_records()
        self.assertEqual(len(inds), 2)
        self.assertTrue(all([x[7] == 5.0 for x in recs[1:]]))

        completed_inds = []
        for _ in range(1000):
            Q = ciw.Simulation(N)
            Q.simulate_until_max_time(36)
            inds = Q.get_all_individuals()
            completed_inds.append(len(inds))
        self.assertAlmostEqual(completed_inds.count(2) / float(1000), 1 / 4.0, places=1)

    def test_exactness(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(20)],
            service_distributions=[ciw.dists.Deterministic(0.01)],
            routing=[[0.0]],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[0, 1, 0], shift_end_dates=[0.5, 0.55, 3.0])],
        )
        ciw.seed(777)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        mod_service_starts = [obs % 3 for obs in [r[6] for r in recs]]
        self.assertNotEqual(
            set(mod_service_starts),
            set([0.50, 0.51, 0.52, 0.53, 0.54, 0.55])
        )
        rounded_mod_service_starts = [round(r, 10) for r in mod_service_starts]
        self.assertEqual(
            set(rounded_mod_service_starts),
            set([0.50, 0.51, 0.52, 0.53, 0.54, 0.55])
        )

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(20)],
            service_distributions=[ciw.dists.Deterministic(0.01)],
            routing=[[0.0]],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[0, 1, 0], shift_end_dates=[0.5, 0.55, 3.0])],
        )

        ciw.seed(777)
        Q = ciw.Simulation(N, exact=14)
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        mod_service_starts = [obs % 3 for obs in [r[6] for r in recs]]
        expected_set = set([Decimal(k) for k in ["0.50", "0.51", "0.52", "0.53", "0.54", "0.55"]])
        self.assertEqual(set(mod_service_starts), expected_set)

    def test_setting_classes(self):
        class DummyNode(ciw.Node):
            pass

        class DummyArrivalNode(ciw.ArrivalNode):
            pass

        class DummyExitNode(ciw.ExitNode):
            pass

        class DummyIndividual(ciw.Individual):
            pass

        class DummyServer(ciw.Server):
            pass

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(20)],
            service_distributions=[ciw.dists.Deterministic(0.01)],
            routing=[[0.0]],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.IndividualType, ciw.Individual)

        Q.set_classes(None, None, None, None, None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(DummyNode, None, None, None, None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(None, DummyArrivalNode, None, None, None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(None, None, None, DummyIndividual, None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(None, None, None, None, DummyServer)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(DummyNode, DummyArrivalNode, None, None, None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(DummyNode, None, None, DummyIndividual, None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(DummyNode, None, None, None, DummyServer)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(None, DummyArrivalNode, None, DummyIndividual, None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(None, DummyArrivalNode, None, None, DummyServer)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(None, None, None, DummyIndividual, DummyServer)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(DummyNode, DummyArrivalNode, None, DummyIndividual, None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(DummyNode, DummyArrivalNode, None, None, DummyServer)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(DummyNode, None, None, DummyIndividual, DummyServer)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(None, DummyArrivalNode, None, DummyIndividual, DummyServer)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(DummyNode, DummyArrivalNode, None, DummyIndividual, DummyServer)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, ciw.ExitNode)

        Q.set_classes(None, None, DummyExitNode, None, None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(DummyNode, None, DummyExitNode, None, None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(None, DummyArrivalNode, DummyExitNode, None, None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(None, None, DummyExitNode, DummyIndividual, None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(None, None, DummyExitNode, None, DummyServer)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(DummyNode, DummyArrivalNode, DummyExitNode, None, None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(DummyNode, None, DummyExitNode, DummyIndividual, None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(DummyNode, None, DummyExitNode, None, DummyServer)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(None, DummyArrivalNode, DummyExitNode, DummyIndividual, None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(None, DummyArrivalNode, DummyExitNode, None, DummyServer)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(None, None, DummyExitNode, DummyIndividual, DummyServer)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(DummyNode, DummyArrivalNode, DummyExitNode, DummyIndividual, None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(DummyNode, DummyArrivalNode, DummyExitNode, None, DummyServer)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(DummyNode, None, DummyExitNode, DummyIndividual, DummyServer)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(None, DummyArrivalNode, DummyExitNode, DummyIndividual, DummyServer)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)

        Q.set_classes(DummyNode, DummyArrivalNode, DummyExitNode, DummyIndividual, DummyServer)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertEqual(Q.ExitNodeType, DummyExitNode)


    def test_setting_classes_in_init(self):
        class DummyNode(ciw.Node):
            pass

        class DummyArrivalNode(ciw.ArrivalNode):
            pass

        class DummyExitNode(ciw.ExitNode):
            pass

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(20)],
            service_distributions=[ciw.dists.Deterministic(0.01)],
            routing=[[0.0]],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[0, 1, 0], shift_end_dates=[0.5, 0.55, 3.0])],
        )
        Q = ciw.Simulation(N, node_class=None, arrival_node_class=None, exit_node_class=None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[0], ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[-1], ciw.ExitNode)
        self.assertFalse(isinstance(Q.nodes[1], DummyNode))
        self.assertFalse(isinstance(Q.nodes[0], DummyArrivalNode))
        self.assertFalse(isinstance(Q.nodes[-1], DummyExitNode))

        Q = ciw.Simulation(N, node_class=DummyNode, arrival_node_class=None, exit_node_class=None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[1], DummyNode)
        self.assertIsInstance(Q.nodes[0], ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[-1], ciw.ExitNode)
        self.assertFalse(isinstance(Q.nodes[0], DummyArrivalNode))
        self.assertFalse(isinstance(Q.nodes[-1], DummyExitNode))

        Q = ciw.Simulation(N, node_class=None, arrival_node_class=DummyArrivalNode, exit_node_class=None)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[0], DummyArrivalNode)
        self.assertIsInstance(Q.nodes[-1], ciw.ExitNode)
        self.assertFalse(isinstance(Q.nodes[1], DummyNode))
        self.assertFalse(isinstance(Q.nodes[-1], DummyExitNode))

        Q = ciw.Simulation(N, node_class=DummyNode, arrival_node_class=DummyArrivalNode, exit_node_class=None)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertIsInstance(Q.nodes[1], DummyNode)
        self.assertIsInstance(Q.nodes[0], DummyArrivalNode)
        self.assertIsInstance(Q.nodes[-1], ciw.ExitNode)
        self.assertFalse(isinstance(Q.nodes[-1], DummyExitNode))

        Q = ciw.Simulation(N, node_class=None, arrival_node_class=None, exit_node_class=DummyExitNode)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[0], ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[-1], DummyExitNode)
        self.assertFalse(isinstance(Q.nodes[1], DummyNode))
        self.assertFalse(isinstance(Q.nodes[0], DummyArrivalNode))

        Q = ciw.Simulation(N, node_class=DummyNode, arrival_node_class=None, exit_node_class=DummyExitNode)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[1], DummyNode)
        self.assertIsInstance(Q.nodes[0], ciw.ArrivalNode)
        self.assertIsInstance(Q.nodes[-1], DummyExitNode)
        self.assertFalse(isinstance(Q.nodes[0], DummyArrivalNode))

        Q = ciw.Simulation(N, node_class=None, arrival_node_class=DummyArrivalNode, exit_node_class=DummyExitNode)
        self.assertEqual(Q.NodeTypes, [ciw.Node])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[0], DummyArrivalNode)
        self.assertIsInstance(Q.nodes[-1], DummyExitNode)
        self.assertFalse(isinstance(Q.nodes[1], DummyNode))

        Q = ciw.Simulation(N, node_class=DummyNode, arrival_node_class=DummyArrivalNode, exit_node_class=DummyExitNode)
        self.assertEqual(Q.NodeTypes, [DummyNode])
        self.assertEqual(Q.ArrivalNodeType, DummyArrivalNode)
        self.assertIsInstance(Q.nodes[1], DummyNode)
        self.assertIsInstance(Q.nodes[0], DummyArrivalNode)
        self.assertIsInstance(Q.nodes[-1], DummyExitNode)


    def test_setting_multiple_node_classes(self):
        class DummyNode1(ciw.Node):
            pass

        class DummyNode2(ciw.Node):
            pass

        class DummyNode3(ciw.Node):
            pass

        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(10),
                ciw.dists.Exponential(10),
                ciw.dists.Exponential(10),
            ],
            service_distributions=[
                ciw.dists.Exponential(10),
                ciw.dists.Exponential(10),
                ciw.dists.Exponential(10),
            ],
            routing=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
            number_of_servers=[1, 1, 1],
        )

        Q = ciw.Simulation(N)
        self.assertEqual(Q.NodeTypes, [ciw.Node, ciw.Node, ciw.Node])
        self.assertIsInstance(Q.nodes[1], ciw.Node)
        self.assertIsInstance(Q.nodes[2], ciw.Node)
        self.assertIsInstance(Q.nodes[3], ciw.Node)

        Q = ciw.Simulation(N, node_class=DummyNode1)
        self.assertEqual(Q.NodeTypes, [DummyNode1, DummyNode1, DummyNode1])
        self.assertIsInstance(Q.nodes[1], DummyNode1)
        self.assertIsInstance(Q.nodes[2], DummyNode1)
        self.assertIsInstance(Q.nodes[3], DummyNode1)

        Q = ciw.Simulation(N, node_class=DummyNode2)
        self.assertEqual(Q.NodeTypes, [DummyNode2, DummyNode2, DummyNode2])
        self.assertIsInstance(Q.nodes[1], DummyNode2)
        self.assertIsInstance(Q.nodes[2], DummyNode2)
        self.assertIsInstance(Q.nodes[3], DummyNode2)

        Q = ciw.Simulation(N, node_class=DummyNode3)
        self.assertEqual(Q.NodeTypes, [DummyNode3, DummyNode3, DummyNode3])
        self.assertIsInstance(Q.nodes[1], DummyNode3)
        self.assertIsInstance(Q.nodes[2], DummyNode3)
        self.assertIsInstance(Q.nodes[3], DummyNode3)

        Q = ciw.Simulation(N, node_class=[DummyNode1, DummyNode2, DummyNode3])
        self.assertEqual(Q.NodeTypes, [DummyNode1, DummyNode2, DummyNode3])
        self.assertIsInstance(Q.nodes[1], DummyNode1)
        self.assertIsInstance(Q.nodes[2], DummyNode2)
        self.assertIsInstance(Q.nodes[3], DummyNode3)

        Q = ciw.Simulation(N, node_class=[DummyNode1, DummyNode3, DummyNode2])
        self.assertEqual(Q.NodeTypes, [DummyNode1, DummyNode3, DummyNode2])
        self.assertIsInstance(Q.nodes[1], DummyNode1)
        self.assertIsInstance(Q.nodes[2], DummyNode3)
        self.assertIsInstance(Q.nodes[3], DummyNode2)

        Q = ciw.Simulation(N, node_class=[DummyNode2, DummyNode1, DummyNode3])
        self.assertEqual(Q.NodeTypes, [DummyNode2, DummyNode1, DummyNode3])
        self.assertIsInstance(Q.nodes[1], DummyNode2)
        self.assertIsInstance(Q.nodes[2], DummyNode1)
        self.assertIsInstance(Q.nodes[3], DummyNode3)

        Q = ciw.Simulation(N, node_class=[DummyNode2, DummyNode3, DummyNode1])
        self.assertEqual(Q.NodeTypes, [DummyNode2, DummyNode3, DummyNode1])
        self.assertIsInstance(Q.nodes[1], DummyNode2)
        self.assertIsInstance(Q.nodes[2], DummyNode3)
        self.assertIsInstance(Q.nodes[3], DummyNode1)

        Q = ciw.Simulation(N, node_class=[DummyNode3, DummyNode2, DummyNode1])
        self.assertEqual(Q.NodeTypes, [DummyNode3, DummyNode2, DummyNode1])
        self.assertIsInstance(Q.nodes[1], DummyNode3)
        self.assertIsInstance(Q.nodes[2], DummyNode2)
        self.assertIsInstance(Q.nodes[3], DummyNode1)

        Q = ciw.Simulation(N, node_class=[DummyNode3, DummyNode1, DummyNode2])
        self.assertEqual(Q.NodeTypes, [DummyNode3, DummyNode1, DummyNode2])
        self.assertIsInstance(Q.nodes[1], DummyNode3)
        self.assertIsInstance(Q.nodes[2], DummyNode1)
        self.assertIsInstance(Q.nodes[3], DummyNode2)

        Q = ciw.Simulation(N, node_class=[DummyNode1, DummyNode1, DummyNode2])
        self.assertEqual(Q.NodeTypes, [DummyNode1, DummyNode1, DummyNode2])
        self.assertIsInstance(Q.nodes[1], DummyNode1)
        self.assertIsInstance(Q.nodes[2], DummyNode1)
        self.assertIsInstance(Q.nodes[3], DummyNode2)

    def test_raise_error_when_setting_wrong_number_of_node_classes(self):
        class DummyNode(ciw.Node):
            pass

        def create_simulation_with_node_classes(node_classes):
            N = ciw.create_network(
                arrival_distributions=[
                    ciw.dists.Exponential(10),
                    ciw.dists.Exponential(10),
                    ciw.dists.Exponential(10),
                ],
                service_distributions=[
                    ciw.dists.Exponential(10),
                    ciw.dists.Exponential(10),
                    ciw.dists.Exponential(10),
                ],
                routing=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                number_of_servers=[1, 1, 1],
            )
            return ciw.Simulation(N, node_class=node_classes)

        two_nodes = [DummyNode, DummyNode]
        four_nodes = [DummyNode, DummyNode, DummyNode, DummyNode]
        self.assertRaises(ValueError, create_simulation_with_node_classes, two_nodes)
        self.assertRaises(ValueError, create_simulation_with_node_classes, four_nodes)

    def test_setting_individual_and_server_classes_in_init(self):
        class DummyIndividual(ciw.Individual):
            def __repr__(self):
                return "DummyIndividual %s" % self.id_number

        class DummyServer(ciw.Server):
            def __repr__(self):
                return "DummyServer %s at Node %s" % (
                    self.id_number,
                    self.node.id_number,
                )

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(5)],
            service_distributions=[ciw.dists.Deterministic(100)],
            routing=[[0.0]],
            number_of_servers=[2],
        )
        Q = ciw.Simulation(N, individual_class=None, server_class=None)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertIsInstance(Q.nodes[1].servers[0], ciw.Server)
        self.assertIsInstance(Q.nodes[1].servers[1], ciw.Server)
        self.assertEqual(str(Q.nodes[1].servers[0]), "Server 1 at Node 1")
        self.assertEqual(str(Q.nodes[1].servers[1]), "Server 2 at Node 1")
        Q.simulate_until_max_time(6)
        self.assertIsInstance(Q.nodes[1].all_individuals[0], ciw.Individual)
        self.assertEqual(str(Q.nodes[1].all_individuals[0]), "Individual 1")

        Q = ciw.Simulation(N, individual_class=DummyIndividual, server_class=None,)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, ciw.Server)
        self.assertIsInstance(Q.nodes[1].servers[0], ciw.Server)
        self.assertIsInstance(Q.nodes[1].servers[1], ciw.Server)
        self.assertEqual(str(Q.nodes[1].servers[0]), "Server 1 at Node 1")
        self.assertEqual(str(Q.nodes[1].servers[1]), "Server 2 at Node 1")
        Q.simulate_until_max_time(6)
        self.assertIsInstance(Q.nodes[1].all_individuals[0], DummyIndividual)
        self.assertEqual(str(Q.nodes[1].all_individuals[0]), "DummyIndividual 1")

        Q = ciw.Simulation(N, individual_class=None, server_class=DummyServer,)
        self.assertEqual(Q.IndividualType, ciw.Individual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertIsInstance(Q.nodes[1].servers[0], DummyServer)
        self.assertIsInstance(Q.nodes[1].servers[1], DummyServer)
        self.assertEqual(str(Q.nodes[1].servers[0]), "DummyServer 1 at Node 1")
        self.assertEqual(str(Q.nodes[1].servers[1]), "DummyServer 2 at Node 1")
        Q.simulate_until_max_time(6)
        self.assertIsInstance(Q.nodes[1].all_individuals[0], ciw.Individual)
        self.assertEqual(str(Q.nodes[1].all_individuals[0]), "Individual 1")

        Q = ciw.Simulation(N, individual_class=DummyIndividual, server_class=DummyServer)
        self.assertEqual(Q.IndividualType, DummyIndividual)
        self.assertEqual(Q.ServerType, DummyServer)
        self.assertIsInstance(Q.nodes[1].servers[0], DummyServer)
        self.assertIsInstance(Q.nodes[1].servers[1], DummyServer)
        self.assertEqual(str(Q.nodes[1].servers[0]), "DummyServer 1 at Node 1")
        self.assertEqual(str(Q.nodes[1].servers[1]), "DummyServer 2 at Node 1")
        Q.simulate_until_max_time(6)
        self.assertIsInstance(Q.nodes[1].all_individuals[0], DummyIndividual)
        self.assertEqual(str(Q.nodes[1].all_individuals[0]), "DummyIndividual 1")

    def test_get_all_records(self):
        Q = ciw.Simulation(N_params)
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        for row in recs:
            self.assertIsInstance(row, ciw.data_record.DataRecord)
            self.assertEqual(len(row), len(ciw.data_record.DataRecord._fields))

    def test_namedtuple_record(self):
        expected_fields = (
            "id_number",
            "customer_class",
            "original_customer_class",
            "node",
            "arrival_date",
            "waiting_time",
            "service_start_date",
            "service_time",
            "service_end_date",
            "time_blocked",
            "exit_date",
            "destination",
            "queue_size_at_arrival",
            "queue_size_at_departure",
            "server_id",
            "record_type",
        )
        self.assertEqual(ciw.data_record.DataRecord._fields, expected_fields)
        self.assertEqual(ciw.data_record.DataRecord.__name__, "Record")

    def test_priority_output(self):
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Deterministic(1.0)],
                "Class 1": [ciw.dists.Deterministic(1.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(0.75)],
                "Class 1": [ciw.dists.Deterministic(0.75)],
            },
            routing={"Class 0": [[0.0]], "Class 1": [[0.0]]},
            number_of_servers=[1],
            priority_classes={"Class 0": 0, "Class 1": 1},
        )
        ciw.seed(36)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(35)
        recs = Q.get_all_records()
        waits = [
            sum([r.waiting_time for r in recs if r.customer_class == cls])
            for cls in ['Class 0', 'Class 1']
        ]
        # Because of high traffic intensity: the low
        # priority individuals have a large wait
        self.assertEqual(sorted(waits), [12.75, 135.75])

        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Deterministic(1.0)],
                "Class 1": [ciw.dists.Deterministic(1.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(0.75)],
                "Class 1": [ciw.dists.Deterministic(0.75)],
            },
            routing={"Class 0": [[0.0]], "Class 1": [[0.0]]},
            number_of_servers=[1],
        )
        ciw.seed(36)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(35)
        recs = Q.get_all_records()
        waits = [
            sum([r.waiting_time for r in recs if r.customer_class == cls])
            for cls in ['Class 0', 'Class 1']
        ]
        # Both total waits are now comparable. Total wait is higher
        # because more more individuals have gone through the system.
        self.assertEqual(sorted(waits),  [126.5, 132.0])

    def test_priority_system_compare_literature(self):
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(0.2)],
                "Class 1": [ciw.dists.Exponential(0.6)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(1.0)],
                "Class 1": [ciw.dists.Exponential(1.0)],
            },
            routing={"Class 0": [[0.0]], "Class 1": [[0.0]]},
            number_of_servers=[1],
            priority_classes={"Class 0": 0, "Class 1": 1},
        )
        # Results expected from analytical queueing theory are:
        # expected_throughput_class0 = 2.0, and expected_throughput_class1 = 6.0
        throughput_class0 = []
        throughput_class1 = []

        ciw.seed(3231)
        for iteration in range(25):
            Q = ciw.Simulation(N)
            Q.simulate_until_max_time(180)
            recs = Q.get_all_records()
            throughput_c0 = [
                r.waiting_time + r.service_time
                for r in recs
                if r.customer_class == 'Class 0'
                if r.arrival_date > 100
            ]
            throughput_c1 = [
                r.waiting_time + r.service_time
                for r in recs
                if r.customer_class == 'Class 1'
                if r.arrival_date > 100
            ]
            throughput_class0.append(sum(throughput_c0) / len(throughput_c0))
            throughput_class1.append(sum(throughput_c1) / len(throughput_c1))

        self.assertEqual(round(sum(throughput_class0) / 25, 5), 1.84736)
        self.assertEqual(round(sum(throughput_class1) / 25, 5), 5.71125)

    def test_baulking(self):
        def my_baulking_function(n, Q=None, next_ind=None, next_node=None):
            if n < 3:
                return 0.0
            return 1.0

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(5.0)],
            service_distributions=[ciw.dists.Deterministic(21.0)],
            number_of_servers=[1],
            baulking_functions=[my_baulking_function],
        )

        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(51)
        recs = Q.get_all_records()
        completed_recs = [r for r in recs if r.record_type == "service"]
        baulk_recs = [r for r in recs if r.record_type == "baulk"]
        self.assertEqual(
            [r.arrival_date for r in baulk_recs], [20.0, 25.0, 35.0, 40.0, 45.0]
        )
        self.assertEqual([r.id_number for r in completed_recs], [1, 2])
        self.assertEqual([r.arrival_date for r in completed_recs], [5.0, 10.0])
        self.assertEqual([r.waiting_time for r in completed_recs], [0.0, 16.0])
        self.assertEqual([r.service_start_date for r in completed_recs], [5.0, 26.0])
        self.assertEqual([r.service_end_date for r in completed_recs], [26.0, 47.0])

        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Deterministic(5.0),
                ciw.dists.Deterministic(23.0),
            ],
            service_distributions=[
                ciw.dists.Deterministic(21.0),
                ciw.dists.Deterministic(1.5),
            ],
            routing=[[0.0, 0.0], [1.0, 0.0]],
            number_of_servers=[1, 1],
            baulking_functions=[my_baulking_function, None],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(51)
        recs = Q.get_all_records()
        completed_recs = [r for r in recs if r.record_type == "service"]
        baulk_recs = [r for r in recs if r.record_type == "baulk"]
        self.assertEqual(
            [r.arrival_date for r in baulk_recs],
            [20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
        )
        self.assertEqual(sorted([r.id_number for r in completed_recs]), [1, 2, 5, 11])
        self.assertEqual(
            sorted([r.arrival_date for r in completed_recs]),
            [5.0, 10.0, 23.0, 46.0]
        )
        self.assertEqual(
            sorted([r.waiting_time for r in completed_recs]),
            [0.0, 0.0, 0.0, 16.0]
        )
        self.assertEqual(
            sorted([r.service_start_date for r in completed_recs]),
            [5.0, 23.0, 26.0, 46.0],
        )
        self.assertEqual(
            sorted([r.service_end_date for r in completed_recs]),
            [24.5, 26.0, 47.0, 47.5],
        )

    def test_state_dependent_baulking(self):
        def my_baulking_function(n, Q, next_ind=None, next_node=None):
            total_population = sum(node.number_of_individuals for node in Q.transitive_nodes)
            if total_population < 5:
                return 0.0
            return 1.0

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(5.0)],
            service_distributions=[ciw.dists.Deterministic(21.0)],
            number_of_servers=[1],
            baulking_functions=[my_baulking_function],
        )

        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(200)
        max_population = max(ts[1] for ts in Q.statetracker.history)
        self.assertEqual(max_population, 5)


    def test_prioritys_with_classchanges(self):
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(0.5), ciw.dists.Exponential(0.5)],
                "Class 1": [ciw.dists.Exponential(0.5), ciw.dists.Exponential(0.5)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Uniform(0.9, 1.1), ciw.dists.Uniform(0.9, 1.1)],
                "Class 1": [ciw.dists.Uniform(0.9, 1.1), ciw.dists.Uniform(0.9, 1.1)],
            },
            number_of_servers=[1, 1],
            routing={
                "Class 0": [[0.0, 1.0], [1.0, 0.0]],
                "Class 1": [[0.0, 1.0], [1.0, 0.0]],
            },
            priority_classes={"Class 1": 0, "Class 0": 1},
            class_change_matrices=[
                {'Class 0': {'Class 0': 0.0, 'Class 1': 1.0}, 'Class 1': {'Class 0': 1.0, 'Class 1': 0.0}},
                {'Class 0': {'Class 0': 0.0, 'Class 1': 1.0}, 'Class 1': {'Class 0': 1.0, 'Class 1': 0.0}}
            ],
        )
        ciw.seed(1)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(25)
        recs = Q.get_all_records()
        recs_cust1 = sorted(
            [r for r in recs if r.id_number == 1],
            key=lambda r: r.arrival_date
        )
        recs_cust2 = sorted(
            [r for r in recs if r.id_number == 2],
            key=lambda r: r.arrival_date
        )
        recs_cust3 = sorted(
            [r for r in recs if r.id_number == 3],
            key=lambda r: r.arrival_date
        )

        self.assertEqual(['Class 0', 'Class 1', 'Class 0', 'Class 1', 'Class 0', 'Class 1'], [r.customer_class for r in recs_cust1])
        self.assertEqual(['Class 1', 'Class 0', 'Class 1', 'Class 0', 'Class 1'], [r.customer_class for r in recs_cust2])
        self.assertEqual(['Class 0', 'Class 1', 'Class 0', 'Class 1'], [r.customer_class for r in recs_cust3])

        self.assertEqual([1, 2, 1, 2, 1, 2], [r.node for r in recs_cust1])
        self.assertEqual([2, 1, 2, 1, 2], [r.node for r in recs_cust2])
        self.assertEqual([1, 2, 1, 2], [r.node for r in recs_cust3])

        self.assertEqual(
            set([r.customer_class for r in Q.nodes[1].individuals[0]]),
            set(['Class 1'])
        )
        self.assertEqual(
            set([r.customer_class for r in Q.nodes[1].individuals[1]]),
            set(['Class 0'])
        )
        self.assertEqual(
            set([r.customer_class for r in Q.nodes[2].individuals[0]]),
            set(['Class 1'])
        )
        self.assertEqual(
            set([r.customer_class for r in Q.nodes[2].individuals[1]]),
            set(['Class 0'])
        )

    def test_allow_zero_servers(self):
        N_c1 = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(5)],
            service_distributions=[ciw.dists.Deterministic(0.2)],
            number_of_servers=[1],
        )
        N_c0 = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(5)],
            service_distributions=[ciw.dists.Deterministic(0.2)],
            number_of_servers=[0],
        )
        ciw.seed(1)
        Q = ciw.Simulation(N_c1)
        Q.simulate_until_max_time(100)
        total_inds_1 = len(Q.nodes[-1].all_individuals) + len(Q.nodes[1].all_individuals)

        ciw.seed(1)
        Q = ciw.Simulation(N_c0)
        Q.simulate_until_max_time(100)
        recs = Q.get_all_records()
        total_inds_0 = len(Q.nodes[1].all_individuals)

        self.assertEqual(recs, [])
        self.assertEqual(total_inds_0, total_inds_1)

    def test_schedules_and_blockages_work_together(self):
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(0.5), ciw.dists.Exponential(0.9)],
                "Class 1": [ciw.dists.Exponential(0.6), ciw.dists.Exponential(1.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(0.8), ciw.dists.Exponential(1.2)],
                "Class 1": [ciw.dists.Exponential(0.5), ciw.dists.Exponential(1.0)],
            },
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 2], shift_end_dates=[10, 20, 30], preemption="resample"), 2],
            routing={
                "Class 0": [[0.1, 0.3], [0.2, 0.2]],
                "Class 1": [[0.0, 0.6], [0.2, 0.1]],
            },
            class_change_matrices=[
                {'Class 0': {'Class 0': 0.8, 'Class 1': 0.2}, 'Class 1': {'Class 0': 0.5, 'Class 1': 0.5}},
                {'Class 0': {'Class 0': 1.0, 'Class 1': 0.0}, 'Class 1': {'Class 0': 0.1, 'Class 1': 0.9}}
            ],
            queue_capacities=[2, 2],
        )
        ciw.seed(10)
        Q = ciw.Simulation(
            N,
            deadlock_detector=ciw.deadlock.StateDigraph(),
            tracker=ciw.trackers.NaiveBlocking(),
        )
        Q.simulate_until_deadlock()
        ttd = Q.times_to_deadlock[((0, 0), (0, 0))]
        self.assertEqual(round(ttd, 5), 51.75691)

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1.0), None],
            service_distributions=[
                ciw.dists.Deterministic(0.1),
                ciw.dists.Deterministic(3.0),
            ],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0], shift_end_dates=[2.5, 2.8], preemption="resample"), 1],
            queue_capacities=[float("inf"), 0],
            routing=[[0.0, 1.0], [0.0, 0.0]],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(3, method="Finish")
        inds = Q.nodes[-1].all_individuals
        service_times = [
            round(dr.service_time, 1)
            for ind in inds
            for dr in ind.data_records
            if dr.record_type == "service"
        ]
        self.assertEqual(service_times, [0.1, 3.0, 0.1, 3.0, 0.1, 3.0])

    def test_generic_deadlock_detector(self):
        DD = ciw.deadlock.NoDetection()
        self.assertEqual(DD.detect_deadlock(), False)

    def test_system_capacity(self):
        """
        Expected results would be:

        node    id  arrival_date  current_capacity  start_date  end_date
        ----------------------------------------------------------------
           1     1           0.8                 1         0.8       5.9
           2     2           1.0                 2         1.0       6.1
           1     3           1.6                 3         5.9      11.0
           2     4           2.0                 4         6.1      11.2
           1     5           2.4                 5        11.0      16.1
           2     6           3.0                 reject
           1     7           3.2                 reject
          1,2  8,9           4.0                 reject
           1    10           4.8                 reject
           2    11           5.0                 reject
           1    12           5.6                 reject
           2    13           6.0                 5        11.2      16.3
           1    14           6.4                 5        16.1      21.2
           2    15           7.0                 reject
           1    16           7.2                 reject
          1,2  17,18         8.0                 reject
           1    19           8.8                 reject
           2    20           9.0                 reject
           1    21           9.6                 reject
           2    22          10.0                 reject
           1    23          10.4                 reject
           2    24          11.0                 5      16.3       21.4
           1    25          11.2                 5      21.2       26.3  (incomplete)
           2    26          12.0                 reject
           1    27          12.0                 reject
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(0.8), ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(5.1), ciw.dists.Deterministic(5.1)],
            routing=[[0.0, 0.0], [0.0, 0.0]],
            number_of_servers=[1, 1],
            system_capacity=5
        )
        ciw.seed(0) ## Set seed to exactly replicate simultaneous events
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(22)
        recs_service = sorted(Q.get_all_records(only=['service']), key=lambda r: r.arrival_date)
        recs_reject = sorted(Q.get_all_records(only=['rejection']), key=lambda r: r.arrival_date)

        expected_arrivals = [0.8, 1.0, 1.6, 2.0, 2.4, 6.0, 6.4, 11.0]
        expected_ssds = [0.8, 1.0, 5.9, 6.1, 11.0, 11.2, 16.1, 16.3]
        expected_seds = [5.9, 6.1, 11.0, 11.2, 16.1, 16.3, 21.2, 21.4]
        expected_nodes = [1, 2, 1, 2, 1, 2, 1, 2]
        expected_first_10_rejection_times = [3.0, 3.2, 4.0, 4.0, 4.8, 5.0, 5.6, 7.0, 7.2, 8.0]

        self.assertTrue(all([s[1] <= 5 for s in Q.statetracker.history]))
        self.assertEqual([round(r.arrival_date, 2) for r in recs_service], expected_arrivals)
        self.assertEqual([r.node for r in recs_service], expected_nodes)
        self.assertEqual([round(r.service_start_date, 2) for r in recs_service], expected_ssds)
        self.assertEqual([round(r.service_end_date, 2) for r in recs_service], expected_seds)
        self.assertEqual([round(r.arrival_date, 2) for r in recs_reject][:10], expected_first_10_rejection_times)

    def test_reroute_preemption_classpriorities(self):
        """
        Class 0 arrive to Node 1 every 0.7, service lasts 0.2
        Class 1 arrive to Node 1 every 1.0, service lasts 0.2
        Class 0 have priority over class 1
        Class 1 rerouted to Node 2 upon preemption

        Ind    arr    clss    end
          1    0.7       0    0.9
          2    1.0       1    1.2
          3    1.4       0    1.6
          4    2.0       1    interrupted (goes to Node 2 for 0.5)
          5    2.1       0    2.3
        """
        class Reroute(ciw.routing.NodeRouting):
            def next_node(self, ind):
                """
                Chooses the exit node with probability 1.
                """
                return self.simulation.nodes[-1]

            def next_node_for_rerouting(self, ind):
                """
                Chooses Node 2
                """
                return self.simulation.nodes[2]

        N = ciw.create_network(
            arrival_distributions={
                'Class 0': [ciw.dists.Deterministic(value=0.7), None],
                'Class 1': [ciw.dists.Deterministic(value=1.0), None]
            },
            service_distributions={
                'Class 0': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.5)],
                'Class 1': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.5)]
            },
            number_of_servers=[1, 1],
            priority_classes=({'Class 0': 0, 'Class 1': 1}, ['reroute', False]),
            routing={
                'Class 0': ciw.routing.NetworkRouting(routers=[ciw.routing.Leave(), ciw.routing.Leave()]),
                'Class 1': ciw.routing.NetworkRouting(routers=[Reroute(), ciw.routing.Leave()])
            }
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(2.7)
        recs = Q.get_all_records()

        nd_1 = sorted([r for r in recs if r.node == 1], key=lambda r: r.arrival_date)
        self.assertEqual([round(r.arrival_date, 5) for r in nd_1], [0.7, 1.0, 1.4, 2.0, 2.1])
        self.assertEqual([round(r.service_time, 5) for r in nd_1], [0.2, 0.2, 0.2, 0.2, 0.2])
        self.assertEqual([round(r.exit_date, 5) for r in nd_1], [0.9, 1.2, 1.6, 2.1, 2.3])
        self.assertEqual([r.destination for r in nd_1], [-1, -1, -1, 2, -1])
        self.assertEqual([r.record_type for r in nd_1], ['service', 'service', 'service', 'interrupted service', 'service'])

        nd_2 = sorted([r for r in recs if r.node == 2], key=lambda r: r.arrival_date)
        self.assertEqual([round(r.arrival_date, 5) for r in nd_2], [2.1])
        self.assertEqual([round(r.service_time, 5) for r in nd_2], [0.5])
        self.assertEqual([round(r.exit_date, 5) for r in nd_2], [2.6])
        self.assertEqual([r.destination for r in nd_2], [-1])
        self.assertEqual([r.record_type for r in nd_2], ['service'])

        """
        Class 0 arrive to Node 1 every 0.7, service lasts 0.2
        Class 1 arrive to Node 1 every 1.0, service lasts 0.2
        Class 0 have priority over class 1
        All classes go Node 1 then Node 2

        Node 1
        Ind    arr    clss    end
          1    0.7       0    0.9
          2    1.0       1    1.2
          3    1.4       0    1.6
          4    2.0       1    interrupted
          5    2.1       0    2.3

        Node 2
        Ind    arr    clss    end
          1    0.9       0    1.0
          2    1.2       1    1.3
          3    1.6       0    1.7
          4    2.1       1    2.2
          5    2.3       0    2.4
        """
        N = ciw.create_network(
            arrival_distributions={
                'Class 0': [ciw.dists.Deterministic(value=0.7), None],
                'Class 1': [ciw.dists.Deterministic(value=1.0), None]
            },
            service_distributions={
                'Class 0': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.1)],
                'Class 1': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.1)]
            },
            number_of_servers=[1, 1],
            priority_classes=({'Class 0': 0, 'Class 1': 1}, ['reroute', False]),
            routing={
                'Class 0': ciw.routing.TransitionMatrix(transition_matrix=[[0.0, 1.0], [0.0, 0.0]]),
                'Class 1': ciw.routing.TransitionMatrix(transition_matrix=[[0.0, 1.0], [0.0, 0.0]])
            }
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(2.7)
        recs = Q.get_all_records()

        nd_1 = sorted([r for r in recs if r.node == 1], key=lambda r: r.arrival_date)
        self.assertEqual([round(r.arrival_date, 5) for r in nd_1], [0.7, 1.0, 1.4, 2.0, 2.1])
        self.assertEqual([round(r.service_time, 5) for r in nd_1], [0.2, 0.2, 0.2, 0.2, 0.2])
        self.assertEqual([round(r.exit_date, 5) for r in nd_1], [0.9, 1.2, 1.6, 2.1, 2.3])
        self.assertEqual([r.destination for r in nd_1], [2, 2, 2, 2, 2])
        self.assertEqual([r.record_type for r in nd_1], ['service', 'service', 'service', 'interrupted service', 'service'])

        nd_2 = sorted([r for r in recs if r.node == 2], key=lambda r: r.arrival_date)
        self.assertEqual([round(r.arrival_date, 5) for r in nd_2], [0.9, 1.2, 1.6, 2.1, 2.3])
        self.assertEqual([round(r.service_time, 5) for r in nd_2], [0.1, 0.1, 0.1, 0.1, 0.1])
        self.assertEqual([round(r.exit_date, 5) for r in nd_2], [1.0, 1.3, 1.7, 2.2, 2.4])
        self.assertEqual([r.destination for r in nd_2], [-1, -1, -1, -1, -1])
        self.assertEqual([r.record_type for r in nd_2], ['service', 'service', 'service', 'service', 'service'])

    def test_reroute_preemption_classpriorities_process_based(self):
        """
        Class 0 arrive to Node 1 every 0.7, service lasts 0.2
        Class 1 arrive to Node 1 every 1.0, service lasts 0.2
        Class 0 have priority over class 1
        All classes go Node 1 then Node 2

        Node 1
        Ind    arr    clss    end
          1    0.7       0    0.9
          2    1.0       1    1.2
          3    1.4       0    1.6
          4    2.0       1    interrupted
          5    2.1       0    2.3

        Node 2
        Ind    arr    clss    end
          1    0.9       0    1.0
          2    1.2       1    1.3
          3    1.6       0    1.7
          4    2.1       1    2.2
          5    2.3       0    2.4
        """
        def from_1_to_2(ind, simulation):
            return [2]

        N = ciw.create_network(
            arrival_distributions={
                'Class 0': [ciw.dists.Deterministic(value=0.7), None],
                'Class 1': [ciw.dists.Deterministic(value=1.0), None]
            },
            service_distributions={
                'Class 0': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.1)],
                'Class 1': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.1)]
            },
            number_of_servers=[1, 1],
            priority_classes=({'Class 0': 0, 'Class 1': 1}, ['reroute', False]),
            routing={
                'Class 0': ciw.routing.ProcessBased(from_1_to_2),
                'Class 1': ciw.routing.ProcessBased(from_1_to_2)
            }
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(2.7)
        recs = Q.get_all_records()

        nd_1 = sorted([r for r in recs if r.node == 1], key=lambda r: r.arrival_date)
        self.assertEqual([round(r.arrival_date, 5) for r in nd_1], [0.7, 1.0, 1.4, 2.0, 2.1])
        self.assertEqual([round(r.service_time, 5) for r in nd_1], [0.2, 0.2, 0.2, 0.2, 0.2])
        self.assertEqual([round(r.exit_date, 5) for r in nd_1], [0.9, 1.2, 1.6, 2.1, 2.3])
        self.assertEqual([r.destination for r in nd_1], [2, 2, 2, 2, 2])
        self.assertEqual([r.record_type for r in nd_1], ['service', 'service', 'service', 'interrupted service', 'service'])

        nd_2 = sorted([r for r in recs if r.node == 2], key=lambda r: r.arrival_date)
        self.assertEqual([round(r.arrival_date, 5) for r in nd_2], [0.9, 1.2, 1.6, 2.1, 2.3])
        self.assertEqual([round(r.service_time, 5) for r in nd_2], [0.1, 0.1, 0.1, 0.1, 0.1])
        self.assertEqual([round(r.exit_date, 5) for r in nd_2], [1.0, 1.3, 1.7, 2.2, 2.4])
        self.assertEqual([r.destination for r in nd_2], [-1, -1, -1, -1, -1])
        self.assertEqual([r.record_type for r in nd_2], ['service', 'service', 'service', 'service', 'service'])

    def test_rerouting_ignores_queue_capacities(self):
        """
        Class 0 arrive to Node 1 every 0.7, service lasts 0.2
        Class 1 arrive to Node 1 every 1.0, service lasts 0.2
        Class 0 have priority over class 1
        Class 1 rerouted to Node 2 upon preemption
        Class 2 arrive at Node 2 every 0.6
        
        Node 1
        Ind    arr    clss    end
          2    0.7       0    0.9
          3    1.0       1    1.2
          5    1.4       0    1.6
          6    2.0       1    interrupted (goes to Node 2 for 0.5)
          7    2.1       0    2.3

        Node 2
        Ind    arr    clss    end
          1    0.6       2    1.3
          4    1.2       2    rejected
          3    1.8       2    2.5
          6    2.1       1    (2.5 + 0.7 =) 3.2 (individual is accepted even though a queue capacity of 0)
          8    2.4       2    rejected
        """
        class Reroute(ciw.routing.NodeRouting):
            def next_node(self, ind):
                """
                Chooses the exit node with probability 1.
                """
                return self.simulation.nodes[-1]

            def next_node_for_rerouting(self, ind):
                """
                Chooses Node 2
                """
                return self.simulation.nodes[2]

        N = ciw.create_network(
            arrival_distributions={
                'Class 0': [ciw.dists.Deterministic(value=0.7), None],
                'Class 1': [ciw.dists.Deterministic(value=1.0), None],
                'Class 2': [None, ciw.dists.Deterministic(value=0.6)]
            },
            service_distributions={
                'Class 0': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.7)],
                'Class 1': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.7)],
                'Class 2': [ciw.dists.Deterministic(value=0.2), ciw.dists.Deterministic(value=0.7)]
            },
            number_of_servers=[1, 1],
            queue_capacities=[float('inf'), 0],
            priority_classes=({'Class 0': 0, 'Class 1': 1, 'Class 2': 1}, ['reroute', False]),
            routing={
                'Class 0': ciw.routing.NetworkRouting(routers=[ciw.routing.Leave(), ciw.routing.Leave()]),
                'Class 1': ciw.routing.NetworkRouting(routers=[Reroute(), ciw.routing.Leave()]),
                'Class 2': ciw.routing.NetworkRouting(routers=[ciw.routing.Leave(), ciw.routing.Leave()])
            }
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(3.3)
        recs = Q.get_all_records()

        nd_1 = sorted([r for r in recs if r.node == 1], key=lambda r: r.arrival_date)[:5]
        self.assertEqual([round(r.arrival_date, 5) for r in nd_1], [0.7, 1.0, 1.4, 2.0, 2.1])
        self.assertEqual([round(r.service_time, 5) for r in nd_1], [0.2, 0.2, 0.2, 0.2, 0.2])
        self.assertEqual([round(r.exit_date, 5) for r in nd_1], [0.9, 1.2, 1.6, 2.1, 2.3])
        self.assertEqual([r.destination for r in nd_1], [-1, -1, -1, 2, -1])
        self.assertEqual([r.record_type for r in nd_1], ['service', 'service', 'service', 'interrupted service', 'service'])

        nd_2 = sorted([r for r in recs if r.node == 2], key=lambda r: r.arrival_date)[:5]
        self.assertEqual([round(r.arrival_date, 5) for r in nd_2], [0.6, 1.2, 1.8, 2.1, 2.4])
        self.assertEqual([str(round(r.service_time, 5)) for r in nd_2], ['0.7', 'nan', '0.7', '0.7', 'nan'])
        self.assertEqual([round(r.exit_date, 5) for r in nd_2], [1.3, 1.2, 2.5, 3.2, 2.4])
        self.assertEqual([str(r.destination) for r in nd_2], ['-1', 'nan', '-1', '-1', 'nan'])
        self.assertEqual([r.record_type for r in nd_2], ['service', 'rejection', 'service', 'service', 'rejection'])

    def test_reroute_at_shift_change(self):
        """
        Two nodes: arrivals to Node 1 every 1 time unit; service lasts 0.4 time units.
        One server on duty from - to 4.2; 0 from 4.2 to 6.1; 1 from 6.1 to 100.
        Interrupted individuals go to node 2, have service time 1.

        Node 1
        Ind    arr    exit
          1    1.0     1.4
          2    2.0     2.4
          3    3.0     4.4
          4    4.0     4.2 (interrupted)
          5    5.0     6.5 (service started at 6.1 when server back on duty)
          6    6.0     6.9 (service starts after ind 5 finishes service)
          7    7.0     7.4

        Node 2
        Ind    arr    exit
          4    4.2     5.2
        """
        class Reroute(ciw.routing.NodeRouting):
            def next_node(self, ind):
                """
                Chooses the exit node with probability 1.
                """
                return self.simulation.nodes[-1]

            def next_node_for_rerouting(self, ind):
                """
                Chooses Node 2
                """
                return self.simulation.nodes[2]

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(value=1.0), None],
            service_distributions=[ciw.dists.Deterministic(value=0.4), ciw.dists.Deterministic(value=1.0)],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 1], shift_end_dates=[4.2, 6.1, 100], preemption="reroute"), 1],
            routing=ciw.routing.NetworkRouting(routers=[Reroute(), ciw.routing.Leave()])
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(7.5)

        recs = Q.get_all_records()
        nd_1 = sorted([r for r in recs if r.node == 1], key=lambda r: r.arrival_date)
        self.assertEqual([round(r.arrival_date, 5) for r in nd_1], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
        self.assertEqual([round(r.service_time, 5) for r in nd_1], [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4])
        self.assertEqual([round(r.exit_date, 5) for r in nd_1], [1.4, 2.4, 3.4, 4.2, 6.5, 6.9, 7.4])
        self.assertEqual([r.destination for r in nd_1], [-1, -1, -1, 2, -1, -1, -1])
        self.assertEqual([r.record_type for r in nd_1], ['service', 'service', 'service', 'interrupted service', 'service', 'service', 'service'])

        nd_2 = sorted([r for r in recs if r.node == 2], key=lambda r: r.arrival_date)
        self.assertEqual([round(r.arrival_date, 5) for r in nd_2], [4.2])
        self.assertEqual([round(r.service_time, 5) for r in nd_2], [1.0])
        self.assertEqual([round(r.exit_date, 5) for r in nd_2], [5.2])
        self.assertEqual([r.destination for r in nd_2], [-1])
        self.assertEqual([r.record_type for r in nd_2], ['service'])


class TestServiceDisciplines(unittest.TestCase):
    def test_first_in_first_out(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(1.5)],
            service_disciplines=[ciw.disciplines.FIFO],
            number_of_servers=[1],
        )
        self.assertTrue(
            isinstance(N.service_centres[0].service_discipline, types.FunctionType)
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(9)
        recs = sorted(Q.get_all_records(), key=lambda dr: dr.service_start_date)
        self.assertEqual([r.id_number for r in recs], [1, 2, 3, 4, 5])
        self.assertEqual([r.arrival_date for r in recs], [1.0, 2.0, 3.0, 4.0, 5.0])
        self.assertEqual([r.service_time for r in recs], [1.5, 1.5, 1.5, 1.5, 1.5])
        self.assertEqual([r.service_end_date for r in recs], [2.5, 4.0, 5.5, 7.0, 8.5])

    def test_service_in_random_order(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(2.5)],
            service_disciplines=[ciw.disciplines.SIRO],
            number_of_servers=[1],
        )
        self.assertTrue(isinstance(N.service_centres[0].service_discipline, types.FunctionType))
        ciw.seed(1)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(14)
        recs = sorted(Q.get_all_records(), key=lambda dr: dr.service_start_date)
        self.assertEqual([r.id_number for r in recs], [1, 2, 5, 6, 4])
        self.assertEqual([r.arrival_date for r in recs], [1.0, 2.0, 5.0, 6.0, 4.0])
        self.assertEqual([r.service_time for r in recs], [2.5, 2.5, 2.5, 2.5, 2.5])
        self.assertEqual(
            [r.service_end_date for r in recs],
            [3.5, 6.0, 8.5, 11.0, 13.5]
        )

    def test_last_in_first_out(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(1.6)],
            service_disciplines=[ciw.disciplines.LIFO],
            number_of_servers=[1],
        )
        self.assertTrue(isinstance(N.service_centres[0].service_discipline, types.FunctionType))
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(9.5)
        recs = sorted(Q.get_all_records(), key=lambda dr: dr.service_start_date)
        self.assertEqual([r.id_number for r in recs], [1, 2, 4, 5, 7])
        self.assertEqual([r.arrival_date for r in recs], [1.0, 2.0, 4.0, 5.0, 7.0])
        self.assertEqual(
            [round(r.service_time, 10) for r in recs],
            [1.6, 1.6, 1.6, 1.6, 1.6]
        )
        self.assertEqual(
            [round(r.service_end_date, 10) for r in recs],
            [2.6, 4.2, 5.8, 7.4, 9.0]
        )

    def test_mixed_service_disciplines(self):
        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Deterministic(1),
                ciw.dists.Deterministic(0.7),
            ],
            service_distributions=[
                ciw.dists.Deterministic(2.1),
                ciw.dists.Deterministic(3),
            ],
            service_disciplines=[ciw.disciplines.FIFO, ciw.disciplines.LIFO],
            routing=[[0.0, 1.0], [0.0, 0.0]],
            number_of_servers=[1, 1],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(9.9)
        recs = sorted(Q.get_all_records(), key=lambda dr: dr.service_start_date)
        recs_n1 = [r for r in recs if r.node == 1]
        recs_n2 = [r for r in recs if r.node == 2]

        self.assertEqual([r.id_number for r in recs_n1], [2, 4, 7, 9])
        self.assertEqual(
            [round(r.arrival_date, 10) for r in recs_n1],
            [1.0, 2.0, 3.0, 4.0]
        )
        self.assertEqual(
            [round(r.service_end_date, 10) for r in recs_n1],
            [3.1, 5.2, 7.3, 9.4]
        )

        self.assertEqual([r.id_number for r in recs_n2], [1, 8, 15])
        self.assertEqual([round(r.arrival_date, 10) for r in recs_n2], [0.7, 3.5, 6.3])
        self.assertEqual(
            [round(r.service_end_date, 10) for r in recs_n2],
            [3.7, 6.7, 9.7]
        )


    def test_custom_service_discipline(self):
        """
        First test for a given linger time, no person waited less than the linger time.
        """
        def linger(individuals, t):
            individuals_who_lingered = [ind for ind in individuals if (t - ind.arrival_date) >= 3]
            if len(individuals_who_lingered) == 0:
                return None
            return individuals_who_lingered[0]

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(3)],
            service_distributions=[ciw.dists.Exponential(5)],
            number_of_servers=[1],
            service_disciplines=[linger]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(100)
        recs = Q.get_all_records()
        waits = [r.waiting_time for r in recs]
        self.assertTrue(min(waits) >= 3)

        """
        Now test a specific example:
        Customers arrive every 1.31
        Services last 1.9 and 0.2 alternatively
        Customers must linger for at least 3

        ID  Arrive  Linger  Start  Service    End
        -----------------------------------------
        1    01.31   04.31  05.24      1.9  07.14
        2    02.62   05.62  07.14      0.2  07.34
        3    03.93   06.93  07.34      1.9  09.24
        4    05.24   08.24  09.24      0.2  09.44
        5    06.55   09.55  10.48      1.9  12.38
        6    07.86   10.86  12.38      0.2  12.58
        7    09.17   12.17  12.58      1.9  14.48
        8    10.48   13.48  14.48      0.2  14.68
        -----------------------------------------
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(value=1.31)],
            service_distributions=[ciw.dists.Sequential([1.9, 0.2])],
            number_of_servers=[1],
            service_disciplines=[linger]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(8, method='Finish')
        recs = Q.get_all_records()
        self.assertEqual(len(recs), 8)

        arrivals = [round(r.arrival_date, 2) for r in recs]
        start_dates = [round(r.service_start_date, 2) for r in recs]
        end_dates = [round(r.service_end_date, 2) for r in recs]

        self.assertEqual(arrivals, [1.31, 2.62, 3.93, 5.24, 6.55, 7.86, 9.17, 10.48])
        self.assertEqual(start_dates, [5.24, 7.14, 7.34, 9.24, 10.48, 12.38, 12.58, 14.48])
        self.assertEqual(end_dates, [7.14, 7.34, 9.24, 9.44, 12.38, 12.58, 14.48, 14.68])


    def test_names_for_customer_classes(self):
        N = ciw.create_network(
            arrival_distributions={
                'Adult': [ciw.dists.Exponential(3), None],
                'Child': [ciw.dists.Exponential(2), ciw.dists.Exponential(0.5)]
            },
            service_distributions={
                'Adult': [ciw.dists.Exponential(6), ciw.dists.Exponential(6)],
                'Child': [ciw.dists.Exponential(4), ciw.dists.Exponential(4)]
            },
            routing={
                'Adult': [[0.0, 1.0], [0.0, 0.0]],
                'Child': [[0.0, 0.5], [0.0, 0.0]]
            },
            number_of_servers=[3, 4]
        )
        ciw.seed(5)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records()
        adult_waits = [r.waiting_time for r in recs if r.customer_class=='Adult']
        child_waits = [r.waiting_time for r in recs if r.customer_class=='Child']
        mean_adult_wait = sum(adult_waits) / len(adult_waits)
        mean_child_wait = sum(child_waits) / len(child_waits)
        self.assertEqual(round(mean_adult_wait, 8), 0.00301455)
        self.assertEqual(round(mean_child_wait, 8), 0.00208601)

