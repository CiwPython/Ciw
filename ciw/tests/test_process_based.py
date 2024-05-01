import unittest
import ciw
import random
from collections import Counter

def generator_function_1(ind, simulation):
    return [1, 1]


def generator_function_2(ind, simulation):
    return [1, 2, 1, 3]


def generator_function_3(ind, simulation):
    rnd = random.random()
    if rnd < 0.4:
        return [2, 2, 3, 2]
    if rnd < 0.5:
        return [1]
    return [3, 2, 3]

def generator_function_4(ind, simulation):
    return []

class ClassForProcessBasedMethod:
    def __init__(self, n):
        self.n = n
    def generator_method(self, ind, simulation):
        return [1, 1]

def flexible_generator_1(ind, simulation):
    return [[2], [3, 4, 5], [6]]

class TestProcessBased(unittest.TestCase):
    def test_network_takes_routing_function(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1)],
            service_distributions=[ciw.dists.Exponential(2)],
            number_of_servers=[1],
            routing=ciw.routing.ProcessBased(generator_function_1),
        )
        Q = ciw.Simulation(N)
        self.assertEqual(str(Q), "Simulation")

    def test_individuals_recieve_route(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(1000)],
            number_of_servers=[1],
            routing=ciw.routing.ProcessBased(generator_function_1),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(4.5)
        inds = Q.nodes[1].all_individuals
        for ind in inds:
            self.assertEqual(ind.route, [1, 1])

    def test_routing_correct(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, 10000]), None, None],
            service_distributions=[
                ciw.dists.Deterministic(2),
                ciw.dists.Deterministic(2),
                ciw.dists.Deterministic(2),
            ],
            number_of_servers=[1, 1, 1],
            routing=ciw.routing.ProcessBased(generator_function_2),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(4)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [2, 1, 3])
        self.assertEqual([dr.node for dr in ind.data_records], [1])
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(6)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [1, 3])
        self.assertEqual([dr.node for dr in ind.data_records], [1, 1])
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(8)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [3])
        self.assertEqual([dr.node for dr in ind.data_records], [1, 1, 2])
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(10)
        ind = Q.get_all_individuals()[0]
        self.assertEqual(ind.route, [])
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
            routing=ciw.routing.ProcessBased(generator_function_3),
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
            routing={
                "Class 0": ciw.routing.ProcessBased(generator_function_4),
                "Class 1": ciw.routing.ProcessBased(generator_function_1)
            }
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
            routing=ciw.routing.ProcessBased(G.generator_method),
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(4.5)
        inds = Q.nodes[1].all_individuals
        for ind in inds:
            self.assertEqual(ind.route, [1, 1])

    def test_flexible_process_based(self):
        ## First test 'any-random':
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(rate=1), None, None, None, None, None],
            service_distributions=[ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2)],
            number_of_servers=[3, 3, 3, 3, 3, 3],
            routing=ciw.routing.FlexibleProcessBased(
                route_function=flexible_generator_1,
                rule='any',
                choice='random'
            )
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(1000)
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter(
            [tuple(dr.node for dr in ind.data_records) for ind in inds]
        )
        self.assertEqual(
            routes_counter,
            Counter({(1, 2, 4, 6): 350, (1, 2, 5, 6): 333, (1, 2, 3, 6): 317}), # all evenly spread
        )

        ## Now test 'any-jsq' (flooding Node 4 so no customers ever go here):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(rate=1), None, None, None, None, None],
            service_distributions=[ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Deterministic(value=200000), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2)],
            number_of_servers=[3, 3, 3, 3, 3, 3],
            routing=ciw.routing.FlexibleProcessBased(
                route_function=flexible_generator_1,
                rule='any',
                choice='jsq'
            )
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(1000)
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter(
            [tuple(dr.node for dr in ind.data_records) for ind in inds]
        )
        self.assertEqual(
            routes_counter,
            Counter({(1, 2, 5, 6): 503, (1, 2, 3, 6): 497}),  # evenly spread between the two unflooded nodes
        )

        ## Now test 'any-lb' (flooding Node 4 so no customers ever go here):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(rate=1), None, None, None, None, None],
            service_distributions=[ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Deterministic(value=200000), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2)],
            number_of_servers=[3, 3, 3, 3, 3, 3],
            routing=ciw.routing.FlexibleProcessBased(
                route_function=flexible_generator_1,
                rule='any',
                choice='lb'
            )
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(1000)
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter(
            [tuple(dr.node for dr in ind.data_records) for ind in inds]
        )
        self.assertEqual(
            routes_counter,
            Counter({(1, 2, 5, 6): 508, (1, 2, 3, 6): 492}),  # evenly spread between the two unflooded nodes
        )


        ## Now test 'all-random':
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(rate=1), None, None, None, None, None],
            service_distributions=[ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2), ciw.dists.Exponential(rate=2)],
            number_of_servers=[3, 3, 3, 3, 3, 3],
            routing=ciw.routing.FlexibleProcessBased(
                route_function=flexible_generator_1,
                rule='all',
                choice='random'
            )
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(1000)
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter(
            [tuple(dr.node for dr in ind.data_records) for ind in inds]
        )
        self.assertEqual(routes_counter[(1, 2, 3, 4, 5, 6)], 169)
        self.assertEqual(routes_counter[(1, 2, 3, 5, 4, 6)], 139)
        self.assertEqual(routes_counter[(1, 2, 4, 3, 5, 6)], 185)
        self.assertEqual(routes_counter[(1, 2, 4, 5, 3, 6)], 166)
        self.assertEqual(routes_counter[(1, 2, 5, 3, 4, 6)], 186)
        self.assertEqual(routes_counter[(1, 2, 5, 4, 3, 6)], 155)

    def test_flexible_process_based_error_raising(self):
        self.assertRaises(ValueError, ciw.routing.FlexibleProcessBased, flexible_generator_1, 'something', 'random')
        self.assertRaises(ValueError, ciw.routing.FlexibleProcessBased, flexible_generator_1, 'all', 'something')
