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

class TestProcessBased(unittest.TestCase):

    def test_network_takes_routing_function(self):
        N = ciw.create_network(
            Arrival_distributions=[['Exponential', 1]],
            Service_distributions=[['Exponential', 2]],
            Number_of_servers=[1],
            Routing=generator_function_1
        )
        self.assertEqual(N.process_based, True)
        Q = ciw.Simulation(N)
        self.assertEqual(str(Q), 'Simulation')

    def test_individuals_recieve_route(self):
        N = ciw.create_network(
            Arrival_distributions=[['Deterministic', 1]],
            Service_distributions=[['Deterministic', 1000]],
            Number_of_servers=[1],
            Routing=generator_function_1
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(4.5)
        inds = Q.nodes[1].all_individuals
        for ind in inds:
            self.assertEqual(ind.route, [1, 1, 1])

    def test_routing_correct(self):
        N = ciw.create_network(
            Arrival_distributions=[['Sequential', [1, 10000]], 'NoArrivals', 'NoArrivals'],
            Service_distributions=[['Deterministic', 2], ['Deterministic', 2], ['Deterministic', 2]],
            Number_of_servers=[1, 1, 1],
            Routing=generator_function_2
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
            Arrival_distributions=[['Exponential',1],'NoArrivals','NoArrivals'],
            Service_distributions=[['Exponential',2],['Exponential',2],['Exponential',2]],
            Number_of_servers= [1,1,1],
            Routing=generator_function_3
        )
        ciw.seed(0)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_customers(1000, method='Finish')
        inds = Q.nodes[-1].all_individuals
        routes_counter = Counter([tuple(dr.node for dr in ind.data_records) for ind in inds])
        self.assertEqual(routes_counter,  Counter({(1, 3, 2, 3): 522, (1, 2, 2, 3, 2): 368, (1, 1): 110}))


        
        
