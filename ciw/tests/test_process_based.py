import unittest
import ciw
import random
from collections import Counter


def generator_function_1(ind):
    return [1, 1, 1]


def generator_function_2(ind):
    return [1, 1, 2, 1, 3]


def generator_function_3(ind):
    rnd = random.random()
    if rnd < 0.4:
        return [1, 2, 2, 3, 2]
    if rnd < 0.5:
        return [1, 1]
    return [1, 3, 2, 3]


def generator_function_4(ind):
    return [2, 1, 3, 1, 1]


def generator_function_5(ind):
    return [3, 2, 3, 2, 3]


def generator_function_6(ind):
    return [3]


def generator_function_7(ind):
    rnd = random.random()
    if rnd < 0.4:
        return [2, 1, 2]
    return [2, 1, 1, 2]


def generator_function_8(ind):
    if ind.customer_class == 'Class 0':
        return [1]
    return [1, 1, 1]

class ClassForProcessBasedMethod:
    def __init__(self, n):
        self.n = n
    def generator_method(self, ind):
        return [1, 1, 1]


class TestProcessBased(unittest.TestCase):
    def test_network_takes_routing_function(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1)],
            service_distributions=[ciw.dists.Exponential(2)],
            number_of_servers=[1],
            routing=[generator_function_1],
        )
        self.assertEqual(N.process_based, True)
        Q = ciw.Simulation(N)
        self.assertEqual(str(Q), "Simulation")

    def test_individuals_recieve_route(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(1000)],
            number_of_servers=[1],
            routing=[generator_function_1],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(4.5)
        inds = Q.nodes[1].all_individuals
        for ind in inds:
            self.assertEqual(ind.route, [1, 1, 1])

    def test_routing_correct(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, 10000]), None, None],
            service_distributions=[
                ciw.dists.Deterministic(2),
                ciw.dists.Deterministic(2),
                ciw.dists.Deterministic(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=[generator_function_2, ciw.no_routing, ciw.no_routing],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(4)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [1, 2, 1, 3])
        self.assertEqual([dr.node for dr in ind.data_records], [1])
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(6)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [2, 1, 3])
        self.assertEqual([dr.node for dr in ind.data_records], [1, 1])
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(8)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [1, 3])
        self.assertEqual([dr.node for dr in ind.data_records], [1, 1, 2])
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(10)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [3])
        self.assertEqual([dr.node for dr in ind.data_records], [1, 1, 2, 1])
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(12)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [])
        self.assertEqual([dr.node for dr in ind.data_records], [1, 1, 2, 1, 3])

    def test_probablistic_process_routes(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1), None, None],
            service_distributions=[
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=[generator_function_3, ciw.no_routing, ciw.no_routing],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(500, method="Finish")
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter(
            [tuple(dr.node for dr in ind.data_records) for ind in inds]
        )
        self.assertEqual(
            routes_counter,
            Counter({(1, 3, 2, 3): 244, (1, 2, 2, 3, 2): 204, (1, 1): 52}),
        )

    def test_error_when_ind_sent_wrong_place(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1)],
            service_distributions=[ciw.dists.Exponential(2)],
            number_of_servers=[1],
            routing=[ciw.no_routing],
        )
        Q = ciw.Simulation(N)
        self.assertRaises(ValueError, Q.simulate_until_max_time, 20)

        N = ciw.create_network(
            arrival_distributions=[None, ciw.dists.Exponential(1), None],
            service_distributions=[
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=[ciw.no_routing, generator_function_2, ciw.no_routing],
        )
        Q = ciw.Simulation(N)
        self.assertRaises(ValueError, Q.simulate_until_max_time, 20)

    def test_routing_from_different_starting_points(self):
        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(1),
                ciw.dists.Exponential(1),
                None,
            ],
            service_distributions=[
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=[generator_function_2, generator_function_4, ciw.no_routing],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(500, method="Finish")
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter([tuple(dr.node for dr in ind.data_records) for ind in inds])
        self.assertEqual(
            routes_counter,
            Counter({(1, 1, 2, 1, 3): 245, (2, 1, 3, 1, 1): 255})
        )

        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(1),
                ciw.dists.Exponential(1),
                ciw.dists.Exponential(1),
            ],
            service_distributions=[
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=[generator_function_1, generator_function_4, generator_function_5],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(500, method="Finish")
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter([tuple(dr.node for dr in ind.data_records) for ind in inds])
        self.assertEqual(
            routes_counter,
            Counter({(3, 2, 3, 2, 3): 256, (1, 1, 1): 155, (2, 1, 3, 1, 1): 89}),
        )

        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(1),
                ciw.dists.Exponential(1),
                ciw.dists.Exponential(1),
            ],
            service_distributions=[
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=[generator_function_2, generator_function_4, generator_function_5],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(500, method="Finish")
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter([tuple(dr.node for dr in ind.data_records) for ind in inds])
        self.assertEqual(
            routes_counter,
            Counter({(3, 2, 3, 2, 3): 233, (1, 1, 2, 1, 3): 148, (2, 1, 3, 1, 1): 119}),
        )

        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(1),
                ciw.dists.Exponential(1),
                ciw.dists.Exponential(1),
            ],
            service_distributions=[
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=[generator_function_2, generator_function_4, generator_function_6],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(500, method="Finish")
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter([tuple(dr.node for dr in ind.data_records) for ind in inds])
        self.assertEqual(
            routes_counter,
            Counter({(3,): 385, (1, 1, 2, 1, 3): 57, (2, 1, 3, 1, 1): 58}),
        )

        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(1),
                ciw.dists.Exponential(1),
                None,
            ],
            service_distributions=[
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
                ciw.dists.Exponential(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=[generator_function_1, generator_function_7, ciw.no_routing],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(500, method="Finish")
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter([tuple(dr.node for dr in ind.data_records) for ind in inds])
        self.assertEqual(
            routes_counter,
            Counter({(2, 1, 1, 2): 172, (2, 1, 2): 169, (1, 1, 1): 159})
        )

    def test_customer_class_based_routing(self):
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(1)],
                "Class 1": [ciw.dists.Exponential(1)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(2)],
                "Class 1": [ciw.dists.Exponential(2)],
            },
            number_of_servers=[1],
            routing=[generator_function_8],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(500, method="Finish")
        inds = Q.nodes[-1].all_individuals
        routes_counter = set([tuple([ind.customer_class, tuple(dr.node for dr in ind.data_records)]) for ind in inds])
        self.assertEqual(routes_counter, {('Class 1', (1, 1, 1)), ('Class 0', (1,))})

    def test_process_based_takes_methods(self):
        import types
        G = ClassForProcessBasedMethod(5)
        self.assertTrue(isinstance(G.generator_method, types.MethodType))
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(1000)],
            number_of_servers=[1],
            routing=[G.generator_method],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(4.5)
        inds = Q.nodes[1].all_individuals
        for ind in inds:
            self.assertEqual(ind.route, [1, 1, 1])
