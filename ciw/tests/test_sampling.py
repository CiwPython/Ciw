import unittest
import ciw
from random import random, choice
from hypothesis import given
from hypothesis.strategies import (floats, integers, lists,
    random_module, assume, text)
import os
import copy


def custom_function():
    """
    Custom function to test user defined function functionality.
    """
    val = random()
    if int(str(val*10)[0]) % 2 == 0:
        return 2 * val
    return val / 2.0

def time_dependent_function_1(current_time):
    if current_time < 10.0:
        return 3.0
    return 5.0

def time_dependent_function_2(current_time):
    if current_time < 20.0:
        return current_time / 2.0
    return 8.0

def broken_td_func(current_time):
    return -4.0

class TestSampling(unittest.TestCase):

    def test_sampling_uniform_dist(self):
        params = {
            'Arrival_distributions': [['Uniform', 2.2, 3.3]],
            'Service_distributions': [['Uniform', 2.2, 3.3]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nu = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Nu.simulation.service_times[Nu.id_number][0](), 2), 2.89)
        self.assertEqual(round(
            Nu.simulation.service_times[Nu.id_number][0](), 2), 3.02)
        self.assertEqual(round(
            Nu.simulation.service_times[Nu.id_number][0](), 2), 3.07)
        self.assertEqual(round(
            Nu.simulation.service_times[Nu.id_number][0](), 2), 3.24)
        self.assertEqual(round(
            Nu.simulation.service_times[Nu.id_number][0](), 2), 3.01)
        self.assertEqual(round(
            Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 3.21)
        self.assertEqual(round(
            Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.23)
        self.assertEqual(round(
            Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.71)
        self.assertEqual(round(
            Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 3.24)
        self.assertEqual(round(
            Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2), 2.91)

    @given(u=lists(floats(min_value=0.0, max_value=10000),
                   min_size=2,
                   max_size=2,
                   unique=True).map(sorted),
           rm=random_module())
    def test_sampling_uniform_dist_hypothesis(self, u, rm):
        ul, uh = u[0], u[1]
        params = {
            'Arrival_distributions': [['Uniform', ul, uh]],
            'Service_distributions': [['Uniform', ul, uh]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nu = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                ul <= Nu.simulation.service_times[Nu.id_number][0]() <= uh)
            self.assertTrue(
                ul <= Nu.simulation.inter_arrival_times[Nu.id_number][0]() <= uh)

    def test_error_uniform_dist(self):
        Arrival_distributions = [['Uniform', 2.2, 3.3]]
        Arrival_distributions_E = [['Uniform', -2.2, 3.3]]
        Arrival_distributions_EE = [['Uniform', 3.3, 2.2]]
        Service_distributions = [['Uniform', 2.2, 3.3]]
        Service_distributions_E = [['Uniform', 2.2, -3.3]]
        Service_distributions_EE = [['Uniform', 3.3, 2.2]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions_E,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions_EE,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_E,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_EE,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})

    def test_sampling_deterministic_dist(self):
        params = {
            'Arrival_distributions': [['Deterministic', 4.4]],
            'Service_distributions': [['Deterministic', 4.4]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nd = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.service_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)
        self.assertEqual(round(
            Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2), 4.40)

    @given(d=floats(min_value=0.0, max_value=10000),
           rm=random_module())
    def test_sampling_deterministic_dist_hypothesis(self, d, rm):
        params = {
            'Arrival_distributions': [['Deterministic', d]],
            'Service_distributions': [['Deterministic', d]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nd = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertEqual(
                Nd.simulation.service_times[Nd.id_number][0](), d)
            self.assertEqual(
                Nd.simulation.inter_arrival_times[Nd.id_number][0](), d)

    def test_error_deterministic_dist(self):
        Arrival_distributions = [['Deterministic', 2.2]]
        Arrival_distributions_E = [['Deterministic', -2.2]]
        Service_distributions = [['Deterministic', 3.3]]
        Service_distributions_E = [['Deterministic', -3.3]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions_E,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                 {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_E,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})

    def test_sampling_triangular_dist(self):
        params = {
            'Arrival_distributions': [['Triangular', 1.1, 6.6, 1.5]],
            'Service_distributions': [['Triangular', 1.1, 6.6, 1.5]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nt = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Nt.simulation.service_times[Nt.id_number][0](), 2), 3.35)
        self.assertEqual(round(
            Nt.simulation.service_times[Nt.id_number][0](), 2), 3.91)
        self.assertEqual(round(
            Nt.simulation.service_times[Nt.id_number][0](), 2), 4.20)
        self.assertEqual(round(
            Nt.simulation.service_times[Nt.id_number][0](), 2), 5.33)
        self.assertEqual(round(
            Nt.simulation.service_times[Nt.id_number][0](), 2), 3.90)
        self.assertEqual(round(
            Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 5.12)
        self.assertEqual(round(
            Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 1.35)
        self.assertEqual(round(
            Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 2.73)
        self.assertEqual(round(
            Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 5.34)
        self.assertEqual(round(
            Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2), 3.46)

    @given(t=lists(floats(min_value=0.0, max_value=10000),
                   min_size=3,
                   max_size=3,
                   unique=True).map(sorted),
           rm=random_module())
    def test_sampling_triangular_dist_hypothesis(self, t, rm):
        tl, tm, th = t[0], t[1], t[2]
        params = {
            'Arrival_distributions': [['Triangular', tl, th, tm]],
            'Service_distributions': [['Triangular', tl, th, tm]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nt = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                tl <= Nt.simulation.service_times[Nt.id_number][0]() <= th)
            self.assertTrue(
                tl <= Nt.simulation.inter_arrival_times[Nt.id_number][0]() <= th)

    def test_error_triangular_dist(self):
        Arrival_distributions = [['Triangular', 2.2, 3.3, 2.8]]
        Arrival_distributions_E = [['Triangular', -2.2, 3.3, 2.8]]
        Arrival_distributions_EE = [['Triangular', 3.3, 2.2, 2.1]]
        Service_distributions = [['Triangular', 2.2, 3.3, 2.8]]
        Service_distributions_E = [['Triangular', 2.2, -3.3, 2.8]]
        Service_distributions_EE = [['Triangular', 2.2, 2.6, 2.9]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions_E,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions_EE,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_E,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_EE,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})

    def test_sampling_exponential_dist(self):
        params = {
            'Arrival_distributions': [['Exponential', 4.4]],
            'Service_distributions': [['Exponential', 4.4]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Ne = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Ne.simulation.service_times[Ne.id_number][0](), 2), 0.22)
        self.assertEqual(round(
            Ne.simulation.service_times[Ne.id_number][0](), 2), 0.31)
        self.assertEqual(round(
            Ne.simulation.service_times[Ne.id_number][0](), 2), 0.36)
        self.assertEqual(round(
            Ne.simulation.service_times[Ne.id_number][0](), 2), 0.65)
        self.assertEqual(round(
            Ne.simulation.service_times[Ne.id_number][0](), 2), 0.31)
        self.assertEqual(round(
            Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.58)
        self.assertEqual(round(
            Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.01)
        self.assertEqual(round(
            Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.14)
        self.assertEqual(round(
            Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.65)
        self.assertEqual(round(
            Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2), 0.24)

    @given(e=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_exponential_dist_hypothesis(self, e, rm):
        params = {
            'Arrival_distributions': [['Exponential', e]],
            'Service_distributions': [['Exponential', e]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Ne = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Ne.simulation.service_times[Ne.id_number][0]() >= 0.0)
            self.assertTrue(
                Ne.simulation.inter_arrival_times[Ne.id_number][0]() >= 0.0)

    def test_sampling_gamma_dist(self):
        params = {
            'Arrival_distributions': [['Gamma', 0.6, 1.2]],
            'Service_distributions': [['Gamma', 0.6, 1.2]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Ng = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Ng.simulation.service_times[Ng.id_number][0](), 2), 0.00)
        self.assertEqual(round(
            Ng.simulation.service_times[Ng.id_number][0](), 2), 2.59)
        self.assertEqual(round(
            Ng.simulation.service_times[Ng.id_number][0](), 2), 1.92)
        self.assertEqual(round(
            Ng.simulation.service_times[Ng.id_number][0](), 2), 0.47)
        self.assertEqual(round(
            Ng.simulation.service_times[Ng.id_number][0](), 2), 0.61)
        self.assertEqual(round(
            Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.00)
        self.assertEqual(round(
            Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 1.07)
        self.assertEqual(round(
            Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 1.15)
        self.assertEqual(round(
            Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.75)
        self.assertEqual(round(
            Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2), 0.00)

    @given(ga=floats(min_value=0.001, max_value=10000),
           gb=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_gamma_dist_hypothesis(self, ga, gb, rm):
        params = {
            'Arrival_distributions': [['Gamma', ga, gb]],
            'Service_distributions': [['Gamma', ga, gb]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Ng = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Ng.simulation.service_times[Ng.id_number][0]() >= 0.0)
            self.assertTrue(
                Ng.simulation.inter_arrival_times[Ng.id_number][0]() >= 0.0)

    def test_sampling_lognormal_dist(self):
        params = {
            'Arrival_distributions': [['Lognormal', 0.8, 0.2]],
            'Service_distributions': [['Lognormal', 0.8, 0.2]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nl = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Nl.simulation.service_times[Nl.id_number][0](), 2), 2.62)
        self.assertEqual(round(
            Nl.simulation.service_times[Nl.id_number][0](), 2), 1.64)
        self.assertEqual(round(
            Nl.simulation.service_times[Nl.id_number][0](), 2), 2.19)
        self.assertEqual(round(
            Nl.simulation.service_times[Nl.id_number][0](), 2), 2.31)
        self.assertEqual(round(
            Nl.simulation.service_times[Nl.id_number][0](), 2), 2.48)
        self.assertEqual(round(
            Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.51)
        self.assertEqual(round(
            Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.33)
        self.assertEqual(round(
            Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 1.96)
        self.assertEqual(round(
            Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.32)
        self.assertEqual(round(
            Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2), 2.70)

    @given(lm=floats(min_value=-200, max_value=200),
           lsd=floats(min_value=0.001, max_value=80),
           rm=random_module())
    def test_sampling_lognormal_dist_hypothesis(self, lm, lsd, rm):
        params = {
            'Arrival_distributions': [['Lognormal', lm, lsd]],
            'Service_distributions': [['Lognormal', lm, lsd]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nl = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nl.simulation.service_times[Nl.id_number][0]() >= 0.0)
            self.assertTrue(
                Nl.simulation.inter_arrival_times[Nl.id_number][0]() >= 0.0)

    def test_sampling_weibull_dist(self):
        params = {
            'Arrival_distributions': [['Weibull', 0.9, 0.8]],
            'Service_distributions': [['Weibull', 0.9, 0.8]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nw = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Nw.simulation.service_times[Nw.id_number][0](), 2), 0.87)
        self.assertEqual(round(
            Nw.simulation.service_times[Nw.id_number][0](), 2), 1.31)
        self.assertEqual(round(
            Nw.simulation.service_times[Nw.id_number][0](), 2), 1.60)
        self.assertEqual(round(
            Nw.simulation.service_times[Nw.id_number][0](), 2), 3.34)
        self.assertEqual(round(
            Nw.simulation.service_times[Nw.id_number][0](), 2), 1.31)
        self.assertEqual(round(
            Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 2.91)
        self.assertEqual(round(
            Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.01)
        self.assertEqual(round(
            Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.50)
        self.assertEqual(round(
            Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 3.36)
        self.assertEqual(round(
            Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2), 0.95)

    @given(wa=floats(min_value=0.01, max_value=200),
           wb=floats(min_value=0.01, max_value=200),
           rm=random_module())
    def test_sampling_weibull_dist_hypothesis(self, wa, wb, rm):
        params = {
            'Arrival_distributions': [['Weibull', wa, wb]],
            'Service_distributions': [['Weibull', wa, wb]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nw = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nw.simulation.service_times[Nw.id_number][0]() >= 0.0)
            self.assertTrue(
                Nw.simulation.inter_arrival_times[Nw.id_number][0]() >= 0.0)

    def test_sampling_empirical_dist(self):
        my_empirical_dist = [8.0, 8.0, 8.0, 8.8, 8.8, 12.3]
        params = {
            'Arrival_distributions': [['Empirical',
                'ciw/tests/testing_parameters/sample_empirical_dist.csv']],
            'Service_distributions': [['Empirical', my_empirical_dist]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nem = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Nem.simulation.service_times[Nem.id_number][0](), 2), 8.8)
        self.assertEqual(round(
            Nem.simulation.service_times[Nem.id_number][0](), 2), 12.3)
        self.assertEqual(round(
            Nem.simulation.service_times[Nem.id_number][0](), 2), 8.0)
        self.assertEqual(round(
            Nem.simulation.service_times[Nem.id_number][0](), 2), 8.0)
        self.assertEqual(round(
            Nem.simulation.service_times[Nem.id_number][0](), 2), 8.0)
        self.assertEqual(round(
            Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.7)
        self.assertEqual(round(
            Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.7)
        self.assertEqual(round(
            Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.1)
        self.assertEqual(round(
            Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.1)
        self.assertEqual(round(
            Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2), 7.7)

    @given(dist=lists(floats(min_value=0.001, max_value=10000),
                      min_size=1,
                      max_size=20),
           rm=random_module())
    def test_sampling_empirical_dist_hypothesis(self, dist, rm):
        my_empirical_dist = dist
        params = {
            'Arrival_distributions': [['Empirical', my_empirical_dist]],
            'Service_distributions': [['Empirical',
                'ciw/tests/testing_parameters/sample_empirical_dist.csv']],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nem = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nem.simulation.service_times[
                Nem.id_number][0]() in set([7.0, 7.1, 7.2, 7.3, 7.7, 7.8]))
            self.assertTrue(Nem.simulation.inter_arrival_times[
                Nem.id_number][0]() in set(my_empirical_dist))

    def test_error_empirical_dist(self):
        my_empirical_dist = [8.0, 8.0, 8.0, 8.8, 8.8, 12.3]
        my_empirical_dist_E = [8.0, 8.0, 8.0, -8.8, 8.8, 12.3]
        Arrival_distributions = [['Empirical', my_empirical_dist]]
        Arrival_distributions_E = [['Empirical', my_empirical_dist_E]]
        Service_distributions = [['Empirical', my_empirical_dist]]
        Service_distributions_E = [['Empirical', my_empirical_dist_E]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions': Arrival_distributions_E,
                 'Service_distributions': Service_distributions,
                 'Number_of_servers': Number_of_servers,
                 'Transition_matrices': Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions': Arrival_distributions,
                 'Service_distributions': Service_distributions_E,
                 'Number_of_servers': Number_of_servers,
                 'Transition_matrices': Transition_matrices})

    def test_sampling_custom_dist(self):
        my_custom_dist = [[0.2, 3.7], [0.5, 3.8], [0.3, 4.1]]
        params = {
            'Arrival_distributions': [['Custom', my_custom_dist]],
            'Service_distributions': [['Custom', my_custom_dist]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nc = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(round(
            Nc.simulation.service_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(
            Nc.simulation.service_times[Nc.id_number][0](), 2), 4.1)
        self.assertEqual(round(
            Nc.simulation.service_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(
            Nc.simulation.service_times[Nc.id_number][0](), 2), 4.1)
        self.assertEqual(round(
            Nc.simulation.service_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(
            Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(
            Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 4.1)
        self.assertEqual(round(
            Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(
            Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 3.8)
        self.assertEqual(round(
            Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2), 3.7)

    @given(custs=lists(floats(min_value=0.001, max_value=10000),
                       min_size=2,
                       unique=True),
           rm=random_module())
    def test_sampling_custom_dist_hypothesis(self, custs, rm):
        cust_vals = [round(i, 10) for i in custs]
        numprobs = len(cust_vals)
        probs = [1.0/numprobs for i in range(numprobs)]
        my_custom_dist = [list(i) for i in (zip(probs, cust_vals))]
        params = {
            'Arrival_distributions': [['Custom', my_custom_dist]],
            'Service_distributions': [['Custom', my_custom_dist]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Nc = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nc.simulation.service_times[
                Nc.id_number][0]() in set(cust_vals))
            self.assertTrue(Nc.simulation.inter_arrival_times[
                Nc.id_number][0]() in set(cust_vals))

    def test_error_custom_dist(self):
        my_custom_dist = [[0.2, 3.7], [0.5, 3.8], [0.3, 4.1]]
        my_custom_dist_E = [[0.2, 3.7], [0.5, -3.8], [0.3, 4.1]]
        my_custom_dist_EE = [[0.2, 3.7], [-0.5, 3.8], [0.3, 4.1]]
        Arrival_distributions = [['Custom', my_custom_dist]]
        Arrival_distributions_E = [['Custom', my_custom_dist_E]]
        Arrival_distributions_EE = [['Custom', my_custom_dist_EE]]
        Service_distributions = [['Custom', my_custom_dist]]
        Service_distributions_E = [['Custom', my_custom_dist_E]]
        Service_distributions_EE = [['Custom', my_custom_dist_EE]]
        Number_of_servers = [1]
        Transition_matrices = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions_E,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions_EE,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_E,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})
        self.assertRaises(ValueError, ciw.create_network,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_EE,
                 'Number_of_servers':Number_of_servers,
                 'Transition_matrices':Transition_matrices})

    def test_userdefined_function_dist(self):
        params = {
            'Arrival_distributions': [
                ['UserDefined', lambda : random()],
                ['UserDefined', lambda : custom_function()]],
            'Service_distributions': [
                ['UserDefined', lambda : random()],
                ['UserDefined', lambda : custom_function()]],
            'Number_of_servers': [1, 1],
            'Transition_matrices': [[0.1, 0.1],
                                    [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)
        self.assertEqual(round(
            N1.simulation.service_times[N1.id_number][0](), 2), 0.62)
        self.assertEqual(round(
            N1.simulation.service_times[N1.id_number][0](), 2), 0.74)
        self.assertEqual(round(
            N1.simulation.service_times[N1.id_number][0](), 2), 0.80)
        self.assertEqual(round(
            N1.simulation.service_times[N1.id_number][0](), 2), 0.94)
        self.assertEqual(round(
            N1.simulation.service_times[N1.id_number][0](), 2), 0.74)
        self.assertEqual(round(
            N2.simulation.service_times[N2.id_number][0](), 2), 0.46)
        self.assertEqual(round(
            N2.simulation.service_times[N2.id_number][0](), 2), 0.06)
        self.assertEqual(round(
            N2.simulation.service_times[N2.id_number][0](), 2), 0.93)
        self.assertEqual(round(
            N2.simulation.service_times[N2.id_number][0](), 2), 0.47)
        self.assertEqual(round(
            N2.simulation.service_times[N2.id_number][0](), 2), 1.30)

        self.assertEqual(round(
            N1.simulation.inter_arrival_times[N1.id_number][0](), 2), 0.90)
        self.assertEqual(round(
            N1.simulation.inter_arrival_times[N1.id_number][0](), 2), 0.11)
        self.assertEqual(round(
            N1.simulation.inter_arrival_times[N1.id_number][0](), 2), 0.47)
        self.assertEqual(round(
            N1.simulation.inter_arrival_times[N1.id_number][0](), 2), 0.25)
        self.assertEqual(round(
            N1.simulation.inter_arrival_times[N1.id_number][0](), 2), 0.54)
        self.assertEqual(round(
            N2.simulation.inter_arrival_times[N2.id_number][0](), 2), 0.29)
        self.assertEqual(round(
            N2.simulation.inter_arrival_times[N2.id_number][0](), 2), 0.03)
        self.assertEqual(round(
            N2.simulation.inter_arrival_times[N2.id_number][0](), 2), 0.43)
        self.assertEqual(round(
            N2.simulation.inter_arrival_times[N2.id_number][0](), 2), 0.56)
        self.assertEqual(round(
            N2.simulation.inter_arrival_times[N2.id_number][0](), 2), 0.46)


    @given(const=floats(min_value = 0.02, max_value=200),
           dist=lists(floats(min_value=0.001, max_value=10000), min_size=1, max_size=20),
           rm=random_module())
    def test_userdefined_function_dist_hypothesis(self, const, dist, rm):
        my_empirical_dist = [8.0, 8.0, 8.0, 8.8, 8.8, 12.3]
        params = {
            'Arrival_distributions': [
                ['UserDefined', lambda : choice(my_empirical_dist)],
                ['UserDefined', lambda : const]],
            'Service_distributions': [
                ['UserDefined', lambda : random()],
                ['UserDefined', lambda : custom_function()]],
            'Number_of_servers': [1, 1],
            'Transition_matrices': [[0.1, 0.1],
                                    [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                N1.simulation.inter_arrival_times[N1.id_number][0]()
                in set(my_empirical_dist))
            self.assertTrue(
                N2.simulation.inter_arrival_times[N2.id_number][0]() == const)
            self.assertTrue(
                0.0 <= N1.simulation.service_times[N1.id_number][0]() <= 1.0)
            self.assertTrue(
                0.0 <= N2.simulation.service_times[N2.id_number][0]() <= 2.0)

    def test_no_arrivals_dist(self):
        params = {
            'Arrival_distributions': ['NoArrivals'],
            'Service_distributions': [['Deterministic', 6.6]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        Na = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(
            Na.simulation.inter_arrival_times[Na.id_number][0](), float('Inf'))

    def test_error_dist(self):
        params = {'Arrival_distributions': ['NoArrivals'],
                  'Service_distributions': [['dlkjdlksj', 9]],
                  'Number_of_servers': [1],
                  'Transition_matrices': [[0.1]],
                  'Simulation_time': 2222}
        self.assertRaises(ValueError, ciw.create_network, params)
        params = {'Arrival_distributions': [['skjfhkjsfhjk']],
                  'Service_distributions': [['Exponential', 9.5]],
                  'Number_of_servers': [1],
                  'Transition_matrices': [[0.1]],
                  'Simulation_time': 2222}
        self.assertRaises(ValueError, ciw.create_network, params)

    @given(positive_float=floats(min_value=0.0, max_value=100.0),
           negative_float=floats(min_value=-100.0, max_value=0.0),
           word=text(),
           rm=random_module())
    def test_check_userdef_dist(self, positive_float, negative_float, word, rm):
        assume(negative_float < 0)
        Q = ciw.Simulation(
            ciw.create_network('ciw/tests/testing_parameters/params.yml'))
        self.assertEqual(
            Q.check_userdef_dist(lambda : positive_float), positive_float)
        self.assertRaises(
            ValueError, Q.check_userdef_dist, lambda : negative_float)
        self.assertRaises(
            ValueError, Q.check_userdef_dist, lambda : word)


    def test_timedependent_function_dist(self):
        params = {
            'Arrival_distributions': [
                ['TimeDependent', lambda t : time_dependent_function_1(t)],
                ['TimeDependent', lambda t : time_dependent_function_2(t)]],
            'Service_distributions': [
                ['TimeDependent', lambda t : time_dependent_function_1(t)],
                ['TimeDependent', lambda t : time_dependent_function_2(t)]],
            'Number_of_servers': [1, 1],
            'Transition_matrices': [[0.1, 0.1],
                                    [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)
        self.assertEqual(
            N1.simulation.service_times[N1.id_number][0](3.0), 3.0)
        self.assertEqual(
            N1.simulation.service_times[N1.id_number][0](9.0), 3.0)
        self.assertEqual(
            N1.simulation.service_times[N1.id_number][0](9.0), 3.0)
        self.assertEqual(
            N1.simulation.service_times[N1.id_number][0](11.0), 5.0)
        self.assertEqual(
            N1.simulation.service_times[N1.id_number][0](11.0), 5.0)
        self.assertEqual(
            N2.simulation.service_times[N2.id_number][0](4.0), 2.0)
        self.assertEqual(
            N2.simulation.service_times[N2.id_number][0](4.0), 2.0)
        self.assertEqual(
            N2.simulation.service_times[N2.id_number][0](17.0), 8.5)
        self.assertEqual(
            N2.simulation.service_times[N2.id_number][0](22.0), 8.0)
        self.assertEqual(
            N2.simulation.service_times[N2.id_number][0](22.0), 8.0)

        self.assertEqual(N1.get_service_time(0, 3.0), 3.0)
        self.assertEqual(N1.get_service_time(0, 9.0), 3.0)
        self.assertEqual(N1.get_service_time(0, 9.0), 3.0)
        self.assertEqual(N1.get_service_time(0, 11.0), 5.0)
        self.assertEqual(N1.get_service_time(0, 11.0), 5.0)
        self.assertEqual(N2.get_service_time(0, 4.0), 2.0)
        self.assertEqual(N2.get_service_time(0, 4.0), 2.0)
        self.assertEqual(N2.get_service_time(0, 17.0), 8.5)
        self.assertEqual(N2.get_service_time(0, 22.0), 8.0)
        self.assertEqual(N2.get_service_time(0, 22.0), 8.0)

        self.assertEqual(
            N1.simulation.inter_arrival_times[N1.id_number][0](3.0), 3.0)
        self.assertEqual(
            N1.simulation.inter_arrival_times[N1.id_number][0](9.0), 3.0)
        self.assertEqual(
            N1.simulation.inter_arrival_times[N1.id_number][0](9.0), 3.0)
        self.assertEqual(
            N1.simulation.inter_arrival_times[N1.id_number][0](11.0), 5.0)
        self.assertEqual(
            N1.simulation.inter_arrival_times[N1.id_number][0](11.0), 5.0)
        self.assertEqual(
            N2.simulation.inter_arrival_times[N2.id_number][0](4.0), 2.0)
        self.assertEqual(
            N2.simulation.inter_arrival_times[N2.id_number][0](4.0), 2.0)
        self.assertEqual(
            N2.simulation.inter_arrival_times[N2.id_number][0](17.0), 8.5)
        self.assertEqual(
            N2.simulation.inter_arrival_times[N2.id_number][0](22.0), 8.0)
        self.assertEqual(
            N2.simulation.inter_arrival_times[N2.id_number][0](22.0), 8.0)

    def test_broken_timedependent_function_dist(self):
        params = {
            'Arrival_distributions': [
                ['TimeDependent', lambda t : time_dependent_function_1(t)]],
            'Service_distributions': [
                ['TimeDependent', lambda t : broken_td_func(t)]],
            'Number_of_servers': [1],
            'Transition_matrices': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params))
        N = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertRaises(ValueError, N.simulation.service_times[N.id_number][0], 3.0)
        self.assertRaises(ValueError, N.get_service_time, 0, 3.0)

    def test_timedependent_exact(self):
        params = {
            'Arrival_distributions': [
                ['TimeDependent', lambda t : time_dependent_function_1(t)],
                ['TimeDependent', lambda t : time_dependent_function_2(t)]],
            'Service_distributions': [
                ['TimeDependent', lambda t : time_dependent_function_1(t)],
                ['TimeDependent', lambda t : time_dependent_function_2(t)]],
            'Number_of_servers': [1, 1],
            'Transition_matrices': [[0.1, 0.1],
                                    [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(params), exact=26)
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)
        self.assertEqual(N1.get_service_time(0, 3.0), 3.0)
        self.assertEqual(N1.get_service_time(0, 9.0), 3.0)
        self.assertEqual(N1.get_service_time(0, 9.0), 3.0)
        self.assertEqual(N1.get_service_time(0, 11.0), 5.0)
        self.assertEqual(N1.get_service_time(0, 11.0), 5.0)
        self.assertEqual(N2.get_service_time(0, 4.0), 2.0)
        self.assertEqual(N2.get_service_time(0, 4.0), 2.0)
        self.assertEqual(N2.get_service_time(0, 17.0), 8.5)
        self.assertEqual(N2.get_service_time(0, 22.0), 8.0)
        self.assertEqual(N2.get_service_time(0, 22.0), 8.0)
