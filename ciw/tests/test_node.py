import unittest
import ciw
from hypothesis import given, settings
from hypothesis.strategies import floats, integers, random_module
from math import nan, isnan

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
    service_distributions=[ciw.dists.Exponential(30.0), ciw.dists.Exponential(30.0)],
    routing=[[0.3, 0.4], [0.4, 0.3]],
)

N_priorities = ciw.create_network(
    arrival_distributions={
        "Class 0": [ciw.dists.Exponential(0.05), ciw.dists.Exponential(0.04)],
        "Class 1": [ciw.dists.Exponential(0.04), ciw.dists.Exponential(0.06)],
    },
    number_of_servers=[4, 3],
    queue_capacities=[float("inf"), 10],
    service_distributions={
        "Class 0": [ciw.dists.Deterministic(5.0), ciw.dists.Deterministic(5.0)],
        "Class 1": [ciw.dists.Deterministic(10.0), ciw.dists.Deterministic(10.0)],
    },
    routing={"Class 0": [[0.8, 0.1], [0.0, 0.0]], "Class 1": [[0.8, 0.1], [0.2, 0.0]]},
    priority_classes={"Class 0": 0, "Class 1": 1},
)


class TestNode(unittest.TestCase):
    def test_init_method(self):
        Q = ciw.Simulation(N_params)
        N = ciw.Node(1, Q)
        self.assertEqual(N.c, 9)
        self.assertEqual(N.next_event_date, float("inf"))
        self.assertEqual(N.all_individuals, [])
        self.assertEqual(N.id_number, 1)
        self.assertEqual(N.interrupted_individuals, [])
        self.assertFalse(N.reneging)

        Net = ciw.create_network(
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
        Q = ciw.Simulation(Net)
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.class_change, {'Class 0': {'Class 0': 0.5, 'Class 1': 0.5}, 'Class 1': {'Class 0': 0.5, 'Class 1': 0.5}})
        N2 = Q.transitive_nodes[1]
        self.assertEqual(N2.class_change, {'Class 0': {'Class 0': 1.0, 'Class 1': 0.0}, 'Class 1': {'Class 0': 0.0, 'Class 1': 1.0}})
        self.assertEqual(N.interrupted_individuals, [])

        N_schedule = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(0.05), ciw.dists.Exponential(0.04)],
                "Class 1": [ciw.dists.Exponential(0.04), ciw.dists.Exponential(0.06)],
            },
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 2, 1, 3], shift_end_dates=[30, 60, 90, 100]), 3],
            queue_capacities=[float("Inf"), 10],
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(5.0), ciw.dists.Exponential(0.2)],
                "Class 1": [ciw.dists.Deterministic(10.0), ciw.dists.Exponential(0.1)],
            },
            routing={
                "Class 0": [[0.8, 0.1], [0.0, 0.0]],
                "Class 1": [[0.8, 0.1], [0.2, 0.0]],
            },
        )
        Q = ciw.Simulation(N_schedule)
        N = Q.transitive_nodes[0]
        N.have_event()
        N.update_next_event_date()
        self.assertEqual(N.schedule.cyclelength, 100)
        self.assertEqual(N.c, 1)
        self.assertEqual(N.schedule.shift_end_dates, [30, 60, 90, 100])
        self.assertEqual(N.schedule.numbers_of_servers, [1, 2, 1, 3])
        self.assertEqual(N.next_event_date, 30)
        self.assertEqual(N.interrupted_individuals, [])
        self.assertFalse(N.reneging)

        Q = ciw.Simulation(N_priorities)
        N = Q.transitive_nodes[0]
        N.have_event()
        N.update_next_event_date()
        self.assertEqual(N.c, 4)
        self.assertEqual(Q.network.priority_class_mapping, {'Class 0': 0, 'Class 1': 1})
        self.assertEqual(Q.number_of_priority_classes, 2)
        self.assertEqual(N.interrupted_individuals, [])
        self.assertFalse(N.reneging)

    def test_repr_method(self):
        Q = ciw.Simulation(N_params)
        N1 = ciw.Node(1, Q)
        N2 = ciw.Node(2, Q)
        self.assertEqual(str(N1), "Node 1")
        self.assertEqual(str(N2), "Node 2")

    def test_finish_service_method(self):
        ciw.seed(4)
        Q = ciw.Simulation(N_params)
        N = Q.transitive_nodes[0]
        inds = [ciw.Individual(i + 1, 'Class 0') for i in range(3)]
        for current_time in [0.01, 0.02, 0.03]:
            Q.current_time = current_time
            N.accept(inds[int(current_time * 100 - 1)])
        self.assertEqual(
            [str(obs) for obs in N.all_individuals],
            ["Individual 1", "Individual 2", "Individual 3"],
        )
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [["Individual 1", "Individual 2", "Individual 3"]],
        )
        Q.current_time = 0.03
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.03604)
        N.finish_service()
        self.assertEqual(
            [str(obs) for obs in N.all_individuals], ["Individual 1", "Individual 3"]
        )
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [["Individual 1", "Individual 3"]],
        )

    def test_change_customer_class_method(self):
        ciw.seed(14)
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
        N1 = Q.transitive_nodes[0]
        ind = ciw.Individual(254, 'Class 0')
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.previous_class, 'Class 0')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.previous_class, 'Class 0')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.previous_class, 'Class 0')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.previous_class, 'Class 0')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.previous_class, 'Class 1')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.previous_class, 'Class 1')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.previous_class, 'Class 0')

        # Test for case of having priorities
        ciw.seed(14)
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(0.05), ciw.dists.Exponential(0.04)],
                "Class 1": [ciw.dists.Exponential(0.04), ciw.dists.Exponential(0.06)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(5), ciw.dists.Deterministic(5)],
                "Class 1": [ciw.dists.Deterministic(10), ciw.dists.Deterministic(10)],
            },
            routing={
                "Class 0": [[0.8, 0.1], [0.0, 0.0]],
                "Class 1": [[0.8, 0.1], [0.2, 0.0]],
            },
            number_of_servers=[4, 3],
            class_change_matrices=[
                {'Class 0': {'Class 0': 0.5, 'Class 1': 0.5}, 'Class 1': {'Class 0': 0.25, 'Class 1': 0.75}},
                {'Class 0': {'Class 0': 1, 'Class 1': 0}, 'Class 1': {'Class 0': 0, 'Class 1': 1}}
            ],
            priority_classes={"Class 0": 0, "Class 1": 1},
        )
        Q = ciw.Simulation(N)
        N1 = Q.transitive_nodes[0]
        ind = ciw.Individual(254, 'Class 0')
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 'Class 0')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 'Class 0')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 'Class 0')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 'Class 0')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 'Class 1')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 'Class 1')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 'Class 1')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 'Class 1')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 1')
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 'Class 1')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 'Class 1')
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 'Class 0')
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 'Class 0')

    def test_block_individual_method(self):
        ciw.seed(4)
        Q = ciw.Simulation(N_deadlock, deadlock_detector=ciw.deadlock.StateDigraph())
        inds = [ciw.Individual(i + 1) for i in range(7)]
        N1 = Q.transitive_nodes[0]
        N1.individuals = [inds[:6]]
        N2 = Q.transitive_nodes[1]
        Q.current_time = 2
        N2.accept(inds[6])
        self.assertEqual(inds[6].is_blocked, False)
        self.assertEqual(N1.blocked_queue, [])
        self.assertEqual(set(Q.deadlock_detector.statedigraph.edges()), set([]))
        N2.block_individual(inds[6], N1)
        self.assertEqual(inds[6].is_blocked, True)
        self.assertEqual(
            set(Q.deadlock_detector.statedigraph.edges()),
            set(
                [
                    ("Server 1 at Node 2", "Server 2 at Node 1"),
                    ("Server 1 at Node 2", "Server 5 at Node 1"),
                    ("Server 1 at Node 2", "Server 3 at Node 1"),
                    ("Server 1 at Node 2", "Server 1 at Node 1"),
                    ("Server 1 at Node 2", "Server 4 at Node 1"),
                ]
            ),
        )

    def test_release_method(self):
        ciw.seed(4)
        Q = ciw.Simulation(N_params)
        N = Q.transitive_nodes[0]
        inds = [ciw.Individual(i + 1, 'Class 0') for i in range(3)]
        for current_time in [0.01, 0.02, 0.03]:
            Q.current_time = current_time
            N.accept(inds[int(current_time * 100 - 1)])
        self.assertEqual(
            [str(obs) for obs in N.all_individuals],
            ["Individual 1", "Individual 2", "Individual 3"],
        )
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [["Individual 1", "Individual 2", "Individual 3"]],
        )
        Q.current_time = 0.03
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.03604)

        N.servers[1].next_end_service_date = float("inf")
        N.release(inds[1], Q.transitive_nodes[1])
        self.assertEqual(
            [str(obs) for obs in N.all_individuals], ["Individual 1", "Individual 3"]
        )
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [["Individual 1", "Individual 3"]],
        )
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.03708)

        N.servers[0].next_end_service_date = float("inf")
        N.release(inds[0], Q.transitive_nodes[1])
        self.assertEqual([str(obs) for obs in N.all_individuals], ["Individual 3"])
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [["Individual 3"]],
        )
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.06447)

    def test_begin_service_if_possible_release_method(self):
        ciw.seed(50)
        Q = ciw.Simulation(N_deadlock, deadlock_detector=ciw.deadlock.StateDigraph())
        inds = [[ciw.Individual(i) for i in range(30)]]
        Q.transitive_nodes[0].individuals = inds
        ind = Q.transitive_nodes[0].individuals[0][0]
        ind.arrival_date = 100.0
        self.assertEqual(
            set(Q.deadlock_detector.statedigraph.nodes()),
            set(
                [
                    "Server 5 at Node 2",
                    "Server 5 at Node 1",
                    "Server 3 at Node 2",
                    "Server 1 at Node 2",
                    "Server 1 at Node 1",
                    "Server 2 at Node 1",
                    "Server 2 at Node 2",
                    "Server 3 at Node 1",
                    "Server 4 at Node 1",
                    "Server 4 at Node 2",
                ]
            ),
        )
        self.assertEqual(ind.arrival_date, 100.0)
        self.assertEqual(ind.service_time, False)
        self.assertEqual(ind.service_start_date, False)
        self.assertEqual(ind.service_end_date, False)
        Q.current_time = 200.0
        Q.transitive_nodes[0].begin_service_if_possible_release(ind, Q.nodes[1].servers[0])
        self.assertEqual(ind.arrival_date, 100.0)
        self.assertEqual(round(ind.service_time, 5), 0.03382)
        self.assertEqual(ind.service_start_date, 200.0)
        self.assertEqual(round(ind.service_end_date, 5), 200.03382)

    def test_release_blocked_individual_method(self):
        Q = ciw.Simulation(N_deadlock, deadlock_detector=ciw.deadlock.StateDigraph())
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        N1.individuals = [[ciw.Individual(i) for i in range(N1.c + 3)]]
        N2.individuals = [[ciw.Individual(i + 100) for i in range(N2.c + 4)]]
        for ind in N1.all_individuals[:2]:
            N1.attach_server(N1.find_free_server(ind), ind)
        for ind in N2.all_individuals[:1]:
            N2.attach_server(N2.find_free_server(ind), ind)

        self.assertEqual(
            [str(obs) for obs in N1.all_individuals],
            [
                "Individual 0",
                "Individual 1",
                "Individual 2",
                "Individual 3",
                "Individual 4",
                "Individual 5",
                "Individual 6",
                "Individual 7",
            ],
        )
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals],
            [
                "Individual 100",
                "Individual 101",
                "Individual 102",
                "Individual 103",
                "Individual 104",
                "Individual 105",
                "Individual 106",
                "Individual 107",
                "Individual 108",
            ],
        )
        Q.current_time = 100
        N1.release_blocked_individual()
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals],
            [
                "Individual 0",
                "Individual 1",
                "Individual 2",
                "Individual 3",
                "Individual 4",
                "Individual 5",
                "Individual 6",
                "Individual 7",
            ],
        )
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals],
            [
                "Individual 100",
                "Individual 101",
                "Individual 102",
                "Individual 103",
                "Individual 104",
                "Individual 105",
                "Individual 106",
                "Individual 107",
                "Individual 108",
            ],
        )

        N1.blocked_queue = [(1, 1), (2, 100)]
        N1.len_blocked_queue = 2
        rel_ind = N1.individuals[0].pop(0)
        N1.detatch_server(rel_ind.server, rel_ind)

        Q.current_time = 110
        N1.release_blocked_individual()
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals],
            [
                "Individual 2",
                "Individual 3",
                "Individual 4",
                "Individual 5",
                "Individual 6",
                "Individual 7",
                "Individual 1",
                "Individual 100",
            ],
        )
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals],
            [
                "Individual 101",
                "Individual 102",
                "Individual 103",
                "Individual 104",
                "Individual 105",
                "Individual 106",
                "Individual 107",
                "Individual 108",
            ],
        )

    def test_accept_method(self):
        ciw.seed(6)
        Q = ciw.Simulation(N_params)
        N = Q.transitive_nodes[0]
        N.next_event_date = 0.0
        self.assertEqual(N.all_individuals, [])
        ind1 = ciw.Individual(1, customer_class='Class 0')
        ind2 = ciw.Individual(2, customer_class='Class 0')
        ind3 = ciw.Individual(3, customer_class='Class 0')
        ind4 = ciw.Individual(4, customer_class='Class 0')
        ind5 = ciw.Individual(5, customer_class='Class 0')
        ind6 = ciw.Individual(6, customer_class='Class 0')
        ind7 = ciw.Individual(7, customer_class='Class 0')
        ind8 = ciw.Individual(8, customer_class='Class 0')
        ind9 = ciw.Individual(9, customer_class='Class 0')
        ind10 = ciw.Individual(10, customer_class='Class 0')

        Q.current_time = 0.01
        N.accept(ind1)
        self.assertEqual([str(obs) for obs in N.all_individuals], ["Individual 1"])
        self.assertEqual(ind1.arrival_date, 0.01)
        self.assertEqual(ind1.service_start_date, 0.01)
        self.assertEqual(round(ind1.service_time, 5), 0.18695)
        self.assertEqual(round(ind1.service_end_date, 5), 0.19695)

        Q.current_time = 0.02
        N.accept(ind2)
        Q.current_time = 0.03
        N.accept(ind3)
        Q.current_time = 0.04
        N.accept(ind4)
        self.assertEqual(
            [str(obs) for obs in N.all_individuals],
            ["Individual 1", "Individual 2", "Individual 3", "Individual 4"],
        )
        self.assertEqual(round(ind4.arrival_date, 5), 0.04)
        self.assertEqual(round(ind4.service_start_date, 5), 0.04)
        self.assertEqual(round(ind4.service_time, 5), 0.1637)
        self.assertEqual(round(ind4.service_end_date, 5), 0.2037)

        Q.current_time = 0.05
        N.accept(ind5)
        Q.current_time = 0.06
        N.accept(ind6)
        Q.current_time = 0.07
        N.accept(ind7)
        Q.current_time = 0.08
        N.accept(ind8)
        Q.current_time = 0.09
        N.accept(ind9)
        Q.current_time = 0.1
        N.accept(ind10)
        self.assertEqual(
            [str(obs) for obs in N.all_individuals],
            [
                "Individual 1",
                "Individual 2",
                "Individual 3",
                "Individual 4",
                "Individual 5",
                "Individual 6",
                "Individual 7",
                "Individual 8",
                "Individual 9",
                "Individual 10",
            ],
        )
        self.assertEqual(round(ind10.arrival_date, 5), 0.1)
        self.assertEqual(ind10.service_start_date, False)
        self.assertEqual(ind10.service_time, False)

    def test_begin_service_if_possible_accept_method(self):
        ciw.seed(50)
        Q = ciw.Simulation(N_deadlock, deadlock_detector=ciw.deadlock.StateDigraph())
        ind = ciw.Individual(1)
        self.assertEqual(
            set(Q.deadlock_detector.statedigraph.nodes()),
            set(
                [
                    "Server 5 at Node 2",
                    "Server 5 at Node 1",
                    "Server 3 at Node 2",
                    "Server 1 at Node 2",
                    "Server 1 at Node 1",
                    "Server 2 at Node 1",
                    "Server 2 at Node 2",
                    "Server 3 at Node 1",
                    "Server 4 at Node 1",
                    "Server 4 at Node 2",
                ]
            ),
        )
        self.assertEqual(ind.arrival_date, False)
        self.assertEqual(ind.service_time, False)
        self.assertEqual(ind.service_start_date, False)
        self.assertEqual(ind.service_end_date, False)
        Q.current_time = 300
        Q.transitive_nodes[0].individuals[0].append(ind)
        Q.transitive_nodes[0].begin_service_if_possible_accept(ind)
        self.assertEqual(ind.arrival_date, 300)
        self.assertEqual(round(ind.service_time, 5), 0.03382)
        self.assertEqual(ind.service_start_date, 300)
        self.assertEqual(round(ind.service_end_date, 5), 300.03382)

    def test_update_next_event_date_method(self):
        Net = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(10.0)],
            service_distributions=[ciw.dists.Sequential([0.5, 0.2])],
            number_of_servers=[5],
        )
        Q = ciw.Simulation(Net)
        N = Q.transitive_nodes[0]
        self.assertEqual(N.next_event_date, float("inf"))
        self.assertEqual(N.all_individuals, [])
        Q.current_time = 0.0
        N.update_next_event_date()
        self.assertEqual(N.next_event_date, float("inf"))

        ind1 = ciw.Individual(1)
        ind1.arrival_date = 0.3
        N.next_event_date = 0.3
        Q.current_time = 0.3
        N.accept(ind1)
        N.update_next_event_date()
        self.assertEqual(N.next_event_date, 0.8)

        ind2 = ciw.Individual(2)
        ind2.arrival_date = 0.4
        Q.current_time = 0.4
        N.accept(ind2)
        Q.current_time = N.next_event_date + 0.000001
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 4), 0.6)

        N.finish_service()
        N.update_next_event_date()
        self.assertEqual(N.next_event_date, 0.8)

        N.finish_service()
        N.update_next_event_date()
        self.assertEqual(N.next_event_date, float("inf"))

    def test_next_node_method(self):
        ciw.seed(6)
        Q = ciw.Simulation(N_params)
        node = Q.transitive_nodes[0]
        ind = ciw.Individual(22, 'Class 0')
        self.assertEqual(str(node.next_node(ind)), "Node 4")
        self.assertEqual(str(node.next_node(ind)), "Node 4")
        self.assertEqual(str(node.next_node(ind)), "Node 4")
        self.assertEqual(str(node.next_node(ind)), "Node 4")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 4")
        self.assertEqual(str(node.next_node(ind)), "Exit Node")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Exit Node")
        self.assertEqual(str(node.next_node(ind)), "Node 4")

        ciw.seed(54)
        Q = ciw.Simulation(N_params)
        node = Q.transitive_nodes[2]
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 4")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 4")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 4")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 3")
        self.assertEqual(str(node.next_node(ind)), "Node 2")
        self.assertEqual(str(node.next_node(ind)), "Node 2")

    def test_write_individual_record_method(self):
        ciw.seed(7)
        Q = ciw.Simulation(N_params)
        N = Q.transitive_nodes[0]
        ind = ciw.Individual(6, 'Class 0')
        Q.current_time = 3
        N.accept(ind)
        ind.service_start_date = 3.5
        ind.service_end_date = 5.5
        ind.exit_date = 9
        N.write_individual_record(ind)
        self.assertEqual(ind.data_records[0].arrival_date, 3)
        self.assertEqual(ind.data_records[0].waiting_time, 0.5)
        self.assertEqual(ind.data_records[0].service_start_date, 3.5)
        self.assertEqual(ind.data_records[0].service_time, 2)
        self.assertEqual(ind.data_records[0].service_end_date, 5.5)
        self.assertEqual(ind.data_records[0].time_blocked, 3.5)
        self.assertEqual(ind.data_records[0].exit_date, 9)
        self.assertEqual(ind.data_records[0].customer_class, 'Class 0')

    def test_reset_individual_attributes(self):
        ciw.seed(7)
        Q = ciw.Simulation(N_params)
        N = Q.transitive_nodes[0]
        ind = ciw.Individual(6, 'Class 0')
        Q.current_time = 3
        N.accept(ind)
        ind.service_start_date = 3.5
        ind.service_end_date = 5.5
        ind.exit_date = 9
        N.write_individual_record(ind)
        self.assertEqual(ind.arrival_date, 3)
        self.assertEqual(ind.service_start_date, 3.5)
        self.assertEqual(ind.service_end_date, 5.5)
        self.assertEqual(ind.exit_date, 9)
        self.assertEqual(ind.customer_class, 'Class 0')

        N.reset_individual_attributes(ind)
        self.assertFalse(ind.arrival_date)
        self.assertFalse(ind.service_start_date)
        self.assertFalse(ind.service_end_date)
        self.assertFalse(ind.exit_date)

    def test_date_from_schedule_generator(self):
        sg = ciw.Schedule(numbers_of_servers=[1, 0, 2, 3], shift_end_dates=[30, 60, 90, 100])
        sg.initialise()
        sg.get_next_shift()
        self.assertEqual(sg.c, 1)
        self.assertEqual(sg.next_c, 0)
        self.assertEqual(sg.next_shift_change_date, 30)
        self.assertEqual(next(sg.schedule_generator), (60, 2))
        self.assertEqual(next(sg.schedule_generator), (90, 3))
        self.assertEqual(next(sg.schedule_generator), (100, 1))
        self.assertEqual(next(sg.schedule_generator), (130, 0))
        self.assertEqual(next(sg.schedule_generator), (160, 2))

        sg.initialise()
        sg.get_next_shift()
        self.assertEqual(sg.c, 1)
        self.assertEqual(sg.next_c, 0)
        self.assertEqual(sg.next_shift_change_date, 30)
        self.assertEqual(next(sg.schedule_generator), (60, 2))
        self.assertEqual(next(sg.schedule_generator), (90, 3))
        self.assertEqual(next(sg.schedule_generator), (100, 1))
        self.assertEqual(next(sg.schedule_generator), (130, 0))
        self.assertEqual(next(sg.schedule_generator), (160, 2))

    def test_all_individuals_property(self):
        Q = ciw.Simulation(N_priorities)
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.individuals, [[], []])
        self.assertEqual(N1.all_individuals, [])

        N1.individuals = [[3, 6, 1], [1, 9]]
        self.assertEqual(N1.all_individuals, [3, 6, 1, 1, 9])

        N1.individuals = [[3, "help", 1], [], [1, 9]]
        self.assertEqual(N1.all_individuals, [3, "help", 1, 1, 9])

    def test_if_putting_individuals_in_correct_priority_queue(self):
        Q = ciw.Simulation(N_priorities)
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]

        self.assertEqual([[str(obs) for obs in lst] for lst in N1.individuals], [[], []])
        self.assertEqual([str(obs) for obs in N1.all_individuals], [])
        self.assertEqual([[str(obs) for obs in lst] for lst in N2.individuals], [[], []])
        self.assertEqual([str(obs) for obs in N2.all_individuals], [])

        Q.nodes[0].next_node = 1
        Q.nodes[0].next_class = 'Class 0'
        Q.nodes[0].have_event()

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals],
            [["Individual 1"], []],
        )
        self.assertEqual([str(obs) for obs in N1.all_individuals], ["Individual 1"])
        self.assertEqual([[str(obs) for obs in lst] for lst in N2.individuals], [[], []])
        self.assertEqual([str(obs) for obs in N2.all_individuals], [])

        Q.nodes[0].next_node = 1
        Q.nodes[0].next_class = 'Class 1'
        Q.nodes[0].have_event()

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals],
            [["Individual 1"], ["Individual 2"]],
        )
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals], ["Individual 1", "Individual 2"]
        )
        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N2.individuals], [[], []]
        )
        self.assertEqual([str(obs) for obs in N2.all_individuals], [])

        Q.nodes[0].next_node = 2
        Q.nodes[0].next_class = 'Class 0'
        Q.nodes[0].have_event()

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals],
            [["Individual 1"], ["Individual 2"]],
        )
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals], ["Individual 1", "Individual 2"]
        )
        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N2.individuals],
            [["Individual 3"], []],
        )
        self.assertEqual([str(obs) for obs in N2.all_individuals], ["Individual 3"])

        Q.nodes[0].next_node = 2
        Q.nodes[0].next_class = 'Class 1'
        Q.nodes[0].have_event()

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals],
            [["Individual 1"], ["Individual 2"]],
        )
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals], ["Individual 1", "Individual 2"]
        )
        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N2.individuals],
            [["Individual 3"], ["Individual 4"]],
        )
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals], ["Individual 3", "Individual 4"]
        )

    def test_server_utilisation(self):
        # Single server
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 3.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([1.0, 6.0, 100.0])],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(14.0)
        self.assertEqual(Q.transitive_nodes[0].server_utilisation, 0.5)

        # Multi server
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 3.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([10.0, 6.0, 100.0])],
            number_of_servers=[3],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20.0)
        self.assertEqual(Q.transitive_nodes[0].server_utilisation, 4.0 / 15.0)

    def test_server_utilisation_with_schedules(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 4.0, 4.0, 0.0, 7.0, 1000.0])],
            service_distributions=[ciw.dists.Sequential([4.0, 2.0, 6.0, 6.0, 3.0])],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 2], shift_end_dates=[9, 23])],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(23)
        recs = Q.get_all_records()
        self.assertEqual(Q.transitive_nodes[0].server_utilisation, 21.0 / 37.0)

    def test_server_utilisation_with_wrapup(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(7.14)],
            service_distributions=[ciw.dists.Exponential(0.04)],
            number_of_servers=[70],
        )
        ciw.seed(1)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(168)
        for srvr in Q.transitive_nodes[0].servers:
            self.assertGreaterEqual(srvr.total_time, srvr.busy_time)

    @given(
        lmbda=floats(min_value=0.01, max_value=5),
        mu=floats(min_value=0.01, max_value=5),
        c=integers(min_value=1, max_value=10),
        rm=random_module(),
    )
    @settings(deadline=None)
    def test_utilisation_always_1_or_less(self, lmbda, mu, c, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(lmbda)],
            service_distributions=[ciw.dists.Exponential(mu)],
            number_of_servers=[c],
        )
        ciw.seed(1)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(200)
        for srvr in Q.transitive_nodes[0].servers:
            self.assertGreaterEqual(srvr.total_time, srvr.busy_time)
        self.assertLessEqual(Q.transitive_nodes[0].server_utilisation, 1.0)
        self.assertGreaterEqual(Q.transitive_nodes[0].server_utilisation, 0.0)

    def test_num_inds_equal_len_all_inds(self):
        # Create a Simulation class that inherits from ciw.Simulation so that
        # an assertion than number_of_individuals == len(all_individuals)
        # every time self.event_and_return_nextnode is called.
        class AssertSim(ciw.Simulation):
            def event_and_return_nextnode(simself, next_active_node):
                """
                Carries out the event of current next_active_node, and return the next
                next_active_node
                """
                next_active_node.have_event()
                for node in simself.transitive_nodes:
                    node.update_next_event_date()
                    self.assertEqual(
                        node.number_of_individuals, len(node.all_individuals)
                    )
                return simself.find_next_active_node()

        # Now carry out the tests by running a simulation with this new
        # inherited Node class.
        N = N_params
        Q = AssertSim(N)
        Q.simulate_until_max_time(100)

    def test_server_priority_function_allocate_to_less_busy(self):
        """
        Test the server priority function when we prioritise the server that was
        less busy throughout the simulation.
        """

        def get_server_busy_time(server, ind):
            return server.busy_time

        ciw.seed(0)
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1)],
            service_distributions=[ciw.dists.Exponential(2)],
            number_of_servers=[2],
            server_priority_functions=[get_server_busy_time],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(1000)

        expected_times = [245.07547532640024, 244.68396417751663]
        for i, srv in enumerate(Q.nodes[1].servers):
            self.assertEqual(srv.busy_time, expected_times[i])

    def test_server_priority_function_allocate_to_last_server_first(self):
        """
        Test the server priority function when we prioritise the server with the
        highest id number.
        """

        def get_server_busy_time(server, ind):
            return -server.id_number

        ciw.seed(0)
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1)],
            service_distributions=[ciw.dists.Exponential(2)],
            number_of_servers=[2],
            server_priority_functions=[get_server_busy_time],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(1000)

        expected_times = [158.68745586286119, 331.0719836410557]
        for i, srv in enumerate(Q.nodes[1].servers):
            self.assertEqual(srv.busy_time, expected_times[i])

    def test_server_priority_function_two_nodes(self):
        """
        Test the server priority function with two nodes that each has a
        different priority rule.
        """

        def prioritise_less_busy(srv, ind):
            return srv.busy_time

        def prioritise_highest_id(srv, ind):
            return -srv.id_number

        ciw.seed(0)
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1), ciw.dists.Exponential(1)],
            service_distributions=[ciw.dists.Exponential(2), ciw.dists.Exponential(2)],
            number_of_servers=[2, 2],
            routing=[[0.0, 0.0], [0.0, 0.0]],
            server_priority_functions=[prioritise_less_busy, prioritise_highest_id],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(1000)
        expected_times_node_1 = [256.2457715650031, 257.59339967047254]
        expected_times_node_2 = [157.35577182806387, 356.41473247082365]

        for i, (srv_1, srv_2) in enumerate(zip(Q.nodes[1].servers, Q.nodes[2].servers)):
            self.assertEqual(srv_1.busy_time, expected_times_node_1[i])
            self.assertEqual(srv_2.busy_time, expected_times_node_2[i])

    def test_records_correct_server_id(self):
        """
        Test that the server id is recorded correctly.
        """

        def custom_server_priority(srv, ind):
            """
            A custom server priority function that priortises server 1 for
            customer class 0 and server 2 for customer class 1.
            """
            if ind.customer_class == 'Class 0':
                priorities = {1: 0, 2: 1}
                return priorities[srv.id_number]
            if ind.customer_class == 'Class 1':
                priorities = {1: 1, 2: 0}
                return priorities[srv.id_number]

        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(rate=1.0)],
                "Class 1": [ciw.dists.Exponential(rate=1.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(rate=200.0)],
                "Class 1": [ciw.dists.Exponential(rate=200.0)],
            },
            number_of_servers=[2],
            server_priority_functions=[custom_server_priority],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(50)

        all_class_0_correct = all(
            [
                rec.server_id == 1
                for rec in Q.get_all_records()
                if rec.customer_class == 'Class 0'
            ]
        )
        all_class_1_correct = all(
            [
                rec.server_id == 1
                for rec in Q.get_all_records()
                if rec.customer_class == 'Class 0'
            ]
        )

        self.assertTrue(all_class_0_correct)
        self.assertTrue(all_class_1_correct)

    def test_reneging_next_event(self):
        """
        Tests that when reneging the correct next event time is detected.
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(7)],
            service_distributions=[ciw.dists.Deterministic(11)],
            number_of_servers=[1],
            reneging_time_distributions=[ciw.dists.Deterministic(3)],
        )
        Q = ciw.Simulation(N)
        self.assertTrue(Q.nodes[1].reneging)
        #### We would expect:
        # t=7  arrival cust 1
        # t=14 arrival cust 2
        # t=17 renege  cust 2
        # t=18 leave   cust 1
        # t=21 arrival cust 3
        # t=28 arrival cust 4
        # t=31 renege  cust 4
        # t=32 leave   cust 3
        Q.simulate_until_max_time(6)
        self.assertEqual(Q.nodes[0].next_event_date, 7)
        self.assertEqual(Q.nodes[1].next_event_date, float("inf"))
        self.assertEqual(Q.nodes[1].next_event_type, None)
        Q.simulate_until_max_time(13)
        self.assertEqual(Q.nodes[0].next_event_date, 14)
        self.assertEqual(Q.nodes[1].next_event_date, 18)
        self.assertEqual(Q.nodes[1].next_event_type, 'end_service')
        Q.simulate_until_max_time(16)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, 17)
        self.assertEqual(Q.nodes[1].next_event_type, 'renege')
        Q.simulate_until_max_time(17.5)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, 18)
        self.assertEqual(Q.nodes[1].next_event_type, 'end_service')
        Q.simulate_until_max_time(20)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, float("inf"))
        self.assertEqual(Q.nodes[1].next_event_type, None)
        Q.simulate_until_max_time(27)
        self.assertEqual(Q.nodes[0].next_event_date, 28)
        self.assertEqual(Q.nodes[1].next_event_date, 32)
        self.assertEqual(Q.nodes[1].next_event_type, 'end_service')
        Q.simulate_until_max_time(30)
        self.assertEqual(Q.nodes[0].next_event_date, 35)
        self.assertEqual(Q.nodes[1].next_event_date, 31)
        self.assertEqual(Q.nodes[1].next_event_type, 'renege')
        Q.simulate_until_max_time(31.5)
        self.assertEqual(Q.nodes[0].next_event_date, 35)
        self.assertEqual(Q.nodes[1].next_event_date, 32)
        self.assertEqual(Q.nodes[1].next_event_type, 'end_service')

    def test_reneging_records(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(7)],
            service_distributions=[ciw.dists.Deterministic(11)],
            number_of_servers=[1],
            reneging_time_distributions=[ciw.dists.Deterministic(3)],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(31.5)
        reneging_recs = Q.get_all_records(only=["renege"])
        self.assertEqual([r.id_number for r in reneging_recs], [2, 4])
        self.assertEqual([r.arrival_date for r in reneging_recs], [14, 28])
        self.assertEqual([r.exit_date for r in reneging_recs], [17, 31])
        self.assertEqual([r.waiting_time for r in reneging_recs], [3, 3])
        self.assertEqual([r.node for r in reneging_recs], [1, 1])
        self.assertEqual([r.service_time for r in reneging_recs], [nan, nan])
        self.assertEqual([r.service_start_date for r in reneging_recs], [nan, nan])
        self.assertEqual([r.service_end_date for r in reneging_recs], [nan, nan])
        self.assertEqual([r.server_id for r in reneging_recs], [nan, nan])
        self.assertEqual([r.customer_class for r in reneging_recs], ['Customer', 'Customer'])
        self.assertEqual([r.queue_size_at_arrival for r in reneging_recs], [1, 1])
        self.assertEqual([r.queue_size_at_departure for r in reneging_recs], [1, 1])

    def test_reneging_sends_to_destination(self):
        class Jockey(ciw.routing.NodeRouting):
            def next_node(self, ind):
                """
                Chooses the exit node with probability 1.
                """
                return self.simulation.nodes[-1]

            def next_node_for_jockeying(self, ind):
                """
                Chooses Node 2
                """
                return self.simulation.nodes[2]

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(7), None],
            service_distributions=[ciw.dists.Deterministic(11), ciw.dists.Deterministic(2)],
            routing=ciw.routing.NetworkRouting(routers=[Jockey(), ciw.routing.Leave()]),
            number_of_servers=[1, 1],
            reneging_time_distributions=[ciw.dists.Deterministic(3), None],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records()
        recs_ind2 = [r for r in recs if r.id_number == 2]

        self.assertEqual([r.arrival_date for r in recs_ind2], [14, 17])
        self.assertEqual([r.exit_date for r in recs_ind2], [17, 19])
        self.assertEqual([r.waiting_time for r in recs_ind2], [3, 0])
        self.assertEqual([r.node for r in recs_ind2], [1, 2])
        self.assertEqual([r.service_time for r in recs_ind2], [nan, 2])
        self.assertEqual([r.service_start_date for r in recs_ind2], [nan, 17])
        self.assertEqual([r.service_end_date for r in recs_ind2], [nan, 19])
        self.assertEqual([r.server_id for r in recs_ind2], [nan, 1])
        self.assertEqual([r.customer_class for r in recs_ind2], ['Customer', 'Customer'])
        self.assertEqual([r.queue_size_at_arrival for r in recs_ind2], [1, 0])
        self.assertEqual([r.queue_size_at_departure for r in recs_ind2], [1, 0])

    def test_process_based_defaults_jockeyers_to_exit(self):
        def route(self, ind):
            """
            1-2
            """
            return [1]

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(7), None],
            service_distributions=[ciw.dists.Deterministic(11), ciw.dists.Deterministic(2)],
            routing=ciw.routing.ProcessBased(route_function=route),
            number_of_servers=[1, 1],
            reneging_time_distributions=[ciw.dists.Deterministic(3), None],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records()
        self.assertEqual([r.id_number for r in recs], [1, 2])
        self.assertEqual([r.record_type for r in recs], ['service', 'renege'])
        self.assertEqual([r.arrival_date for r in recs], [7, 14])
        self.assertEqual([r.exit_date for r in recs], [18, 17])
        self.assertEqual([r.waiting_time for r in recs], [0, 3])
        self.assertEqual([r.node for r in recs], [1, 1])
        self.assertEqual([r.service_time for r in recs], [11, nan])
        self.assertEqual([r.service_start_date for r in recs], [7, nan])
        self.assertEqual([r.service_end_date for r in recs], [18, nan])
        self.assertEqual([r.server_id for r in recs], [1, nan])
        self.assertEqual([r.customer_class for r in recs], ['Customer', 'Customer'])
        self.assertEqual([r.queue_size_at_arrival for r in recs], [0, 1])
        self.assertEqual([r.queue_size_at_departure for r in recs], [0, 1])

    def test_reneging_none_dist(self):
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [None],
                "Class 1": [ciw.dists.Deterministic(7)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(11)],
                "Class 1": [ciw.dists.Deterministic(11)],
            },
            number_of_servers=[1],
            reneging_time_distributions={
                "Class 0": [ciw.dists.Deterministic(3)],
                "Class 1": [None],
            },
        )
        Q = ciw.Simulation(N)
        self.assertTrue(Q.nodes[1].reneging)
        #### We would expect:
        # t=7  arrival cust 1
        # t=14 arrival cust 2
        # t=18 leave   cust 1
        Q.simulate_until_max_time(6)
        self.assertEqual(Q.nodes[0].next_event_date, 7)
        self.assertEqual(Q.nodes[1].next_event_date, float("inf"))
        self.assertEqual(Q.nodes[1].next_event_type, None)
        Q.simulate_until_max_time(13)
        self.assertEqual(Q.nodes[0].next_event_date, 14)
        self.assertEqual(Q.nodes[1].next_event_date, 18)
        self.assertEqual(Q.nodes[1].next_event_type, 'end_service')
        Q.simulate_until_max_time(17.5)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, 18)
        self.assertEqual(Q.nodes[1].next_event_type, 'end_service')
        Q.simulate_until_max_time(20)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, 29)
        self.assertEqual(Q.nodes[1].next_event_type, 'end_service')

    def test_reneging_with_schedules(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(7)],
            service_distributions=[ciw.dists.Deterministic(11)],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0], shift_end_dates=[16, 10000])],
            reneging_time_distributions=[ciw.dists.Deterministic(3)],
        )
        Q = ciw.Simulation(N)
        self.assertTrue(Q.nodes[1].reneging)
        #### We would expect:
        # t=7  arrival cust 1
        # t=14 arrival cust 2
        # t=16 server meant to go off duty but doesn't
        # t=17 renege  cust 2
        # t=18 leave   cust 1, server goes off duty
        # t=21 arrival cust 3
        # t=24 renege  cust 3
        # t=28 arrival cust 4
        Q.simulate_until_max_time(6)
        self.assertEqual(Q.nodes[0].next_event_date, 7)
        self.assertEqual(Q.nodes[1].next_event_date, 16)
        self.assertEqual(Q.nodes[1].next_event_type, 'shift_change')
        Q.simulate_until_max_time(13)
        self.assertEqual(Q.nodes[0].next_event_date, 14)
        self.assertEqual(Q.nodes[1].next_event_date, 16)
        self.assertEqual(Q.nodes[1].next_event_type, 'shift_change')
        Q.simulate_until_max_time(15.5)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, 16)
        self.assertEqual(Q.nodes[1].next_event_type, 'shift_change')
        Q.simulate_until_max_time(16.5)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, 17)
        self.assertEqual(Q.nodes[1].next_event_type, 'renege')
        Q.simulate_until_max_time(17.5)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, 18)
        self.assertEqual(Q.nodes[1].next_event_type, 'end_service')
        Q.simulate_until_max_time(20)
        self.assertEqual(Q.nodes[0].next_event_date, 21)
        self.assertEqual(Q.nodes[1].next_event_date, 10000)
        self.assertEqual(Q.nodes[1].next_event_type, 'shift_change')
        Q.simulate_until_max_time(23)
        self.assertEqual(Q.nodes[0].next_event_date, 28)
        self.assertEqual(Q.nodes[1].next_event_date, 24)
        self.assertEqual(Q.nodes[1].next_event_type, 'renege')
        Q.simulate_until_max_time(27)
        self.assertEqual(Q.nodes[0].next_event_date, 28)
        self.assertEqual(Q.nodes[1].next_event_date, 10000)
        self.assertEqual(Q.nodes[1].next_event_type, 'shift_change')

    def test_simultaneous_reneging(self):
        """
        Tests that both customers renege when they should renege simultaneously.
        Arrivals at [3, 4, 5, 20]
          t=3 Cust 1 arrives, enters service
          t=4 Cust 2 arrives
          t=5 Cust 3 arrives
          t=11 Custs 2 & 3 renege
          t=20 Cust 4 arrives
          t=23 Cust 1 leaves, Cust 4 enters service
          t=43 Cust 4 leaves
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([3, 1, 1, 15, float('inf')])],
            service_distributions=[ciw.dists.Deterministic(20)],
            number_of_servers=[1],
            reneging_time_distributions=[ciw.dists.Sequential([100, 7, 6, 100])],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(50)
        recs_services = sorted(Q.get_all_records(only=['service']), key=lambda x: x.id_number)
        recs_reneges = sorted(Q.get_all_records(only=['renege']), key=lambda x: x.id_number)
        self.assertEqual(len(recs_services), 2)
        self.assertEqual([r.id_number for r in recs_services], [1, 4])
        self.assertEqual([r.service_start_date for r in recs_services], [3, 23])
        self.assertEqual([r.service_end_date for r in recs_services], [23, 43])
        self.assertEqual(len(recs_reneges), 2)
        self.assertEqual([r.id_number for r in recs_reneges], [2, 3])
        self.assertEqual([r.arrival_date for r in recs_reneges], [4, 5])
        self.assertEqual([r.exit_date for r in recs_reneges], [11, 11])

    def test_class_change_while_waiting(self):
        """
        Only one type of customer arrive (Class 0),
        but if they wait more than 4 time units they change to Class 1.
        Services last exactly 4.5 time units.
        Simulate until 26 time units.

        We would expect:
        - first three customers to wait 0, 1.5, and 3 respectively. (Remain Class 0)
        - next two customer wait 4.5 and 6 respectively. (Change to Class 1)
        """
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Deterministic(3)],
                "Class 1": [None],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(4.5)],
                "Class 1": [ciw.dists.Deterministic(4.5)],
            },
            number_of_servers=[1],
            class_change_time_distributions={
                'Class 0': {'Class 0': None, 'Class 1': ciw.dists.Deterministic(4)},
                'Class 1': {'Class 0': None, 'Class 1': None},
            },
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(26)
        recs = Q.get_all_records()
        self.assertEqual(len(recs), 5)
        # Customer 1
        self.assertEqual(recs[0].arrival_date, 3)
        self.assertEqual(recs[0].waiting_time, 0)
        self.assertEqual(recs[0].service_start_date, 3)
        self.assertEqual(recs[0].service_end_date, 7.5)
        self.assertEqual(recs[0].customer_class, 'Class 0')
        self.assertEqual(recs[0].original_customer_class, 'Class 0')
        # Customer 2
        self.assertEqual(recs[1].arrival_date, 6)
        self.assertEqual(recs[1].waiting_time, 1.5)
        self.assertEqual(recs[1].service_start_date, 7.5)
        self.assertEqual(recs[1].service_end_date, 12)
        self.assertEqual(recs[1].customer_class, 'Class 0')
        self.assertEqual(recs[1].original_customer_class, 'Class 0')
        # Customer 3
        self.assertEqual(recs[2].arrival_date, 9)
        self.assertEqual(recs[2].waiting_time, 3)
        self.assertEqual(recs[2].service_start_date, 12)
        self.assertEqual(recs[2].service_end_date, 16.5)
        self.assertEqual(recs[2].customer_class, 'Class 0')
        self.assertEqual(recs[2].original_customer_class, 'Class 0')
        # Customer 4
        self.assertEqual(recs[3].arrival_date, 12)
        self.assertEqual(recs[3].waiting_time, 4.5)
        self.assertEqual(recs[3].service_start_date, 16.5)
        self.assertEqual(recs[3].service_end_date, 21)
        self.assertEqual(recs[3].customer_class, 'Class 1')
        self.assertEqual(recs[3].original_customer_class, 'Class 0')
        # Customer 5
        self.assertEqual(recs[4].arrival_date, 15)
        self.assertEqual(recs[4].waiting_time, 6)
        self.assertEqual(recs[4].service_start_date, 21)
        self.assertEqual(recs[4].service_end_date, 25.5)
        self.assertEqual(recs[4].customer_class, 'Class 1')
        self.assertEqual(recs[4].original_customer_class, 'Class 0')

    def test_class_change_while_waiting_default_nones(self):
        """
        Only one type of customer arrive (Class 0),
        but if they wait more than 4 time units they change to Class 1.
        Services last exactly 4.5 time units.
        Simulate until 26 time units.

        We would expect:
        - first three customers to wait 0, 1.5, and 3 respectively. (Remain Class 0)
        - next two customer wait 4.5 and 6 respectively. (Change to Class 1)
        """
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Deterministic(3)],
                "Class 1": [None],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(4.5)],
                "Class 1": [ciw.dists.Deterministic(4.5)],
            },
            number_of_servers=[1],
            class_change_time_distributions={
                'Class 0': {'Class 1': ciw.dists.Deterministic(4)},
            },
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(26)
        recs = Q.get_all_records()
        self.assertEqual(len(recs), 5)
        # Customer 1
        self.assertEqual(recs[0].arrival_date, 3)
        self.assertEqual(recs[0].waiting_time, 0)
        self.assertEqual(recs[0].service_start_date, 3)
        self.assertEqual(recs[0].service_end_date, 7.5)
        self.assertEqual(recs[0].customer_class, 'Class 0')
        self.assertEqual(recs[0].original_customer_class, 'Class 0')
        # Customer 2
        self.assertEqual(recs[1].arrival_date, 6)
        self.assertEqual(recs[1].waiting_time, 1.5)
        self.assertEqual(recs[1].service_start_date, 7.5)
        self.assertEqual(recs[1].service_end_date, 12)
        self.assertEqual(recs[1].customer_class, 'Class 0')
        self.assertEqual(recs[1].original_customer_class, 'Class 0')
        # Customer 3
        self.assertEqual(recs[2].arrival_date, 9)
        self.assertEqual(recs[2].waiting_time, 3)
        self.assertEqual(recs[2].service_start_date, 12)
        self.assertEqual(recs[2].service_end_date, 16.5)
        self.assertEqual(recs[2].customer_class, 'Class 0')
        self.assertEqual(recs[2].original_customer_class, 'Class 0')
        # Customer 4
        self.assertEqual(recs[3].arrival_date, 12)
        self.assertEqual(recs[3].waiting_time, 4.5)
        self.assertEqual(recs[3].service_start_date, 16.5)
        self.assertEqual(recs[3].service_end_date, 21)
        self.assertEqual(recs[3].customer_class, 'Class 1')
        self.assertEqual(recs[3].original_customer_class, 'Class 0')
        # Customer 5
        self.assertEqual(recs[4].arrival_date, 15)
        self.assertEqual(recs[4].waiting_time, 6)
        self.assertEqual(recs[4].service_start_date, 21)
        self.assertEqual(recs[4].service_end_date, 25.5)
        self.assertEqual(recs[4].customer_class, 'Class 1')
        self.assertEqual(recs[4].original_customer_class, 'Class 0')


    def test_priority_change_while_waiting(self):
        """
        Customers of class 0 have priority over class 1.
        Class 0 arrive every 4, class 1 arrive every 3.
        Class 1 turn to class 0 if they have waited longer than 7.
        Services last exactly 4.5 time units.
        Simulate until 26 time units.

        We would expect:
        - First served customer to be class 1, all other customers to be class 0
        - Arrivals at 3, 4, 8, 12, and 6 respectively
        - Service starts at 3, 7.5, 12, 16.5, and 21 respectively
        - (the customer who arrives at 6 was class 1, but changed to class 0 at time 13)
        """
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Deterministic(4)],
                "Class 1": [ciw.dists.Deterministic(3)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(4.5)],
                "Class 1": [ciw.dists.Deterministic(4.5)],
            },
            number_of_servers=[1],
            class_change_time_distributions={
                'Class 0': {'Class 0': None, 'Class 1': None},
                'Class 1': {'Class 0': ciw.dists.Deterministic(7), 'Class 1': None},
            },
            priority_classes={"Class 0": 0, "Class 1": 1},
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(26)
        recs = Q.get_all_records()
        self.assertEqual(len(recs), 5)
        # Customer 1
        self.assertEqual(recs[0].arrival_date, 3)
        self.assertEqual(recs[0].waiting_time, 0)
        self.assertEqual(recs[0].service_start_date, 3)
        self.assertEqual(recs[0].service_end_date, 7.5)
        self.assertEqual(recs[0].customer_class, 'Class 1')
        self.assertEqual(recs[0].original_customer_class, 'Class 1')
        # Customer 2
        self.assertEqual(recs[1].arrival_date, 4)
        self.assertEqual(recs[1].waiting_time, 3.5)
        self.assertEqual(recs[1].service_start_date, 7.5)
        self.assertEqual(recs[1].service_end_date, 12)
        self.assertEqual(recs[1].customer_class, 'Class 0')
        self.assertEqual(recs[1].original_customer_class, 'Class 0')
        # Customer 3
        self.assertEqual(recs[2].arrival_date, 8)
        self.assertEqual(recs[2].waiting_time, 4)
        self.assertEqual(recs[2].service_start_date, 12)
        self.assertEqual(recs[2].service_end_date, 16.5)
        self.assertEqual(recs[2].customer_class, 'Class 0')
        self.assertEqual(recs[2].original_customer_class, 'Class 0')
        # Customer 4
        self.assertEqual(recs[3].arrival_date, 12)
        self.assertEqual(recs[3].waiting_time, 4.5)
        self.assertEqual(recs[3].service_start_date, 16.5)
        self.assertEqual(recs[3].service_end_date, 21)
        self.assertEqual(recs[3].customer_class, 'Class 0')
        self.assertEqual(recs[3].original_customer_class, 'Class 0')
        # Customer 5
        self.assertEqual(recs[4].arrival_date, 6)
        self.assertEqual(recs[4].waiting_time, 15)
        self.assertEqual(recs[4].service_start_date, 21)
        self.assertEqual(recs[4].service_end_date, 25.5)
        self.assertEqual(recs[4].customer_class, 'Class 0')
        self.assertEqual(recs[4].original_customer_class, 'Class 1')

    def test_preemptive_priorities(self):
        """
        One server.
        Two classes of customer, 0 and 1, 0 higher priority than 1.
        Class 0 have service distribution Deterministic 4.
        Class 1 have service distribution Deterministic 5.

        Class 0 arrive at times [1.5, 5]
        Class 1 arrive at times [7.5]

        Without preemption we would expect:
        Class & Arrival & Wait & Service start & Service end
        1     & 1.5     & 0    & 1.5           & 6.5
        1     & 5       & 1.5  & 6.5           & 11.5
        0     & 7.5     & 4    & 11.5          & 15.5

        With preemption we would expect:
        Class & Arrival & Wait & Service start & Service end
        1     & 1.5     & 0    & 1.5           & 6.5
        1     & 5       & 6.5  & 11.5          & 11.5
        0     & 7.5     & 0    & 7.5           & 11.5
        """

        # First without preemption:
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Sequential([7.5, float("inf")])],
                "Class 1": [ciw.dists.Sequential([1.5, 3.5, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(4)],
                "Class 1": [ciw.dists.Deterministic(5)],
            },
            number_of_servers=[1],
            priority_classes=({"Class 0": 0, "Class 1": 1}, [False]),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records()
        recs.sort(key=lambda r: r.arrival_date)
        self.assertEqual(recs[0].arrival_date, 1.5)
        self.assertEqual(recs[1].arrival_date, 5)
        self.assertEqual(recs[2].arrival_date, 7.5)
        self.assertEqual(recs[0].waiting_time, 0)
        self.assertEqual(recs[1].waiting_time, 1.5)
        self.assertEqual(recs[2].waiting_time, 4)
        self.assertEqual(recs[0].service_start_date, 1.5)
        self.assertEqual(recs[1].service_start_date, 6.5)
        self.assertEqual(recs[2].service_start_date, 11.5)
        self.assertEqual(recs[0].service_end_date, 6.5)
        self.assertEqual(recs[1].service_end_date, 11.5)
        self.assertEqual(recs[2].service_end_date, 15.5)

        # Now with preemption:
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Sequential([7.5, float("inf")])],
                "Class 1": [ciw.dists.Sequential([1.5, 3.5, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(4)],
                "Class 1": [ciw.dists.Deterministic(5)],
            },
            number_of_servers=[1],
            priority_classes=({"Class 0": 0, "Class 1": 1}, ["resample"]),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        all_recs = Q.get_all_records()
        recs = [r for r in all_recs if r.record_type == "service"]
        recs.sort(key=lambda r: r.arrival_date)
        self.assertEqual(recs[0].arrival_date, 1.5)
        self.assertEqual(recs[1].arrival_date, 5)
        self.assertEqual(recs[2].arrival_date, 7.5)
        self.assertEqual(recs[0].waiting_time, 0)
        self.assertEqual(recs[1].waiting_time, 6.5)
        self.assertEqual(recs[2].waiting_time, 0)
        self.assertEqual(recs[0].service_start_date, 1.5)
        self.assertEqual(recs[1].service_start_date, 11.5)
        self.assertEqual(recs[2].service_start_date, 7.5)
        self.assertEqual(recs[0].service_end_date, 6.5)
        self.assertEqual(recs[1].service_end_date, 16.5)
        self.assertEqual(recs[2].service_end_date, 11.5)

        # Test there are interrupted service data records
        interrupted_recs = [r for r in all_recs if r.record_type == "interrupted service"]
        self.assertEqual(len(interrupted_recs), 1)
        self.assertEqual(interrupted_recs[0].arrival_date, 5)
        self.assertEqual(interrupted_recs[0].service_start_date, 6.5)
        self.assertEqual(interrupted_recs[0].waiting_time, 1.5)
        self.assertEqual(interrupted_recs[0].exit_date, 7.5)
        self.assertEqual(interrupted_recs[0].service_time, 5)
        self.assertTrue(isnan(interrupted_recs[0].service_end_date))

    def test_preemptive_priorities_at_class_change(self):
        """
        One server.
        Two classes of customer, 0 and 1, 0 higher priority than 1.
        Only Class 1 arrive, every 2 time units
        All classes have service distribution Deterministic 2.5.

        Class 1 turn into class 0 after waiting 1.2 time units

        Without preemption we would expect:
        Arrival & Wait & Service start & Service end
        2       & 0    & 2             & 4.5
        4       & 0.5  & 4.5           & 7
        6       & 1    & 7             & 9.5
        8       & 1.5  & 9.5           & 12
        10      & 2    & 12            & 14.5

        With preemption we would expect:
        Arrival & Wait & Service start & Service end
        2       & 0    & 2             & 4.5
        4       & 0.5  & 4.5           & 7
        6       & 5.7  & 11.7          & 14.2
        8       & 1.2  & 9.2           & 11.7
        10      & 4.2  & 14.2          & 16.5
        """
        # First without preemption:
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [None],
                "Class 1": [ciw.dists.Sequential([2, 2, 2, 2, 2, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(2.5)],
                "Class 1": [ciw.dists.Deterministic(2.5)],
            },
            number_of_servers=[1],
            priority_classes=({"Class 0": 0, "Class 1": 1}, [False]),
            class_change_time_distributions={
                'Class 0': {'Class 0': None, 'Class 1': None},
                'Class 1': {'Class 0': ciw.dists.Deterministic(1.2), 'Class 1': None}
            },
        )
        Q = ciw.Simulation(N, exact=26)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records()
        recs.sort(key=lambda r: r.arrival_date)
        self.assertEqual(float(recs[0].arrival_date), 2)
        self.assertEqual(float(recs[1].arrival_date), 4)
        self.assertEqual(float(recs[2].arrival_date), 6)
        self.assertEqual(float(recs[3].arrival_date), 8)
        self.assertEqual(float(recs[4].arrival_date), 10)
        self.assertEqual(float(recs[0].waiting_time), 0)
        self.assertEqual(float(recs[1].waiting_time), 0.5)
        self.assertEqual(float(recs[2].waiting_time), 1)
        self.assertEqual(float(recs[3].waiting_time), 1.5)
        self.assertEqual(float(recs[4].waiting_time), 2)
        self.assertEqual(float(recs[0].service_start_date), 2)
        self.assertEqual(float(recs[1].service_start_date), 4.5)
        self.assertEqual(float(recs[2].service_start_date), 7)
        self.assertEqual(float(recs[3].service_start_date), 9.5)
        self.assertEqual(float(recs[4].service_start_date), 12)
        self.assertEqual(float(recs[0].service_end_date), 4.5)
        self.assertEqual(float(recs[1].service_end_date), 7)
        self.assertEqual(float(recs[2].service_end_date), 9.5)
        self.assertEqual(float(recs[3].service_end_date), 12)
        self.assertEqual(float(recs[4].service_end_date), 14.5)

        # Now with preemption:
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [None],
                "Class 1": [ciw.dists.Sequential([2, 2, 2, 2, 2, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(2.5)],
                "Class 1": [ciw.dists.Deterministic(2.5)],
            },
            number_of_servers=[1],
            priority_classes=({"Class 0": 0, "Class 1": 1}, ["resample"]),
            class_change_time_distributions={
                'Class 0': {'Class 0': None, 'Class 1': None},
                'Class 1': {'Class 0': ciw.dists.Deterministic(1.2), 'Class 1': None}
            },
        )
        Q = ciw.Simulation(N, exact=26)
        Q.simulate_until_max_time(20)
        self.assertTrue(Q.nodes[1].dynamic_classes)
        all_recs = Q.get_all_records()
        recs = [r for r in all_recs if r.record_type == "service"]
        recs.sort(key=lambda r: r.arrival_date)
        self.assertEqual(float(recs[0].arrival_date), 2)
        self.assertEqual(float(recs[1].arrival_date), 4)
        self.assertEqual(float(recs[2].arrival_date), 6)
        self.assertEqual(float(recs[3].arrival_date), 8)
        self.assertEqual(float(recs[4].arrival_date), 10)
        self.assertEqual(float(recs[0].waiting_time), 0)
        self.assertEqual(float(recs[1].waiting_time), 0.5)
        self.assertEqual(float(recs[2].waiting_time), 5.7)
        self.assertEqual(float(recs[3].waiting_time), 1.2)
        self.assertEqual(float(recs[4].waiting_time), 4.2)
        self.assertEqual(float(recs[0].service_start_date), 2)
        self.assertEqual(float(recs[1].service_start_date), 4.5)
        self.assertEqual(float(recs[2].service_start_date), 11.7)
        self.assertEqual(float(recs[3].service_start_date), 9.2)
        self.assertEqual(float(recs[4].service_start_date), 14.2)
        self.assertEqual(float(recs[0].service_end_date), 4.5)
        self.assertEqual(float(recs[1].service_end_date), 7)
        self.assertEqual(float(recs[2].service_end_date), 14.2)
        self.assertEqual(float(recs[3].service_end_date), 11.7)
        self.assertEqual(float(recs[4].service_end_date), 16.7)

        # Test interrupted service data records
        interrupted_recs = [r for r in all_recs if r.record_type == "interrupted service"]
        self.assertEqual(len(interrupted_recs), 1)
        self.assertEqual(float(interrupted_recs[0].arrival_date), 6)
        self.assertEqual(float(interrupted_recs[0].service_start_date), 7)
        self.assertEqual(float(interrupted_recs[0].waiting_time), 1)
        self.assertEqual(float(interrupted_recs[0].exit_date), 9.2)
        self.assertEqual(float(interrupted_recs[0].service_time), 2.5)
        self.assertTrue(isnan(interrupted_recs[0].service_end_date))

    def test_preemptive_priorities_reset_class_change(self):
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(1)],
                "Class 1": [ciw.dists.Exponential(1)],
                "Class 2": [ciw.dists.Exponential(1)]
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(7)],
                "Class 1": [ciw.dists.Exponential(6)],
                "Class 2": [ciw.dists.Exponential(2)]
            },
            number_of_servers=[4],
            class_change_time_distributions={
                "Class 0": {"Class 1": ciw.dists.Exponential(1), "Class 2": ciw.dists.Exponential(2)},
                "Class 1": {"Class 0": ciw.dists.Exponential(3), "Class 2": ciw.dists.Exponential(1)},
                "Class 2": {"Class 0": ciw.dists.Exponential(3), "Class 1": ciw.dists.Exponential(3)}
            },
            priority_classes=({"Class 0": 0, "Class 1": 1, "Class 2": 2}, ["resample"]),
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(1000)
        self.assertEqual(len(Q.nodes[-1].all_individuals), 3070)


    def test_preemptive_priorities_resume_options(self):
        """
        One customer of class 1 arrives at date 1. Class 1 customers alternate
        between service times of 6 and 3. One customer of class 0 arrives at
        date 3. They have deterministic service times of 10.

        The first customer would be displaced at time 3 and would restart
        service at time 13.
            - Under "restart" we would expect customer 1 to leave at time 19
            (service time = 6)
            - Under "resume" we would expect customer 1 to leave at time 17
            (service time = 6 - 2 = 4)
            - Under "resample" we would expect the customer to leave at time 16
            (service time = 3)
        """
        # Testing under restart
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Sequential([3, float("inf")])],
                "Class 1": [ciw.dists.Sequential([1, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(10)],
                "Class 1": [ciw.dists.Sequential([6, 3])],
            },
            number_of_servers=[1],
            priority_classes=({"Class 0": 0, "Class 1": 1}, ["restart"]),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records(only=["service"])
        r1, r2 = recs
        self.assertEqual(r1.arrival_date, 3)
        self.assertEqual(r1.service_start_date, 3)
        self.assertEqual(r1.service_end_date, 13)
        self.assertEqual(r1.service_time, 10)
        self.assertEqual(r1.waiting_time, 0)

        self.assertEqual(r2.arrival_date, 1)
        self.assertEqual(r2.service_start_date, 13)
        self.assertEqual(r2.service_end_date, 19)
        self.assertEqual(r2.service_time, 6)
        self.assertEqual(r2.waiting_time, 12)

        # Testing under resume
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Sequential([3, float("inf")])],
                "Class 1": [ciw.dists.Sequential([1, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(10)],
                "Class 1": [ciw.dists.Sequential([6, 3])],
            },
            number_of_servers=[1],
            priority_classes=({"Class 0": 0, "Class 1": 1}, ["resume"]),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records(only=["service"])
        r1, r2 = recs
        self.assertEqual(r1.arrival_date, 3)
        self.assertEqual(r1.service_start_date, 3)
        self.assertEqual(r1.service_end_date, 13)
        self.assertEqual(r1.service_time, 10)
        self.assertEqual(r1.waiting_time, 0)

        self.assertEqual(r2.arrival_date, 1)
        self.assertEqual(r2.service_start_date, 13)
        self.assertEqual(r2.service_end_date, 17)
        self.assertEqual(r2.service_time, 4)
        self.assertEqual(r2.waiting_time, 12)

        # Testing under resample
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Sequential([3, float("inf")])],
                "Class 1": [ciw.dists.Sequential([1, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(10)],
                "Class 1": [ciw.dists.Sequential([6, 3])],
            },
            number_of_servers=[1],
            priority_classes=({"Class 0": 0, "Class 1": 1}, ["resample"]),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records(only=["service"])
        r1, r2 = recs
        self.assertEqual(r1.arrival_date, 3)
        self.assertEqual(r1.service_start_date, 3)
        self.assertEqual(r1.service_end_date, 13)
        self.assertEqual(r1.service_time, 10)
        self.assertEqual(r1.waiting_time, 0)

        self.assertEqual(r2.arrival_date, 1)
        self.assertEqual(r2.service_start_date, 13)
        self.assertEqual(r2.service_end_date, 16)
        self.assertEqual(r2.service_time, 3)
        self.assertEqual(r2.waiting_time, 12)

    def test_data_records_for_interrupted_individuals(self):
        """
        Customers arrive every 7 time units. Services last 4 time units.
        There is one server, who goes off duty at time 24 and comes back at time 29.
        There will be one interrupted individual:
          - ind 3; arrives 21; interrupted 24; resumed 29; finishes 30.
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(7)],
            service_distributions=[ciw.dists.Deterministic(4)],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 1], shift_end_dates=[24, 29, 37], preemption="resume")],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(36)
        recs = Q.get_all_records()

        recs_ind3 = [r for r in recs if r.id_number == 3]
        self.assertEqual(len(recs_ind3), 2)

        interrupted_record = [r for r in recs_ind3 if r.record_type == "interrupted service"][0]
        resumed_record = [r for r in recs_ind3 if r.record_type == "service"][0]
        self.assertEqual(interrupted_record.arrival_date, 21)
        self.assertEqual(interrupted_record.service_start_date, 21)
        self.assertEqual(interrupted_record.service_time, 4)
        self.assertEqual(interrupted_record.exit_date, 24)
        self.assertEqual(resumed_record.arrival_date, 21)
        self.assertEqual(resumed_record.service_start_date, 29)
        self.assertEqual(resumed_record.service_time, 1)
        self.assertEqual(resumed_record.service_end_date, 30)
        self.assertEqual(resumed_record.exit_date, 30)

    def test_preemptive_priorities_resume_options_due_to_schedule(self):
        """
        One customer of class 1 arrives at date 1. Class 1 customers alternate
        between service times of 6 and 3. One customer of class 0 arrives at
        date 3. They have deterministic service times of 10.

        Servers have a schedule, 1 server is on duty from the start, then 2
        servers are on duty from time 5 onwards.

        The first customer would be displaced at time 3. Then and would restart
        service at time 5.
            - Under "restart" we would expect customer 1 to leave at time 11
            (service time = 6)
            - Under "resume" we would expect customer 1 to leave at time 9
            (service time = 6 - 2 = 4)
            - Under "resample" we would expect the customer to leave at time 8
            (service time = 3)
        """
        # Testing under restart
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Sequential([3, float("inf")])],
                "Class 1": [ciw.dists.Sequential([1, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(10)],
                "Class 1": [ciw.dists.Sequential([6, 3])],
            },
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 2], shift_end_dates=[5, 100])],
            priority_classes=({"Class 0": 0, "Class 1": 1}, ["restart"]),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records(only=["service"])
        r2, r1 = recs
        self.assertEqual(r1.arrival_date, 3)
        self.assertEqual(r1.service_start_date, 3)
        self.assertEqual(r1.service_end_date, 13)
        self.assertEqual(r1.service_time, 10)
        self.assertEqual(r1.waiting_time, 0)

        self.assertEqual(r2.arrival_date, 1)
        self.assertEqual(r2.service_start_date, 5)
        self.assertEqual(r2.service_end_date, 11)
        self.assertEqual(r2.service_time, 6)
        self.assertEqual(r2.waiting_time, 4)

        # Testing under resume
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Sequential([3, float("inf")])],
                "Class 1": [ciw.dists.Sequential([1, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(10)],
                "Class 1": [ciw.dists.Sequential([6, 3])],
            },
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 2], shift_end_dates=[5, 100])],
            priority_classes=({"Class 0": 0, "Class 1": 1}, ["resume"]),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records(only="service")
        r2, r1 = recs
        self.assertEqual(r1.arrival_date, 3)
        self.assertEqual(r1.service_start_date, 3)
        self.assertEqual(r1.service_end_date, 13)
        self.assertEqual(r1.service_time, 10)
        self.assertEqual(r1.waiting_time, 0)

        self.assertEqual(r2.arrival_date, 1)
        self.assertEqual(r2.service_start_date, 5)
        self.assertEqual(r2.service_end_date, 9)
        self.assertEqual(r2.service_time, 4)
        self.assertEqual(r2.waiting_time, 4)

        # Testing under resample
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Sequential([3, float("inf")])],
                "Class 1": [ciw.dists.Sequential([1, float("inf")])],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(10)],
                "Class 1": [ciw.dists.Sequential([6, 3])],
            },
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 2], shift_end_dates=[5, 100])],
            priority_classes=({"Class 0": 0, "Class 1": 1}, ["resample"]),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records(only=["service"])
        r2, r1 = recs
        self.assertEqual(r1.arrival_date, 3)
        self.assertEqual(r1.service_start_date, 3)
        self.assertEqual(r1.service_end_date, 13)
        self.assertEqual(r1.service_time, 10)
        self.assertEqual(r1.waiting_time, 0)

        self.assertEqual(r2.arrival_date, 1)
        self.assertEqual(r2.service_start_date, 5)
        self.assertEqual(r2.service_end_date, 8)
        self.assertEqual(r2.service_time, 3)
        self.assertEqual(r2.waiting_time, 4)

    def test_do_not_repeat_finish_service_for_blocked_individuals(self):
        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Sequential(sequence=[3.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                ciw.dists.Sequential(sequence=[1.0, 1.0, float("inf")]),
            ],
            service_distributions=[
                ciw.dists.Deterministic(value=1.0),
                ciw.dists.Deterministic(value=300.0),
            ],
            routing=[[0.0, 1.0], [0.0, 0.0]],
            number_of_servers=[10, 2],
            queue_capacities=[float("inf"), 0],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(5)
        expected_blocked_queue = [
            (1, 3),
            (1, 4),
            (1, 5),
            (1, 6),
            (1, 7),
            (1, 8),
            (1, 9),
        ]
        self.assertEqual(set(Q.nodes[2].blocked_queue), set(expected_blocked_queue))

    def test_shift_change_before_arrival(self):
         N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential(sequence=[2.0, float('inf')])],
            service_distributions=[ciw.dists.Deterministic(value=1.0)],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 2], shift_end_dates=[1.0, 10.0], preemption=False)]
         )
         Q = ciw.Simulation(N)
         Q.simulate_until_max_time(10.5)
         recs = Q.get_all_records()
         self.assertEqual(len(recs), 1)
