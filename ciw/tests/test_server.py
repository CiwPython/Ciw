import unittest
import ciw
from hypothesis import given
from hypothesis.strategies import integers

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


class TestServer(unittest.TestCase):
    def test_init_method(self):
        Q = ciw.Simulation(N_params)
        N = Q.transitive_nodes[1]
        s = ciw.Server(N, 3)
        self.assertEqual(s.id_number, 3)
        self.assertEqual(s.node, N)
        self.assertEqual(s.node.id_number, 2)
        self.assertEqual(s.cust, False)
        self.assertEqual(s.busy, False)
        self.assertEqual(s.offduty, False)

    def test_repr_method(self):
        Q = ciw.Simulation(N_params)
        N = Q.transitive_nodes[0]
        s = ciw.Server(N, 4)
        self.assertEqual(str(s), "Server 4 at Node 1")

    def test_busy_total_times(self):
        # Single server
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 3.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([1.0, 6.0, 100.0])],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(14.0)
        s = Q.nodes[1].servers[0]
        self.assertEqual(s.total_time, 14.0)
        self.assertEqual(s.busy_time, 7.0)
        self.assertEqual(s.utilisation, 0.5)

        # Multi server
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 3.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([10.0, 6.0, 100.0])],
            number_of_servers=[3],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20.0)
        s1, s2, s3 = Q.nodes[1].servers
        self.assertEqual(s1.total_time, 20.0)
        self.assertEqual(s1.busy_time, 10.0)
        self.assertEqual(s1.utilisation, 0.5)
        self.assertEqual(s2.total_time, 20.0)
        self.assertEqual(s2.busy_time, 6.0)
        self.assertEqual(s2.utilisation, 0.3)
        self.assertEqual(s3.total_time, 20.0)
        self.assertEqual(s3.busy_time, 0.0)
        self.assertEqual(s3.utilisation, 0.0)

        # Until deadlock
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([3.0, 3.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([1.0, 6.0, 100.0])],
            number_of_servers=[1],
            queue_capacities=[0],
            routing=[[1.0]],
        )
        Q = ciw.Simulation(N, deadlock_detector=ciw.deadlock.StateDigraph())
        Q.simulate_until_deadlock()
        s = Q.nodes[1].servers[0]
        self.assertEqual(s.total_time, 4.0)
        self.assertEqual(s.busy_time, 1.0)
        self.assertEqual(s.utilisation, 0.25)

        # Until max customers
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 1.0, 7.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([5.0, 2.0, 2.0, 100.0])],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(3, method="Arrive")
        s = Q.nodes[1].servers[0]
        self.assertEqual(s.total_time, 10.0)
        self.assertEqual(s.busy_time, 7.0)
        self.assertEqual(s.utilisation, 0.7)
