import unittest
import ciw
from random import random, choice
from hypothesis import given
from hypothesis.strategies import (floats, integers, lists,
    random_module, assume, text)
import os
import copy

class CustomDist(ciw.dists.Distribution):
    """
    A custom distribution to test user defined functionality.
    """
    def sample(self, t=None):
        val = random()
        if int(str(val*10)[0]) % 2 == 0:
            return 2 * val
        return val / 2.0

def custom_function():
    """
    Custom function to test user defined function functionality.
    """
    val = random()
    if int(str(val*10)[0]) % 2 == 0:
        return 2 * val
    return val / 2.0

class TimeDependentDist1(ciw.dists.Distribution):
    """
    A customer time-dependent distribution to test time-dependent functionality.
    """
    def sample(self, t):
        if t < 10.0:
            return 3.0
        return 5.0

def time_dependent_function_1(current_time):
    if current_time < 10.0:
        return 3.0
    return 5.0

class TimeDependentDist2(ciw.dists.Distribution):
    """
    A customer time-dependent distribution to test time-dependent functionality.
    """
    def sample(self, t):
        if t < 20.0:
            return t / 2.0
        return 8.0

def time_dependent_function_2(current_time):
    if current_time < 20.0:
        return current_time / 2.0
    return 8.0

class BrokenDist(ciw.dists.Distribution):
    """
    Broken distribution that should raise an error.
    """
    def sample(self, t=None):
        return -4.0

def broken_td_func(current_time):
    return -4.0

class TestSampling(unittest.TestCase):
    def test_distribution_parent_is_useless(self):
        D = ciw.dists.Distribution()
        self.assertRaises(ValueError, D._sample)

    def test_uniform_dist_object(self):
        U = ciw.dists.Uniform(2.2, 3.3)
        ciw.seed(5)
        samples = [round(U._sample(), 2) for _ in range(10)]
        expected = [2.89, 3.02, 3.07, 3.24, 3.01, 3.21, 2.23, 2.71, 3.24, 2.91]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Uniform, -3.1, 1.2)
        self.assertRaises(ValueError, ciw.dists.Uniform, 3.1, 1.2)

    def test_sampling_uniform_dist(self):
        params = {
            'Arrival_distributions': [['Uniform', 2.2, 3.3]],
            'Service_distributions': [['Uniform', 2.2, 3.3]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nu = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nu.simulation.service_times[Nu.id_number][0](), 2) for _ in range(5)]
        expected = [2.89, 3.02, 3.07, 3.24, 3.01]
        self.assertEqual(samples, expected)

        samples = [round(Nu.simulation.inter_arrival_times[Nu.id_number][0](), 2) for _ in range(5)]
        expected = [3.21, 2.23, 2.71, 3.24, 2.91]
        self.assertEqual(samples, expected)


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
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
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
        Routing = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions_E,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions_EE,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_E,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_EE,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})

    def test_deterministic_dist_object(self):
        D = ciw.dists.Deterministic(4.4)
        ciw.seed(5)
        samples = [round(D._sample(), 2) for _ in range(10)]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Deterministic, -4.4)

    def test_sampling_deterministic_dist(self):
        params = {
            'Arrival_distributions': [['Deterministic', 4.4]],
            'Service_distributions': [['Deterministic', 4.4]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nd = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nd.simulation.service_times[Nd.id_number][0](), 2) for _ in range(5)]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)

        samples = [round(Nd.simulation.inter_arrival_times[Nd.id_number][0](), 2) for _ in range(5)]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)


    @given(d=floats(min_value=0.0, max_value=10000),
           rm=random_module())
    def test_sampling_deterministic_dist_hypothesis(self, d, rm):
        params = {
            'Arrival_distributions': [['Deterministic', d]],
            'Service_distributions': [['Deterministic', d]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
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
        Routing = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions_E,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                 {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_E,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})

    def test_triangular_dist_object(self):
        Tr = ciw.dists.Triangular(1.1, 1.5, 6.6)
        ciw.seed(5)
        samples = [round(Tr._sample(), 2) for _ in range(10)]
        expected = [3.35, 3.91, 4.20, 5.33, 3.90, 5.12, 1.35, 2.73, 5.34, 3.46]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Triangular, -4.4, -0.3, 1.4)
        self.assertRaises(ValueError, ciw.dists.Triangular, 1.3, 2.5, 1.0)

    def test_sampling_triangular_dist(self):
        params = {
            'Arrival_distributions': [['Triangular', 1.1, 6.6, 1.5]],
            'Service_distributions': [['Triangular', 1.1, 6.6, 1.5]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nt = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nt.simulation.service_times[Nt.id_number][0](), 2) for _ in range(5)]
        expected = [3.35, 3.91, 4.20, 5.33, 3.90]
        self.assertEqual(samples, expected)

        samples = [round(Nt.simulation.inter_arrival_times[Nt.id_number][0](), 2) for _ in range(5)]
        expected = [5.12, 1.35, 2.73, 5.34, 3.46]
        self.assertEqual(samples, expected)


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
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
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
        Routing = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions_E,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions_EE,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_E,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_EE,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})

    def test_exponential_dist_object(self):
        E = ciw.dists.Exponential(4.4)
        ciw.seed(5)
        samples = [round(E._sample(), 2) for _ in range(10)]
        expected = [0.22, 0.31, 0.36, 0.65, 0.31, 0.58, 0.01, 0.14, 0.65, 0.24]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Exponential, -4.4)
        self.assertRaises(ValueError, ciw.dists.Exponential, 0.0)

    def test_sampling_exponential_dist(self):
        params = {
            'Arrival_distributions': [['Exponential', 4.4]],
            'Service_distributions': [['Exponential', 4.4]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ne = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Ne.simulation.service_times[Ne.id_number][0](), 2) for _ in range(5)]
        expected = [0.22, 0.31, 0.36, 0.65, 0.31]
        self.assertEqual(samples, expected)

        samples = [round(Ne.simulation.inter_arrival_times[Ne.id_number][0](), 2) for _ in range(5)]
        expected = [0.58, 0.01, 0.14, 0.65, 0.24]
        self.assertEqual(samples, expected)


    @given(e=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_exponential_dist_hypothesis(self, e, rm):
        params = {
            'Arrival_distributions': [['Exponential', e]],
            'Service_distributions': [['Exponential', e]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ne = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Ne.simulation.service_times[Ne.id_number][0]() >= 0.0)
            self.assertTrue(
                Ne.simulation.inter_arrival_times[Ne.id_number][0]() >= 0.0)

    def test_gamma_dist_object(self):
        G = ciw.dists.Gamma(0.6, 1.2)
        ciw.seed(5)
        samples = [round(G._sample(), 2) for _ in range(10)]
        expected = [0.0, 2.59, 1.92, 0.47, 0.61, 0.00, 1.07, 1.15, 0.75, 0.00]
        self.assertEqual(samples, expected)

    def test_sampling_gamma_dist(self):
        params = {
            'Arrival_distributions': [['Gamma', 0.6, 1.2]],
            'Service_distributions': [['Gamma', 0.6, 1.2]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ng = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Ng.simulation.service_times[Ng.id_number][0](), 2) for _ in range(5)]
        expected = [0.0, 2.59, 1.92, 0.47, 0.61]
        self.assertEqual(samples, expected)

        samples = [round(Ng.simulation.inter_arrival_times[Ng.id_number][0](), 2) for _ in range(5)]
        expected = [0.00, 1.07, 1.15, 0.75, 0.00]
        self.assertEqual(samples, expected)


    @given(ga=floats(min_value=0.001, max_value=10000),
           gb=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_gamma_dist_hypothesis(self, ga, gb, rm):
        params = {
            'Arrival_distributions': [['Gamma', ga, gb]],
            'Service_distributions': [['Gamma', ga, gb]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ng = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Ng.simulation.service_times[Ng.id_number][0]() >= 0.0)
            self.assertTrue(
                Ng.simulation.inter_arrival_times[Ng.id_number][0]() >= 0.0)

    def test_lognormal_dist_object(self):
        Ln = ciw.dists.Lognormal(0.8, 0.2)
        ciw.seed(5)
        samples = [round(Ln._sample(), 2) for _ in range(10)]
        expected = [2.62, 1.64, 2.19, 2.31, 2.48, 2.51, 2.33, 1.96, 2.32, 2.70]
        self.assertEqual(samples, expected)

    def test_sampling_lognormal_dist(self):
        params = {
            'Arrival_distributions': [['Lognormal', 0.8, 0.2]],
            'Service_distributions': [['Lognormal', 0.8, 0.2]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nl = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nl.simulation.service_times[Nl.id_number][0](), 2) for _ in range(5)]
        expected = [2.62, 1.64, 2.19, 2.31, 2.48]
        self.assertEqual(samples, expected)

        samples = [round(Nl.simulation.inter_arrival_times[Nl.id_number][0](), 2) for _ in range(5)]
        expected = [2.51, 2.33, 1.96, 2.32, 2.70]
        self.assertEqual(samples, expected)


    @given(lm=floats(min_value=-200, max_value=200),
           lsd=floats(min_value=0.001, max_value=80),
           rm=random_module())
    def test_sampling_lognormal_dist_hypothesis(self, lm, lsd, rm):
        params = {
            'Arrival_distributions': [['Lognormal', lm, lsd]],
            'Service_distributions': [['Lognormal', lm, lsd]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nl = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nl.simulation.service_times[Nl.id_number][0]() >= 0.0)
            self.assertTrue(
                Nl.simulation.inter_arrival_times[Nl.id_number][0]() >= 0.0)

    def test_weibull_dist_object(self):
        W = ciw.dists.Weibull(0.9, 0.8)
        ciw.seed(5)
        samples = [round(W._sample(), 2) for _ in range(10)]
        expected = [0.87, 1.31, 1.60, 3.34, 1.31, 2.91, 0.01, 0.50, 3.36, 0.95]
        self.assertEqual(samples, expected)

    def test_sampling_weibull_dist(self):
        params = {
            'Arrival_distributions': [['Weibull', 0.9, 0.8]],
            'Service_distributions': [['Weibull', 0.9, 0.8]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nw = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nw.simulation.service_times[Nw.id_number][0](), 2) for _ in range(5)]
        expected = [0.87, 1.31, 1.60, 3.34, 1.31]
        self.assertEqual(samples, expected)

        samples = [round(Nw.simulation.inter_arrival_times[Nw.id_number][0](), 2) for _ in range(5)]
        expected = [2.91, 0.01, 0.50, 3.36, 0.95]
        self.assertEqual(samples, expected)


    @given(wa=floats(min_value=0.01, max_value=200),
           wb=floats(min_value=0.01, max_value=200),
           rm=random_module())
    def test_sampling_weibull_dist_hypothesis(self, wa, wb, rm):
        params = {
            'Arrival_distributions': [['Weibull', wa, wb]],
            'Service_distributions': [['Weibull', wa, wb]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nw = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nw.simulation.service_times[Nw.id_number][0]() >= 0.0)
            self.assertTrue(
                Nw.simulation.inter_arrival_times[Nw.id_number][0]() >= 0.0)

    def test_normal_dist_object(self):
        N = ciw.dists.Normal(0.5, 0.1)
        ciw.seed(5)
        samples = [round(N._sample(), 2) for _ in range(10)]
        expected = [0.58, 0.35, 0.49, 0.52, 0.55, 0.56, 0.52, 0.44, 0.52, 0.60]
        self.assertEqual(samples, expected)

    def test_sampling_normal_dist(self):
        params = {
            'Arrival_distributions': [['Normal', 0.5, 0.1]],
            'Service_distributions': [['Normal', 0.5, 0.1]],
            'Number_of_servers': [1],
            'Routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nn.simulation.service_times[Nn.id_number][0](), 2) for _ in range(5)]
        expected = [0.58, 0.35, 0.49, 0.52, 0.55]
        self.assertEqual(samples, expected)

        samples = [round(Nn.simulation.inter_arrival_times[Nn.id_number][0](), 2) for _ in range(5)]
        expected = [0.56, 0.52, 0.44, 0.52, 0.60]
        self.assertEqual(samples, expected)


    @given(nm=floats(min_value=0.01, max_value=20),
           ns=floats(min_value=0.0001, max_value=5),
           rm=random_module())
    def test_sampling_normal_dist_hypothesis(self, nm, ns, rm):
        params = {
            'Arrival_distributions': [['Normal', nm, ns]],
            'Service_distributions': [['Normal', nm, ns]],
            'Number_of_servers': [1],
            'Routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nw = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nw.simulation.service_times[Nw.id_number][0]() >= 0.0)
            self.assertTrue(
                Nw.simulation.inter_arrival_times[Nw.id_number][0]() >= 0.0)

    def test_empirical_dist_object(self):
        Em = ciw.dists.Empirical([8.0, 8.0, 8.0, 8.8, 8.8, 12.3])
        ciw.seed(5)
        samples = [round(Em._sample(), 2) for _ in range(10)]
        expected = [8.8, 8.8, 8.8, 12.3, 8.8, 12.3, 8.0, 8.0, 12.3, 8.8]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Empirical, [-4.4, -0.3, 1.4, 1.4])

    def test_sampling_empirical_dist(self):
        my_empirical_dist = [8.0, 8.0, 8.0, 8.8, 8.8, 12.3]
        params = {
            'Arrival_distributions': [['Empirical',
                'ciw/tests/testing_parameters/sample_empirical_dist.csv']],
            'Service_distributions': [['Empirical', my_empirical_dist]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nem = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nem.simulation.service_times[Nem.id_number][0](), 2) for _ in range(5)]
        expected = [8.8, 8.8, 8.8, 12.3, 8.8]
        self.assertEqual(samples, expected)

        samples = [round(Nem.simulation.inter_arrival_times[Nem.id_number][0](), 2) for _ in range(5)]
        expected = [7.3, 7.0, 7.7, 7.3, 7.1]
        self.assertEqual(samples, expected)


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
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
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
        Routing = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions': Arrival_distributions_E,
                 'Service_distributions': Service_distributions,
                 'Number_of_servers': Number_of_servers,
                 'Routing': Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions': Arrival_distributions,
                 'Service_distributions': Service_distributions_E,
                 'Number_of_servers': Number_of_servers,
                 'Routing': Routing})

    def test_pmf_object(self):
        Pmf = ciw.dists.Pmf([3.7, 3.8, 4.1], [0.2, 0.5, 0.3])
        ciw.seed(5)
        samples = [round(Pmf._sample(), 2) for _ in range(10)]
        expected = [3.8, 4.1, 4.1, 4.1, 4.1, 4.1, 3.7, 3.8, 4.1, 3.8]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Pmf, [2.7, -3.8, 4.1], [0.2, 0.5, 0.3])
        self.assertRaises(ValueError, ciw.dists.Pmf, [2.7, 3.8, 4.1], [0.2, -0.5, 0.3])
        self.assertRaises(ValueError, ciw.dists.Pmf, [2.7, 3.8, 4.1], [0.2, 0.5, 1.3])
        self.assertRaises(ValueError, ciw.dists.Pmf, [2.7, 3.8, 4.1], [0.4, 0.5, 0.3])

    def test_sampling_custom_dist(self):
        my_custom_dist_values =  [3.7, 3.8, 4.1]
        my_custom_dist_probs = [0.2, 0.5, 0.3]
        params = {
            'Arrival_distributions': [['Custom', my_custom_dist_values, my_custom_dist_probs]],
            'Service_distributions': [['Custom', my_custom_dist_values, my_custom_dist_probs]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nc = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nc.simulation.service_times[Nc.id_number][0](), 2) for _ in range(5)]
        expected = [3.8, 4.1, 4.1, 4.1, 4.1]
        self.assertEqual(samples, expected)

        samples = [round(Nc.simulation.inter_arrival_times[Nc.id_number][0](), 2) for _ in range(5)]
        expected = [4.1, 3.7, 3.8, 4.1, 3.8]
        self.assertEqual(samples, expected)


    @given(custs=lists(floats(min_value=0.001, max_value=10000),
                       min_size=2,
                       unique=True),
           rm=random_module())
    def test_sampling_custom_dist_hypothesis(self, custs, rm):
        cust_vals = [round(i, 10) for i in custs]
        numprobs = len(cust_vals)
        probs = [1.0/numprobs for i in range(numprobs)]
        params = {
            'Arrival_distributions': [['Custom', cust_vals, probs]],
            'Service_distributions': [['Custom', cust_vals, probs]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nc = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nc.simulation.service_times[
                Nc.id_number][0]() in set(cust_vals))
            self.assertTrue(Nc.simulation.inter_arrival_times[
                Nc.id_number][0]() in set(cust_vals))

    def test_error_custom_dist(self):
        my_custom_dist_vals = [3.7, 3.8, 4.1]
        my_custom_dist_vals_E = [3.7, -3.8, 4.1]

        my_custom_dist_probs = [0.2, 0.5, 0.3]
        my_custom_dist_probs_E = [0.2, -0.5, 0.3]

        Arrival_distributions = [['Custom', my_custom_dist_vals, my_custom_dist_probs]]
        Arrival_distributions_E = [['Custom', my_custom_dist_vals_E, my_custom_dist_probs]]
        Arrival_distributions_EE = [['Custom', my_custom_dist_vals, my_custom_dist_probs_E]]
        Service_distributions = [['Custom', my_custom_dist_vals, my_custom_dist_probs]]
        Service_distributions_E = [['Custom', my_custom_dist_vals_E, my_custom_dist_probs]]
        Service_distributions_EE = [['Custom', my_custom_dist_vals, my_custom_dist_probs_E]]
        Number_of_servers = [1]
        Routing = [[0.1]]
        Simulation_time = 2222
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions_E,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions_EE,
                 'Service_distributions':Service_distributions,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_E,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})
        self.assertRaises(ValueError, ciw.create_network_from_dictionary,
                {'Arrival_distributions':Arrival_distributions,
                 'Service_distributions':Service_distributions_EE,
                 'Number_of_servers':Number_of_servers,
                 'Routing':Routing})

    def test_custom_dist_object(self):
        CD = CustomDist()
        ciw.seed(5)
        samples = [round(CD._sample(), 2) for _ in range(10)]
        expected = [1.25, 0.37, 0.4, 0.47, 0.37, 0.46, 0.06, 0.93, 0.47, 1.3]
        self.assertEqual(samples, expected)

    def test_userdefined_function_dist(self):
        params = {
            'Arrival_distributions': [
                ['UserDefined', lambda : random()],
                ['UserDefined', lambda : custom_function()]],
            'Service_distributions': [
                ['UserDefined', lambda : random()],
                ['UserDefined', lambda : custom_function()]],
            'Number_of_servers': [1, 1],
            'Routing': [[0.1, 0.1],
                                    [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)

        samples = [round(N1.simulation.service_times[N1.id_number][0](), 2) for _ in range(5)]
        expected = [0.62, 0.74, 0.80, 0.94, 0.74]
        self.assertEqual(samples, expected)

        samples = [round(N2.simulation.service_times[N2.id_number][0](), 2) for _ in range(5)]
        expected = [0.46, 0.06, 0.93, 0.47, 1.30]
        self.assertEqual(samples, expected)

        samples = [round(N1.simulation.inter_arrival_times[N1.id_number][0](), 2) for _ in range(5)]
        expected = [0.90, 0.11, 0.47, 0.25, 0.54]
        self.assertEqual(samples, expected)

        samples = [round(N2.simulation.inter_arrival_times[N2.id_number][0](), 2) for _ in range(5)]
        expected = [0.29, 0.03, 0.43, 0.56, 0.46]
        self.assertEqual(samples, expected)



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
            'Routing': [[0.1, 0.1],
                                    [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
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

    def test_noarrivals_object(self):
        Na = ciw.dists.NoArrivals()
        ciw.seed(5)
        samples = [Na._sample() for _ in range(10)]
        expected = [float('Inf'), float('Inf'), float('Inf'), float('Inf'), float('Inf'), float('Inf'), float('Inf'), float('Inf'), float('Inf'), float('Inf')]
        self.assertEqual(samples, expected)

    def test_no_arrivals_dist(self):
        params = {
            'Arrival_distributions': ['NoArrivals'],
            'Service_distributions': [['Deterministic', 6.6]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Na = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(
            Na.simulation.inter_arrival_times[Na.id_number][0](), float('Inf'))

    def test_error_dist(self):
        params = {'Arrival_distributions': ['NoArrivals'],
                  'Service_distributions': [['dlkjdlksj', 9]],
                  'Number_of_servers': [1],
                  'Routing': [[0.1]],
                  'Simulation_time': 2222}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params)
        params = {'Arrival_distributions': [['skjfhkjsfhjk']],
                  'Service_distributions': [['Exponential', 9.5]],
                  'Number_of_servers': [1],
                  'Routing': [[0.1]],
                  'Simulation_time': 2222}
        self.assertRaises(ValueError, ciw.create_network_from_dictionary, params)

    @given(positive_float=floats(min_value=0.0, max_value=100.0),
           negative_float=floats(min_value=-100.0, max_value=0.0),
           word=text(),
           rm=random_module())
    def test_check_userdef_dist(self, positive_float, negative_float, word, rm):
        assume(negative_float < 0)
        Q = ciw.Simulation(
            ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        self.assertEqual(
            Q.check_userdef_dist(lambda : positive_float), positive_float)
        self.assertRaises(
            ValueError, Q.check_userdef_dist, lambda : negative_float)
        self.assertRaises(
            ValueError, Q.check_userdef_dist, lambda : word)

    def test_timedependent_dist_object(self):
        TD1 = TimeDependentDist1()
        ciw.seed(5)
        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            samples.append(round(TD1.sample(t), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        TD2 = TimeDependentDist2()
        ciw.seed(5)
        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            samples.append(round(TD2.sample(t), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

    def test_timedependent_function_dist(self):
        params = {
            'Arrival_distributions': [
                ['TimeDependent', time_dependent_function_1],
                ['TimeDependent', time_dependent_function_2]],
            'Service_distributions': [
                ['TimeDependent', time_dependent_function_1],
                ['TimeDependent', time_dependent_function_2]],
            'Number_of_servers': [1, 1],
            'Routing': [[0.1, 0.1],
                                    [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            samples.append(round(N1.simulation.service_times[N1.id_number][0](t), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            samples.append(round(N2.simulation.service_times[N2.id_number][0](t), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            Q.current_time = t
            samples.append(round(N1.get_service_time(0), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            Q.current_time = t
            samples.append(round(N2.get_service_time(0), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            samples.append(round(N1.simulation.inter_arrival_times[N1.id_number][0](t), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            samples.append(round(N2.simulation.inter_arrival_times[N2.id_number][0](t), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

    def test_broken_dist_object(self):
        B = BrokenDist()
        ciw.seed(5)
        self.assertRaises(ValueError, B._sample)

    def test_broken_timedependent_function_dist(self):
        params = {
            'Arrival_distributions': [
                ['TimeDependent', time_dependent_function_1]],
            'Service_distributions': [
                ['TimeDependent', broken_td_func]],
            'Number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        N = Q.transitive_nodes[0]
        ciw.seed(5)
        Q.current_time = 3.0
        self.assertRaises(ValueError, N.simulation.service_times[N.id_number][0], 3.0)
        self.assertRaises(ValueError, N.get_service_time, 0)

    def test_timedependent_exact(self):
        params = {
            'Arrival_distributions': [
                ['TimeDependent', time_dependent_function_1],
                ['TimeDependent', time_dependent_function_2]],
            'Service_distributions': [
                ['TimeDependent', time_dependent_function_1],
                ['TimeDependent', time_dependent_function_2]],
            'Number_of_servers': [1, 1],
            'Routing': [[0.1, 0.1],
                                    [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params), exact=26)
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            Q.current_time = t
            samples.append(round(N1.get_service_time(0), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            Q.current_time = t
            samples.append(round(N2.get_service_time(0), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

    def test_sequential_dist_object(self):
        S = ciw.dists.Sequential([0.9, 0.7, 0.5, 0.3, 0.1])
        ciw.seed(5)
        samples = [round(S._sample(), 2) for _ in range(7)]
        expected = [0.9, 0.7, 0.5, 0.3, 0.1, 0.9, 0.7]
        self.assertEqual(samples, expected)

        S = ciw.dists.Sequential([0.2, 0.4, 0.6, 0.8])
        ciw.seed(5)
        samples = [S._sample() for _ in range(7)]
        expected = [0.2, 0.4, 0.6, 0.8, 0.2, 0.4, 0.6]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Sequential, [-4.4, -0.3, 1.4, 1.4])

    def test_sampling_sequential_dist(self):
        params = {
            'Arrival_distributions': [['Sequential', [0.2, 0.4, 0.6, 0.8]]],
            'Service_distributions': [['Sequential', [0.9, 0.7, 0.5, 0.3, 0.1]]],
            'Number_of_servers': [1],
            'Routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ns = Q.transitive_nodes[0]

        samples = [round(Ns.simulation.service_times[Ns.id_number][0](), 2) for _ in range(7)]
        expected = [0.9, 0.7, 0.5, 0.3, 0.1, 0.9, 0.7]
        self.assertEqual(samples, expected)

        # First arrival will be offset by 1, as first customer's inter-arrival
        # time has already been sampled by the arrival node
        samples = [round(Ns.simulation.inter_arrival_times[Ns.id_number][0](), 2) for _ in range(6)]
        expected = [0.4, 0.6, 0.8, 0.2, 0.4, 0.6]
        self.assertEqual(samples, expected)


    @given(dist1=lists(floats(min_value=0.001, max_value=10000),
                       min_size=1,
                       max_size=20),
           dist2=lists(floats(min_value=0.001, max_value=10000),
                       min_size=1,
                       max_size=20))
    def test_sampling_sequential_dist_hypothesis(self, dist1, dist2):
        my_sequential_dist_1 = dist1
        my_sequential_dist_2 = dist2
        params = {
            'Arrival_distributions': [['Sequential', my_sequential_dist_1]],
            'Service_distributions': [['Sequential', my_sequential_dist_2]],
            'Number_of_servers': [1],
            'Routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ns = Q.transitive_nodes[0]

        len1 = len(my_sequential_dist_1)
        len2 = len(my_sequential_dist_2)

        expected_inter_arrival_times = 3*my_sequential_dist_1 + my_sequential_dist_1[:1]
        expected_service_times = 3*my_sequential_dist_2

        inter_arrivals = [Ns.simulation.inter_arrival_times[Ns.id_number][0]() for _ in range(3*len1)]
        services = [Ns.simulation.service_times[Ns.id_number][0]() for _ in range(3*len2)]
        self.assertEqual(inter_arrivals, expected_inter_arrival_times[1:])
        self.assertEqual(services, expected_service_times)
