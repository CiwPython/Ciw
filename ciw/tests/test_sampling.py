import unittest
import ciw
from random import seed
from hypothesis import given
from hypothesis.strategies import floats, integers, lists, random_module
import os
import copy
from numpy import random as nprandom


def set_seed(x):
    seed(x)
    nprandom.seed(x)

class TestSimulation(unittest.TestCase):

    def test_sampling_uniform_dist(self):
        Arrival_distributions = [['Uniform', 2.2, 3.3]]
        Service_distributions = [['Uniform', 2.2, 3.3]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nu = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 2.89)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 3.02)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 3.07)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 3.24)
        self.assertEqual(round(Nu.simulation.service_times[Nu.id_number][0](), 2), 3.01)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 3.21)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.23)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.71)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 3.24)
        self.assertEqual(round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.91)

    @given(u=lists(floats(min_value=0.0, max_value=10000), min_size=2, max_size=2, unique=True).map(sorted),
           rm=random_module())
    def test_sampling_uniform_dist_hypothesis(self, u, rm):
        ul, uh = u[0], u[1]
        Arrival_distributions = [['Uniform', ul, uh]]
        Service_distributions = [['Uniform', ul, uh]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nu = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(ul <= Nu.simulation.service_times[Nu.id_number][0]() <= uh)
            self.assertTrue(ul <= Nu.simulation.inter_arrival_times[Nu.id_number][0]() <= uh)

    def test_sampling_deterministic_dist(self):
        Arrival_distributions = [['Deterministic', 4.4]]
        Service_distributions = [['Deterministic', 4.4]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nd = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)

    @given(d=floats(min_value=0.0, max_value=10000),
           rm=random_module())
    def test_sampling_deterministic_dist_hypothesis(self, d, rm):
        Arrival_distributions = [['Deterministic', d]]
        Service_distributions = [['Deterministic', d]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nd = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertEqual(Nd.simulation.service_times[Nd.id_number][0](), d)
            self.assertEqual(Nd.simulation.inter_arrival_times[Nd.id_number][0](), d)

    def test_sampling_triangular_dist(self):
        Arrival_distributions = [['Triangular', 1.1, 6.6, 1.5]]
        Service_distributions = [['Triangular', 1.1, 6.6, 1.5]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nt = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 3.35)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 3.91)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 4.20)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 5.33)
        self.assertEqual(round(Nt.simulation.service_times[Nt.id_number][0](), 2), 3.90)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 5.12)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 1.35)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 2.73)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 5.34)
        self.assertEqual(round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 3.46)

    @given(t=lists(floats(min_value=0.0, max_value=10000), min_size=3, max_size=3, unique=True).map(sorted),
           rm=random_module())
    def test_sampling_triangular_dist_hypothesis(self, t, rm):
        tl, tm, th = t[0], t[1], t[2]
        Arrival_distributions = [['Triangular', tl, th, tm]]
        Service_distributions = [['Triangular', tl, th, tm]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nt = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(tl <= Nt.simulation.service_times[Nt.id_number][0]() <= th)
            self.assertTrue(tl <= Nt.simulation.inter_arrival_times[Nt.id_number][0]() <= th)

    def test_sampling_exponential_dist(self):
        Arrival_distributions = [['Exponential', 4.4]]
        Service_distributions = [['Exponential', 4.4]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Ne = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.22)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.31)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.36)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.65)
        self.assertEqual(round(Ne.simulation.service_times[Ne.id_number][0](), 2), 0.31)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.58)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.01)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.14)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.65)
        self.assertEqual(round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.24)

    @given(e=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_exponential_dist_hypothesis(self, e, rm):
        Arrival_distributions = [['Exponential', e]]
        Service_distributions = [['Exponential', e]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Ne = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Ne.simulation.service_times[Ne.id_number][0]() >= 0.0)
            self.assertTrue(Ne.simulation.inter_arrival_times[Ne.id_number][0]() >= 0.0)

    def test_sampling_gamma_dist(self):
        Arrival_distributions = [['Gamma', 0.6, 1.2]]
        Service_distributions = [['Gamma', 0.6, 1.2]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Ng = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 0.00)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 2.59)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 1.92)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 0.47)
        self.assertEqual(round(Ng.simulation.service_times[Ng.id_number][0](), 2), 0.61)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.00)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 1.07)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 1.15)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.75)
        self.assertEqual(round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.00)

    @given(ga=floats(min_value=0.001, max_value=10000),
           gb=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_gamma_dist_hypothesis(self, ga, gb, rm):
        Arrival_distributions = [['Gamma', ga, gb]]
        Service_distributions = [['Gamma', ga, gb]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Ng = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Ng.simulation.service_times[Ng.id_number][0]() >= 0.0)
            self.assertTrue(Ng.simulation.inter_arrival_times[Ng.id_number][0]() >= 0.0)

    def test_sampling_lognormal_dist(self):
        Arrival_distributions = [['Lognormal', 0.8, 0.2]]
        Service_distributions = [['Lognormal', 0.8, 0.2]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nl = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 2.62)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 1.64)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 2.19)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 2.31)
        self.assertEqual(round(Nl.simulation.service_times[Nl.id_number][0](), 2), 2.48)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.51)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.33)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 1.96)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.32)
        self.assertEqual(round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.70)

    @given(lm=floats(min_value=-200, max_value=200),
           lsd=floats(min_value=0.001, max_value=80),
           rm=random_module())
    def test_sampling_lognormal_dist_hypothesis(self, lm, lsd, rm):
        Arrival_distributions = [['Lognormal', lm, lsd]]
        Service_distributions = [['Lognormal', lm, lsd]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nl = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nl.simulation.service_times[Nl.id_number][0]() >= 0.0)
            self.assertTrue(Nl.simulation.inter_arrival_times[Nl.id_number][0]() >= 0.0)

    def test_sampling_weibull_dist(self):
        Arrival_distributions = [['Weibull', 0.9, 0.8]]
        Service_distributions = [['Weibull', 0.9, 0.8]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nw = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 0.87)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 1.31)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 1.60)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 3.34)
        self.assertEqual(round(Nw.simulation.service_times[Nw.id_number][0](), 2), 1.31)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 2.91)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.01)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.50)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 3.36)
        self.assertEqual(round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.95)

    @given(wa=floats(min_value=0.01, max_value=200),
           wb=floats(min_value=0.01, max_value=200),
           rm=random_module())
    def test_sampling_weibull_dist_hypothesis(self, wa, wb, rm):
        Arrival_distributions = [['Weibull', wa, wb]]
        Service_distributions = [['Weibull', wa, wb]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nw = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nw.simulation.service_times[Nw.id_number][0]() >= 0.0)
            self.assertTrue(Nw.simulation.inter_arrival_times[Nw.id_number][0]() >= 0.0)

    def test_sampling_empirical_dist(self):
        my_empirical_dist = [8.0, 8.0, 8.0, 8.8, 8.8, 12.3]
        Arrival_distributions = [['Empirical', 'ciw/tests/datafortesting/sample_empirical_dist.csv']]
        Service_distributions = [['Empirical', my_empirical_dist]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nem = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.8)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.8)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.8)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 12.3)
        self.assertEqual(round(Nem.simulation.service_times[Nem.id_number][0](), 2), 8.8)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.3)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.0)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.7)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.3)
        self.assertEqual(round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.1)

    @given(dist=lists(floats(min_value=0.001, max_value=10000), min_size=1, max_size=20),
           rm=random_module())
    def test_sampling_empirical_dist_hypothesis(self, dist, rm):
        my_empirical_dist = dist
        Arrival_distributions = [['Empirical', my_empirical_dist]]
        Service_distributions = [['Empirical', 'ciw/tests/datafortesting/sample_empirical_dist.csv']]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time,)
        Nem = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nem.simulation.service_times[Nem.id_number][0]() in set([7.0, 7.1, 7.2, 7.3, 7.7, 7.8]))
            self.assertTrue(Nem.simulation.inter_arrival_times[Nem.id_number][0]() in set(my_empirical_dist))

    def test_sampling_custom_dist(self):
        my_custom_dist = [[0.2, 3.7], [0.5, 3.8], [0.3, 4.1]]
        Arrival_distributions = [['Custom', 'my_custom_dist']]
        Service_distributions = [['Custom', 'my_custom_dist']]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time,
                           my_custom_dist=my_custom_dist)
        Nc = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(round(Nc.simulation.service_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(Nc.simulation.service_times[Nc.id_number][0](), 2), 4.1)
        self.assertEqual(round(Nc.simulation.service_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(Nc.simulation.service_times[Nc.id_number][0](), 2), 4.1)
        self.assertEqual(round(Nc.simulation.service_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 4.1)
        self.assertEqual(round(Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 3.7)

    @given(custs=lists(floats(min_value=0.001, max_value=10000), unique=True, min_size=2),
           rm=random_module())
    def test_sampling_custom_dist_hypothesis(self, custs, rm):
        Arrival_distributions = [['Custom', 'my_custom_dist']]
        Service_distributions = [['Custom', 'my_custom_dist']]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        cust_vals = [round(i, 10) for i in custs]
        numprobs = len(cust_vals)
        probs = [1.0/numprobs for i in range(numprobs)]
        my_custom_dist = [list(i) for i in (zip(probs, cust_vals))]
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time,
                           my_custom_dist=my_custom_dist)
        Nc = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nc.simulation.service_times[Nc.id_number][0]() in set(cust_vals))
            self.assertTrue(Nc.simulation.inter_arrival_times[Nc.id_number][0]() in set(cust_vals))

    def test_no_arrivals_dist(self):
        Arrival_distributions = ['NoArrivals']
        Service_distributions = [['Deterministic', 6.6]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nna = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(Nna.simulation.inter_arrival_times[Nna.id_number][0](), 'Inf')

    def test_error_dist(self):
        Arrival_distributions = ['NoArrivals']
        Service_distributions = [['testerror', 9]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        Q = ciw.Simulation(Arrival_distributions=Arrival_distributions,
                           Service_distributions=Service_distributions,
                           Number_of_servers=Number_of_servers,
                           Transition_matrices=Transition_matrices,
                           Simulation_time=Simulation_time)
        Nna = Q.transitive_nodes[0]
        set_seed(5)
        self.assertEqual(Nna.simulation.service_times[Nna.id_number][0], False)

