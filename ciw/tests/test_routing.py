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


    def test_direct_routing(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.Direct(to=3)
        R2 = ciw.routing.Direct(to=1)
        R3 = ciw.routing.Direct(to=2)
        R1.initialise(Q, 1)
        R2.initialise(Q, 2)
        R3.initialise(Q, 3)
        ind = ciw.Individual(1)
        samples_1 = [r.id_number for r in [R1.next_node(ind) for _ in range(1000)]]
        samples_2 = [r.id_number for r in [R2.next_node(ind) for _ in range(1000)]]
        samples_3 = [r.id_number for r in [R3.next_node(ind) for _ in range(1000)]]
        self.assertTrue(all(r == 3 for r in samples_1))
        self.assertTrue(all(r == 1 for r in samples_2))
        self.assertTrue(all(r == 2 for r in samples_3))


    def test_leave_routing(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R = ciw.routing.Leave()
        R.initialise(Q, 1)
        ind = ciw.Individual(1)
        samples = [r.id_number for r in [R.next_node(ind) for _ in range(1000)]]
        self.assertTrue(all(r == -1 for r in samples))


    def test_join_shortest_queue(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.JoinShortestQueue(destinations=[1, 2, 3])
        R2 = ciw.routing.JoinShortestQueue(destinations=[1, 3])
        R3 = ciw.routing.JoinShortestQueue(destinations=[2, 3])
        R1.initialise(Q, 1)
        R2.initialise(Q, 2)
        R3.initialise(Q, 3)
        ind = ciw.Individual(1)
        Q.nodes[1].number_of_individuals = 10
        Q.nodes[1].number_in_service = 1
        Q.nodes[2].number_of_individuals = 20
        Q.nodes[2].number_in_service = 2
        Q.nodes[3].number_of_individuals = 40
        Q.nodes[3].number_in_service = 2
        samples_1 = [r.id_number for r in [R1.next_node(ind) for _ in range(1000)]]
        samples_2 = [r.id_number for r in [R2.next_node(ind) for _ in range(1000)]]
        samples_3 = [r.id_number for r in [R3.next_node(ind) for _ in range(1000)]]
        self.assertTrue(all(r == 1 for r in samples_1))
        self.assertTrue(all(r == 1 for r in samples_2))
        self.assertTrue(all(r == 2 for r in samples_3))

    def test_join_shortest_queue_tiebreaks(self):
        """
        There is a tie between nodes 2 and 3
        """
        # Default tie-break (random)
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.JoinShortestQueue(destinations=[1, 2, 3])
        R2 = ciw.routing.JoinShortestQueue(destinations=[1, 3])
        R3 = ciw.routing.JoinShortestQueue(destinations=[3, 2])
        R1.initialise(Q, 1)
        R2.initialise(Q, 2)
        R3.initialise(Q, 3)
        ind = ciw.Individual(1)
        Q.nodes[1].number_of_individuals = 60
        Q.nodes[1].number_in_service = 1
        Q.nodes[2].number_of_individuals = 20
        Q.nodes[2].number_in_service = 2
        Q.nodes[3].number_of_individuals = 20
        Q.nodes[3].number_in_service = 2
        samples_1 = Counter([r.id_number for r in [R1.next_node(ind) for _ in range(1000)]])
        samples_2 = Counter([r.id_number for r in [R2.next_node(ind) for _ in range(1000)]])
        samples_3 = Counter([r.id_number for r in [R3.next_node(ind) for _ in range(1000)]])
        self.assertEqual([samples_1[i] for i in [1, 2, 3, -1]], [0, 507, 493, 0])
        self.assertEqual([samples_2[i] for i in [1, 2, 3, -1]], [0, 0, 1000, 0])
        self.assertEqual([samples_3[i] for i in [1, 2, 3, -1]], [0, 516, 484, 0])

        # Explicitly set random tie-break
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.JoinShortestQueue(destinations=[1, 2, 3], tie_break="random")
        R2 = ciw.routing.JoinShortestQueue(destinations=[1, 3], tie_break="random")
        R3 = ciw.routing.JoinShortestQueue(destinations=[3, 2], tie_break="random")
        R1.initialise(Q, 1)
        R2.initialise(Q, 2)
        R3.initialise(Q, 3)
        ind = ciw.Individual(1)
        Q.nodes[1].number_of_individuals = 60
        Q.nodes[1].number_in_service = 1
        Q.nodes[2].number_of_individuals = 20
        Q.nodes[2].number_in_service = 2
        Q.nodes[3].number_of_individuals = 20
        Q.nodes[3].number_in_service = 2
        samples_1 = Counter([r.id_number for r in [R1.next_node(ind) for _ in range(1000)]])
        samples_2 = Counter([r.id_number for r in [R2.next_node(ind) for _ in range(1000)]])
        samples_3 = Counter([r.id_number for r in [R3.next_node(ind) for _ in range(1000)]])
        self.assertEqual([samples_1[i] for i in [1, 2, 3, -1]], [0, 507, 493, 0])
        self.assertEqual([samples_2[i] for i in [1, 2, 3, -1]], [0, 0, 1000, 0])
        self.assertEqual([samples_3[i] for i in [1, 2, 3, -1]], [0, 516, 484, 0])

        # Explicitly set ordered tie-break
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.JoinShortestQueue(destinations=[1, 2, 3], tie_break="order")
        R2 = ciw.routing.JoinShortestQueue(destinations=[1, 3], tie_break="order")
        R3 = ciw.routing.JoinShortestQueue(destinations=[3, 2], tie_break="order")
        R1.initialise(Q, 1)
        R2.initialise(Q, 2)
        R3.initialise(Q, 3)
        ind = ciw.Individual(1)
        Q.nodes[1].number_of_individuals = 60
        Q.nodes[1].number_in_service = 1
        Q.nodes[2].number_of_individuals = 20
        Q.nodes[2].number_in_service = 2
        Q.nodes[3].number_of_individuals = 20
        Q.nodes[3].number_in_service = 2
        samples_1 = Counter([r.id_number for r in [R1.next_node(ind) for _ in range(1000)]])
        samples_2 = Counter([r.id_number for r in [R2.next_node(ind) for _ in range(1000)]])
        samples_3 = Counter([r.id_number for r in [R3.next_node(ind) for _ in range(1000)]])
        self.assertTrue(all(r == 2 for r in samples_1))
        self.assertTrue(all(r == 3 for r in samples_2))
        self.assertTrue(all(r == 3 for r in samples_3))


    def test_jsq_raises_errors(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.JoinShortestQueue(destinations=[1, 2, 7])
        self.assertRaises(ValueError, R1.initialise, Q, 1)


    def test_jsq_in_simulation(self):
        """
        First consider a 2 node system, and one dummy node. The
        dummy node is where all customers arrive, and routes customers
        to the other nodes in a 50%-50% schema.
        """
        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(rate=3.0),
                None,
                None,
            ],
            service_distributions=[
                ciw.dists.Deterministic(value=0.0),
                ciw.dists.Exponential(rate=2.0),
                ciw.dists.Exponential(rate=2.0),
            ],
            number_of_servers=[float('inf'), 1, 1],
            routing=ciw.routing.NetworkRouting(routers=[
                ciw.routing.Probabilistic(destinations=[2, 3], probs=[0.5, 0.5]),
                ciw.routing.Leave(),
                ciw.routing.Leave()
            ])
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(100)
        recs = Q.get_all_records()
        waits_2 = [r.waiting_time for r in recs if r.node == 2]
        waits_3 = [r.waiting_time for r in recs if r.node == 3]
        self.assertEqual(round(sum(waits_2) / len(waits_2), 6), 0.941912)
        self.assertEqual(round(sum(waits_3) / len(waits_3), 6), 2.209535)
        self.assertEqual(round(max(waits_2), 6), 4.588178)
        self.assertEqual(round(max(waits_3), 6), 8.652946)
        """
        Now consider a 2 node system, and one dummy node. The
        dummy node is where all customers arrive, and routes customers
        to the other nodes with JSQ.
        The average, and maximum waitint times are both lowered.
        """
        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(rate=3.0),
                None,
                None,
            ],
            service_distributions=[
                ciw.dists.Deterministic(value=0.0),
                ciw.dists.Exponential(rate=2.0),
                ciw.dists.Exponential(rate=2.0),
            ],
            number_of_servers=[float('inf'), 1, 1],
            routing=ciw.routing.NetworkRouting(routers=[
                ciw.routing.JoinShortestQueue(destinations=[2, 3]),
                ciw.routing.Leave(),
                ciw.routing.Leave()
            ])
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(100)
        recs = Q.get_all_records()
        waits_2 = [r.waiting_time for r in recs if r.node == 2]
        waits_3 = [r.waiting_time for r in recs if r.node == 3]
        self.assertEqual(round(sum(waits_2) / len(waits_2), 6), 0.536455)
        self.assertEqual(round(sum(waits_3) / len(waits_3), 6), 0.531789)
        self.assertEqual(round(max(waits_2), 6), 2.777136)
        self.assertEqual(round(max(waits_3), 6), 2.507875)


    def test_load_balancing(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.LoadBalancing(destinations=[1, 2, 3])
        R2 = ciw.routing.LoadBalancing(destinations=[1, 3])
        R3 = ciw.routing.LoadBalancing(destinations=[2, 3])
        R1.initialise(Q, 1)
        R2.initialise(Q, 2)
        R3.initialise(Q, 3)
        ind = ciw.Individual(1)
        Q.nodes[1].number_of_individuals = 3
        Q.nodes[1].number_in_service = 1
        Q.nodes[2].number_of_individuals = 3
        Q.nodes[2].number_in_service = 2
        Q.nodes[3].number_of_individuals = 10
        Q.nodes[3].number_in_service = 2
        samples_1 = Counter([r.id_number for r in [R1.next_node(ind) for _ in range(1000)]])
        samples_2 = [r.id_number for r in [R2.next_node(ind) for _ in range(1000)]]
        samples_3 = [r.id_number for r in [R3.next_node(ind) for _ in range(1000)]]
        self.assertEqual([samples_1[i] for i in [1, 2, 3, -1]], [507, 493, 0, 0])
        self.assertTrue(all(r == 1 for r in samples_2))
        self.assertTrue(all(r == 2 for r in samples_3))


    def test_cycle_routing(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.Cycle(cycle=[2, 3, 3])
        R2 = ciw.routing.Cycle(cycle=[1, 2])
        R3 = ciw.routing.Cycle(cycle=[1, -1, 2, -1])
        R1.initialise(Q, 1)
        R2.initialise(Q, 2)
        R3.initialise(Q, 3)
        ind = ciw.Individual(1)
        samples_1 = [r.id_number for r in [R1.next_node(ind) for _ in range(20)]]
        samples_2 = [r.id_number for r in [R2.next_node(ind) for _ in range(20)]]
        samples_3 = [r.id_number for r in [R3.next_node(ind) for _ in range(20)]]
        self.assertEqual([2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 3], samples_1)
        self.assertEqual([1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2], samples_2)
        self.assertEqual([1, -1, 2, -1, 1, -1, 2, -1, 1, -1, 2, -1, 1, -1, 2, -1, 1, -1, 2, -1], samples_3)

    def test_cycle_routing_raises_errors(self):
        ciw.seed(0)
        Q = ciw.Simulation(N)
        R1 = ciw.routing.Cycle(cycle=[1, 2, 7])
        self.assertRaises(ValueError, R1.initialise, Q, 1)
