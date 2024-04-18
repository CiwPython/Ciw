import unittest
import ciw
from collections import Counter

N = ciw.create_network(
    arrival_distributions=[
        ciw.dists.Exponential(rate=1.0),
        ciw.dists.Exponential(rate=1.0),
        ciw.dists.Exponential(rate=1.0),
    ],
    service_distributions=[
        ciw.dists.Exponential(rate=2.0),
        ciw.dists.Exponential(rate=2.0),
        ciw.dists.Exponential(rate=2.0),
    ],
    number_of_servers=[1, 2, 2],
    routing=[
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0]
    ]
)

class TestRouting(unittest.TestCase):
    def test_generic_network_router(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R = ciw.routing.NodeRouting()
        R.initialise(Q, 1)
        self.assertEqual(R.simulation, Q)
        self.assertEqual(R.node, 1)


    def test_probabilistic_routing(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.Probabilistic(destinations=[1, 2, 3], probs=[0.6, 0.3, 0.1])
        R2 = ciw.routing.Probabilistic(destinations=[1, 2, 3], probs=[0.0, 0.0, 0.3])
        R3 = ciw.routing.Probabilistic(destinations=[1, 2, 3], probs=[0.33, 0.34, 0.33])
        R1.initialise(Q, 1)
        R2.initialise(Q, 2)
        R3.initialise(Q, 3)
        ind = ciw.Individual(1)
        samples_1 = Counter([r.id_number for r in [R1.next_node(ind) for _ in range(10000)]])
        samples_2 = Counter([r.id_number for r in [R2.next_node(ind) for _ in range(10000)]])
        samples_3 = Counter([r.id_number for r in [R3.next_node(ind) for _ in range(10000)]])
        self.assertEqual([samples_1[i] for i in [1, 2, 3, -1]], [5976, 3067, 957, 0])
        self.assertEqual([samples_2[i] for i in [1, 2, 3, -1]], [0, 0, 3019, 6981])
        self.assertEqual([samples_3[i] for i in [1, 2, 3, -1]], [3278, 3444, 3278, 0])

    def test_network_routing(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R = ciw.routing.NetworkRouting(routers=[
            ciw.routing.Probabilistic(destinations=[1, 2, 3], probs=[0.6, 0.3, 0.1]),
            ciw.routing.Probabilistic(destinations=[1, 2, 3], probs=[0.0, 0.0, 0.3]),
            ciw.routing.Probabilistic(destinations=[1, 2, 3], probs=[0.33, 0.34, 0.33])
        ])
        R.initialise(Q)
        ind = ciw.Individual(1)
        samples_1 = Counter([r.id_number for r in [R.next_node(ind, 1) for _ in range(10000)]])
        samples_2 = Counter([r.id_number for r in [R.next_node(ind, 2) for _ in range(10000)]])
        samples_3 = Counter([r.id_number for r in [R.next_node(ind, 3) for _ in range(10000)]])
        self.assertEqual([samples_1[i] for i in [1, 2, 3, -1]], [5976, 3067, 957, 0])
        self.assertEqual([samples_2[i] for i in [1, 2, 3, -1]], [0, 0, 3019, 6981])
        self.assertEqual([samples_3[i] for i in [1, 2, 3, -1]], [3278, 3444, 3278, 0])

    def test_transition_matrix_router(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R = ciw.routing.TransitionMatrix(transition_matrix=[
            [0.6, 0.3, 0.1],
            [0.0, 0.0, 0.3],
            [0.33, 0.34, 0.33]
        ])
        R.initialise(Q)
        ind = ciw.Individual(1)
        samples_1 = Counter([r.id_number for r in [R.next_node(ind, 1) for _ in range(10000)]])
        samples_2 = Counter([r.id_number for r in [R.next_node(ind, 2) for _ in range(10000)]])
        samples_3 = Counter([r.id_number for r in [R.next_node(ind, 3) for _ in range(10000)]])
        self.assertEqual([samples_1[i] for i in [1, 2, 3, -1]], [5976, 3067, 957, 0])
        self.assertEqual([samples_2[i] for i in [1, 2, 3, -1]], [0, 0, 3019, 6981])
        self.assertEqual([samples_3[i] for i in [1, 2, 3, -1]], [3278, 3444, 3278, 0])
