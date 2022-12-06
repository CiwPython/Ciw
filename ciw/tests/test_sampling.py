import unittest
import ciw
from csv import reader
from random import random, choice
from hypothesis import given
from hypothesis.strategies import (floats, integers, lists,
    random_module, text)
import os
import copy

def import_empirical(dist_file):
    """
    Imports an empirical distribution from a .csv file
    """
    root = os.getcwd()
    file_name = root + '/' + dist_file
    empirical_file = open(file_name, 'r')
    rdr = reader(empirical_file)
    empirical_dist = [[float(x) for x in row] for row in rdr][0]
    empirical_file.close()
    return empirical_dist


class CustomDist(ciw.dists.Distribution):
    """
    A custom distribution to test user defined functionality.
    """
    def sample(self, t=None, ind=None):
        val = random()
        if int(str(val*10)[0]) % 2 == 0:
            return 2 * val
        return val / 2.0

class TimeDependentDist1(ciw.dists.Distribution):
    """
    A customer time-dependent distribution to test time-dependent functionality.
    """
    def sample(self, t, ind=None):
        if t < 10.0:
            return 3.0
        return 5.0

class TimeDependentDist2(ciw.dists.Distribution):
    """
    A customer time-dependent distribution to test time-dependent functionality.
    """
    def sample(self, t, ind=None):
        if t < 20.0:
            return t / 2.0
        return 8.0

class BrokenDist(ciw.dists.Distribution):
    """
    Broken distribution that should raise an error.
    """
    def sample(self, t=None, ind=None):
        return -4.0

class StateDependent(ciw.dists.Distribution):
    """
    Samples different values based on simulation state:
    n = number of individuals at the node (not including self)
      - 0.2 if n = 0
      - 0.15 if n = 1
      - 0.1 if n = 2
      - 0.05 if n = 3
      - 0.0 otherwise
    """
    def sample(self, t=None, ind=None):
        n = ind.queue_size_at_arrival
        return max((-0.05*n) + 0.2, 0)


class TestSampling(unittest.TestCase):
    def test_dists_repr(self):
        Di = ciw.dists.Distribution()
        Un = ciw.dists.Uniform(3.4, 6.7)
        Dt = ciw.dists.Deterministic(1.1)
        Tr = ciw.dists.Triangular(1.1, 2.2, 3.3)
        Ex = ciw.dists.Exponential(0.4)
        Ga = ciw.dists.Gamma(2.1, 4.1)
        No = ciw.dists.Normal(5.5, 0.6)
        Ln = ciw.dists.Lognormal(5.5, 3.6)
        Wb = ciw.dists.Weibull(8.8, 9.9)
        Em = ciw.dists.Empirical([3.3, 3.3, 4.4, 3.3, 4.4])
        Sq = ciw.dists.Sequential([3.3, 3.3, 4.4, 3.3, 4.4])
        Pf = ciw.dists.Pmf([1.1, 2.2, 3.3], [0.3, 0.2, 0.5])
        Na = ciw.dists.NoArrivals()
        Ph = ciw.dists.PhaseType([1, 0, 0], [[-3, 2, 1], [1, -5, 4], [0, 0, 0]])
        Er = ciw.dists.Erlang(4.5, 8)
        Hx = ciw.dists.HyperExponential([4, 7, 2], [0.3, 0.1, 0.6])
        He = ciw.dists.HyperErlang([4, 7, 2], [0.3, 0.1, 0.6], [2, 2, 7])
        Cx = ciw.dists.Coxian([4, 7, 2], [0.3, 0.2, 1.0])
        Pi = ciw.dists.PoissonIntervals(rates=[5, 1.5, 3], endpoints=[3.2, 7.9, 10], max_sample_date=15)
        self.assertEqual(str(Di), 'Distribution')
        self.assertEqual(str(Un), 'Uniform: 3.4, 6.7')
        self.assertEqual(str(Dt), 'Deterministic: 1.1')
        self.assertEqual(str(Tr), 'Triangular: 1.1, 2.2, 3.3')
        self.assertEqual(str(Ex), 'Exponential: 0.4')
        self.assertEqual(str(Ga), 'Gamma: 2.1, 4.1')
        self.assertEqual(str(No), 'Normal: 5.5, 0.6')
        self.assertEqual(str(Ln), 'Lognormal: 5.5, 3.6')
        self.assertEqual(str(Wb), 'Weibull: 8.8, 9.9')
        self.assertEqual(str(Em), 'Empirical')
        self.assertEqual(str(Sq), 'Sequential')
        self.assertEqual(str(Pf), 'Pmf')
        self.assertEqual(str(Na), 'NoArrivals')
        self.assertEqual(str(Ph), 'PhaseType')
        self.assertEqual(str(Er), 'Erlang: 4.5, 8')
        self.assertEqual(str(Hx), 'HyperExponential')
        self.assertEqual(str(He), 'HyperErlang')
        self.assertEqual(str(Cx), 'Coxian')
        self.assertEqual(str(Pi), 'PoissonIntervals')

    def test_distribution_parent_is_useless(self):
        D = ciw.dists.Distribution()
        self.assertEqual(str(D), 'Distribution')
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
            'arrival_distributions': [ciw.dists.Uniform(2.2, 3.3)],
            'service_distributions': [ciw.dists.Uniform(2.2, 3.3)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nu = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nu.simulation.service_times[Nu.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [2.89, 3.02, 3.07, 3.24, 3.01]
        self.assertEqual(samples, expected)

        samples = [round(Nu.simulation.inter_arrival_times[Nu.id_number][0]._sample(), 2) for _ in range(5)]
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
            'arrival_distributions': [ciw.dists.Uniform(ul, uh)],
            'service_distributions': [ciw.dists.Uniform(ul, uh)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nu = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                ul <= Nu.simulation.service_times[Nu.id_number][0]._sample() <= uh)
            self.assertTrue(
                ul <= Nu.simulation.inter_arrival_times[Nu.id_number][0]._sample() <= uh)

    def test_deterministic_dist_object(self):
        D = ciw.dists.Deterministic(4.4)
        ciw.seed(5)
        samples = [round(D._sample(), 2) for _ in range(10)]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Deterministic, -4.4)

    def test_sampling_deterministic_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.Deterministic(4.4)],
            'service_distributions': [ciw.dists.Deterministic(4.4)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nd = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nd.simulation.service_times[Nd.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)

        samples = [round(Nd.simulation.inter_arrival_times[Nd.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)


    @given(d=floats(min_value=0.0, max_value=10000),
           rm=random_module())
    def test_sampling_deterministic_dist_hypothesis(self, d, rm):
        params = {
            'arrival_distributions': [ciw.dists.Deterministic(d)],
            'service_distributions': [ciw.dists.Deterministic(d)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nd = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertEqual(
                Nd.simulation.service_times[Nd.id_number][0]._sample(), d)
            self.assertEqual(
                Nd.simulation.inter_arrival_times[Nd.id_number][0]._sample(), d)

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
            'arrival_distributions': [ciw.dists.Triangular(1.1, 1.5, 6.6)],
            'service_distributions': [ciw.dists.Triangular(1.1, 1.5, 6.6)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nt = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nt.simulation.service_times[Nt.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [3.35, 3.91, 4.20, 5.33, 3.90]
        self.assertEqual(samples, expected)

        samples = [round(Nt.simulation.inter_arrival_times[Nt.id_number][0]._sample(), 2) for _ in range(5)]
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
            'arrival_distributions': [ciw.dists.Triangular(tl, tm, th)],
            'service_distributions': [ciw.dists.Triangular(tl, tm, th)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nt = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                tl <= Nt.simulation.service_times[Nt.id_number][0]._sample() <= th)
            self.assertTrue(
                tl <= Nt.simulation.inter_arrival_times[Nt.id_number][0]._sample() <= th)

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
            'arrival_distributions': [ciw.dists.Exponential(4.4)],
            'service_distributions': [ciw.dists.Exponential(4.4)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ne = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Ne.simulation.service_times[Ne.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.22, 0.31, 0.36, 0.65, 0.31]
        self.assertEqual(samples, expected)

        samples = [round(Ne.simulation.inter_arrival_times[Ne.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.58, 0.01, 0.14, 0.65, 0.24]
        self.assertEqual(samples, expected)


    @given(e=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_exponential_dist_hypothesis(self, e, rm):
        params = {
            'arrival_distributions': [ciw.dists.Exponential(e)],
            'service_distributions': [ciw.dists.Exponential(e)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ne = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Ne.simulation.service_times[Ne.id_number][0]._sample() >= 0.0)
            self.assertTrue(
                Ne.simulation.inter_arrival_times[Ne.id_number][0]._sample() >= 0.0)

    def test_gamma_dist_object(self):
        G = ciw.dists.Gamma(0.6, 1.2)
        ciw.seed(5)
        samples = [round(G._sample(), 2) for _ in range(10)]
        expected = [0.0, 2.59, 1.92, 0.47, 0.61, 0.00, 1.07, 1.15, 0.75, 0.00]
        self.assertEqual(samples, expected)

    def test_sampling_gamma_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.Gamma(0.6, 1.2)],
            'service_distributions': [ciw.dists.Gamma(0.6, 1.2)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ng = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Ng.simulation.service_times[Ng.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.0, 2.59, 1.92, 0.47, 0.61]
        self.assertEqual(samples, expected)

        samples = [round(Ng.simulation.inter_arrival_times[Ng.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.00, 1.07, 1.15, 0.75, 0.00]
        self.assertEqual(samples, expected)


    @given(ga=floats(min_value=0.001, max_value=10000),
           gb=floats(min_value=0.001, max_value=10000),
           rm=random_module())
    def test_sampling_gamma_dist_hypothesis(self, ga, gb, rm):
        params = {
            'arrival_distributions': [ciw.dists.Gamma(ga, gb)],
            'service_distributions': [ciw.dists.Gamma(ga, gb)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ng = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Ng.simulation.service_times[Ng.id_number][0]._sample() >= 0.0)
            self.assertTrue(
                Ng.simulation.inter_arrival_times[Ng.id_number][0]._sample() >= 0.0)

    def test_lognormal_dist_object(self):
        Ln = ciw.dists.Lognormal(0.8, 0.2)
        ciw.seed(5)
        samples = [round(Ln._sample(), 2) for _ in range(10)]
        expected = [2.62, 1.64, 2.19, 2.31, 2.48, 2.51, 2.33, 1.96, 2.32, 2.70]
        self.assertEqual(samples, expected)

    def test_sampling_lognormal_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.Lognormal(0.8, 0.2)],
            'service_distributions': [ciw.dists.Lognormal(0.8, 0.2)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nl = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nl.simulation.service_times[Nl.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [2.62, 1.64, 2.19, 2.31, 2.48]
        self.assertEqual(samples, expected)

        samples = [round(Nl.simulation.inter_arrival_times[Nl.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [2.51, 2.33, 1.96, 2.32, 2.70]
        self.assertEqual(samples, expected)


    @given(lm=floats(min_value=-200, max_value=200),
           lsd=floats(min_value=0.001, max_value=80),
           rm=random_module())
    def test_sampling_lognormal_dist_hypothesis(self, lm, lsd, rm):
        params = {
            'arrival_distributions': [ciw.dists.Lognormal(lm, lsd)],
            'service_distributions': [ciw.dists.Lognormal(lm, lsd)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nl = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nl.simulation.service_times[Nl.id_number][0]._sample() >= 0.0)
            self.assertTrue(
                Nl.simulation.inter_arrival_times[Nl.id_number][0]._sample() >= 0.0)

    def test_weibull_dist_object(self):
        W = ciw.dists.Weibull(0.9, 0.8)
        ciw.seed(5)
        samples = [round(W._sample(), 2) for _ in range(10)]
        expected = [0.87, 1.31, 1.60, 3.34, 1.31, 2.91, 0.01, 0.50, 3.36, 0.95]
        self.assertEqual(samples, expected)

    def test_sampling_weibull_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.Weibull(0.9, 0.8)],
            'service_distributions': [ciw.dists.Weibull(0.9, 0.8)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nw = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nw.simulation.service_times[Nw.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.87, 1.31, 1.60, 3.34, 1.31]
        self.assertEqual(samples, expected)

        samples = [round(Nw.simulation.inter_arrival_times[Nw.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [2.91, 0.01, 0.50, 3.36, 0.95]
        self.assertEqual(samples, expected)


    @given(wa=floats(min_value=0.01, max_value=200),
           wb=floats(min_value=0.01, max_value=200),
           rm=random_module())
    def test_sampling_weibull_dist_hypothesis(self, wa, wb, rm):
        params = {
            'arrival_distributions': [ciw.dists.Weibull(wa, wb)],
            'service_distributions': [ciw.dists.Weibull(wa, wb)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nw = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nw.simulation.service_times[Nw.id_number][0]._sample() >= 0.0)
            self.assertTrue(
                Nw.simulation.inter_arrival_times[Nw.id_number][0]._sample() >= 0.0)

    def test_normal_dist_object(self):
        N = ciw.dists.Normal(0.5, 0.1)
        ciw.seed(5)
        samples = [round(N._sample(), 2) for _ in range(10)]
        expected = [0.58, 0.35, 0.49, 0.52, 0.55, 0.56, 0.52, 0.44, 0.52, 0.60]
        self.assertEqual(samples, expected)

    def test_sampling_normal_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.Normal(0.5, 0.1)],
            'service_distributions': [ciw.dists.Normal(0.5, 0.1)],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nn.simulation.service_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.58, 0.35, 0.49, 0.52, 0.55]
        self.assertEqual(samples, expected)

        samples = [round(Nn.simulation.inter_arrival_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.56, 0.52, 0.44, 0.52, 0.60]
        self.assertEqual(samples, expected)


    @given(nm=floats(min_value=0.01, max_value=20),
           ns=floats(min_value=0.0001, max_value=5),
           rm=random_module())
    def test_sampling_normal_dist_hypothesis(self, nm, ns, rm):
        params = {
            'arrival_distributions': [ciw.dists.Normal(nm, ns)],
            'service_distributions': [ciw.dists.Normal(nm, ns)],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nw = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nw.simulation.service_times[Nw.id_number][0]._sample() >= 0.0)
            self.assertTrue(
                Nw.simulation.inter_arrival_times[Nw.id_number][0]._sample() >= 0.0)

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
            'arrival_distributions': [ciw.dists.Empirical(import_empirical(
                'ciw/tests/testing_parameters/sample_empirical_dist.csv'))],
            'service_distributions': [ciw.dists.Empirical(my_empirical_dist)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nem = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nem.simulation.service_times[Nem.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [8.8, 8.8, 8.8, 12.3, 8.8]
        self.assertEqual(samples, expected)

        samples = [round(Nem.simulation.inter_arrival_times[Nem.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [7.3, 7.0, 7.7, 7.3, 7.1]
        self.assertEqual(samples, expected)


    @given(dist=lists(floats(min_value=0.001, max_value=10000),
                      min_size=1,
                      max_size=20),
           rm=random_module())
    def test_sampling_empirical_dist_hypothesis(self, dist, rm):
        my_empirical_dist = dist
        params = {
            'arrival_distributions': [ciw.dists.Empirical(my_empirical_dist)],
            'service_distributions': [ciw.dists.Empirical(import_empirical(
                'ciw/tests/testing_parameters/sample_empirical_dist.csv'))],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nem = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nem.simulation.service_times[
                Nem.id_number][0]._sample() in set([7.0, 7.1, 7.2, 7.3, 7.7, 7.8]))
            self.assertTrue(Nem.simulation.inter_arrival_times[
                Nem.id_number][0]._sample() in set(my_empirical_dist))

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

    def test_sampling_pmf_dist(self):
        my_custom_dist_values =  [3.7, 3.8, 4.1]
        my_custom_dist_probs = [0.2, 0.5, 0.3]
        params = {
            'arrival_distributions': [ciw.dists.Pmf(my_custom_dist_values, my_custom_dist_probs)],
            'service_distributions': [ciw.dists.Pmf(my_custom_dist_values, my_custom_dist_probs)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nc = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nc.simulation.service_times[Nc.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [3.8, 4.1, 4.1, 4.1, 4.1]
        self.assertEqual(samples, expected)

        samples = [round(Nc.simulation.inter_arrival_times[Nc.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [4.1, 3.7, 3.8, 4.1, 3.8]
        self.assertEqual(samples, expected)


    @given(custs=lists(floats(min_value=0.001, max_value=10000),
                       min_size=2,
                       unique=True),
           rm=random_module())
    def test_sampling_pmf_dist_hypothesis(self, custs, rm):
        cust_vals = [round(i, 10) for i in custs]
        numprobs = len(cust_vals)
        probs = [1.0/(numprobs+1) for i in range(numprobs-1)]
        probs.append(1.0 - sum(probs))
        params = {
            'arrival_distributions': [ciw.dists.Pmf(cust_vals, probs)],
            'service_distributions': [ciw.dists.Pmf(cust_vals, probs)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nc = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(Nc.simulation.service_times[
                Nc.id_number][0]._sample() in set(cust_vals))
            self.assertTrue(Nc.simulation.inter_arrival_times[
                Nc.id_number][0]._sample() in set(cust_vals))

    def test_custom_dist_object(self):
        CD = CustomDist()
        ciw.seed(5)
        samples = [round(CD._sample(), 2) for _ in range(10)]
        expected = [1.25, 0.37, 0.4, 0.47, 0.37, 0.46, 0.06, 0.93, 0.47, 1.3]
        self.assertEqual(samples, expected)

    def test_custom_dist(self):
        params = {
            'arrival_distributions': [
                CustomDist(), CustomDist()],
            'service_distributions': [
                CustomDist(), CustomDist()],
            'number_of_servers': [1, 1],
            'routing': [[0.1, 0.1],
                        [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)

        samples = [round(N1.simulation.service_times[N1.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [1.25, 0.37, 0.4, 0.47, 0.37]
        self.assertEqual(samples, expected)

        samples = [round(N2.simulation.service_times[N2.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.46, 0.06, 0.93, 0.47, 1.30]
        self.assertEqual(samples, expected)

        samples = [round(N1.simulation.inter_arrival_times[N1.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.45, 0.06, 0.94, 0.49, 0.27]
        self.assertEqual(samples, expected)

        samples = [round(N2.simulation.inter_arrival_times[N2.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.29, 0.03, 0.43, 0.56, 0.46]
        self.assertEqual(samples, expected)

    def test_noarrivals_object(self):
        Na = ciw.dists.NoArrivals()
        ciw.seed(5)
        samples = [Na._sample() for _ in range(10)]
        expected = [float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf')]
        self.assertEqual(samples, expected)

    def test_no_arrivals_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.NoArrivals()],
            'service_distributions': [ciw.dists.Deterministic(6.6)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Na = Q.transitive_nodes[0]
        ciw.seed(5)
        self.assertEqual(
            Na.simulation.inter_arrival_times[Na.id_number][0]._sample(), float('inf'))

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
            'arrival_distributions': [
                TimeDependentDist1(),
                TimeDependentDist2()],
            'service_distributions': [
                TimeDependentDist1(),
                TimeDependentDist2()],
            'number_of_servers': [1, 1],
            'routing': [[0.1, 0.1],
                        [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ind = ciw.Individual(0)
        ciw.seed(5)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            samples.append(round(N1.simulation.service_times[N1.id_number][0]._sample(t), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            samples.append(round(N2.simulation.service_times[N2.id_number][0]._sample(t), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            Q.current_time = t
            samples.append(round(N1.get_service_time(ind), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            Q.current_time = t
            samples.append(round(N2.get_service_time(ind), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            samples.append(round(N1.simulation.inter_arrival_times[N1.id_number][0]._sample(t), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            samples.append(round(N2.simulation.inter_arrival_times[N2.id_number][0]._sample(t), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

    def test_broken_dist_object(self):
        B = BrokenDist()
        ciw.seed(5)
        self.assertRaises(ValueError, B._sample)

    def test_timedependent_exact(self):
        params = {
            'arrival_distributions': [
                TimeDependentDist1(),
                TimeDependentDist2()],
            'service_distributions': [
                TimeDependentDist1(),
                TimeDependentDist2()],
            'number_of_servers': [1, 1],
            'routing': [[0.1, 0.1],
                        [0.1, 0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params), exact=26)
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ind = ciw.Individual(0)
        ciw.seed(5)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            Q.current_time = t
            samples.append(round(N1.get_service_time(ind), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            Q.current_time = t
            samples.append(round(N2.get_service_time(ind), 2))
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
            'arrival_distributions': [ciw.dists.Sequential([0.2, 0.4, 0.6, 0.8])],
            'service_distributions': [ciw.dists.Sequential([0.9, 0.7, 0.5, 0.3, 0.1])],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ns = Q.transitive_nodes[0]

        samples = [round(Ns.simulation.service_times[Ns.id_number][0]._sample(), 2) for _ in range(7)]
        expected = [0.9, 0.7, 0.5, 0.3, 0.1, 0.9, 0.7]
        self.assertEqual(samples, expected)

        # First arrival will be offset by 1, as first customer's inter-arrival
        # time has already been sampled by the arrival node
        samples = [round(Ns.simulation.inter_arrival_times[Ns.id_number][0]._sample(), 2) for _ in range(6)]
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
            'arrival_distributions': [ciw.dists.Sequential(my_sequential_dist_1)],
            'service_distributions': [ciw.dists.Sequential(my_sequential_dist_2)],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Ns = Q.transitive_nodes[0]

        len1 = len(my_sequential_dist_1)
        len2 = len(my_sequential_dist_2)

        expected_inter_arrival_times = 3*my_sequential_dist_1 + my_sequential_dist_1[:1]
        expected_service_times = 3*my_sequential_dist_2

        inter_arrivals = [Ns.simulation.inter_arrival_times[Ns.id_number][0]._sample() for _ in range(3*len1)]
        services = [Ns.simulation.service_times[Ns.id_number][0]._sample() for _ in range(3*len2)]
        self.assertEqual(inter_arrivals, expected_inter_arrival_times[1:])
        self.assertEqual(services, expected_service_times)

    def test_combining_distributions(self):
        Dt = ciw.dists.Deterministic(5.0)
        Sq = ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0])
        Ex = ciw.dists.Exponential(0.5)

        ## As is
        ciw.seed(0)
        samples = [round(Dt._sample(), 3) for _ in range(6)]
        expected = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Sq._sample(), 3) for _ in range(6)]
        expected = [1.0, 2.0, 3.0, 4.0, 1.0, 2.0]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Ex._sample(), 3) for _ in range(6)]
        expected = [3.721, 2.837, 1.091, 0.599, 1.432, 1.038]
        self.assertEqual(samples, expected)

        ## Addition
        Dt_plus_Sq = ciw.dists.Deterministic(5.0) + ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0])
        Dt_plus_Ex = ciw.dists.Deterministic(5.0) + ciw.dists.Exponential(0.5)
        Sq_plus_Ex = ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0]) + ciw.dists.Exponential(0.5)
        Dt_plus_Sq_plus_Ex = ciw.dists.Deterministic(5.0) + ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0]) + ciw.dists.Exponential(0.5)
        ciw.seed(0)
        samples = [round(Dt_plus_Sq._sample(), 3) for _ in range(6)]
        expected = [6.0, 7.0, 8.0, 9.0, 6.0, 7.0]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Dt_plus_Ex._sample(), 3) for _ in range(6)]
        expected = [8.721, 7.837, 6.091, 5.599, 6.432, 6.038]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Sq_plus_Ex._sample(), 3) for _ in range(6)]
        expected = [4.721, 4.837, 4.091, 4.599, 2.432, 3.038]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Dt_plus_Sq_plus_Ex._sample(), 3) for _ in range(6)]
        expected = [9.721, 9.837, 9.091, 9.599, 7.432, 8.038]
        self.assertEqual(samples, expected)

        ## Substraction
        Dt_minus_Sq = ciw.dists.Deterministic(5.0) - ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0])
        Dt_minus_Ex = ciw.dists.Deterministic(5.0) - ciw.dists.Exponential(0.5)
        ciw.seed(0)
        samples = [round(Dt_minus_Sq._sample(), 3) for _ in range(6)]
        expected = [4.0, 3.0, 2.0, 1.0, 4.0, 3.0]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Dt_minus_Ex._sample(), 3) for _ in range(6)]
        expected = [1.279, 2.163, 3.909, 4.401, 3.568, 3.962]
        self.assertEqual(samples, expected)

        ## Multiplication
        Dt_mult_Sq = ciw.dists.Deterministic(5.0) * ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0])
        Dt_mult_Ex = ciw.dists.Deterministic(5.0) * ciw.dists.Exponential(0.5)
        Sq_mult_Ex = ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0]) * ciw.dists.Exponential(0.5)
        ciw.seed(0)
        samples = [round(Dt_mult_Sq._sample(), 3) for _ in range(6)]
        expected = [5.0, 10.0, 15.0, 20.0, 5.0, 10.0]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Dt_mult_Ex._sample(), 3) for _ in range(6)]
        expected = [18.606, 14.186, 5.457, 2.996, 7.16, 5.191]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Sq_mult_Ex._sample(), 3) for _ in range(6)]
        expected = [3.721, 5.675, 3.274, 2.397, 1.432, 2.076]
        self.assertEqual(samples, expected)

        ## Division
        Dt_div_Sq = ciw.dists.Deterministic(5.0) / ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0])
        Dt_div_Ex = ciw.dists.Deterministic(5.0) / ciw.dists.Exponential(0.5)
        Sq_div_Ex = ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0]) / ciw.dists.Exponential(0.5)
        Sq_div_Dt = ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0]) / ciw.dists.Deterministic(5.0)
        Ex_div_Dt = ciw.dists.Exponential(0.5) / ciw.dists.Deterministic(5.0)
        Ex_div_Sq = ciw.dists.Exponential(0.5) / ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0])
        ciw.seed(0)
        samples = [round(Dt_div_Sq._sample(), 3) for _ in range(6)]
        expected = [5.0, 2.5, 1.667, 1.25, 5.0, 2.5]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Dt_div_Ex._sample(), 3) for _ in range(6)]
        expected = [1.344, 1.762, 4.581, 8.343, 3.492, 4.816]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Sq_div_Ex._sample(), 3) for _ in range(6)]
        expected = [0.269, 0.705, 2.749, 6.675, 0.698, 1.926]
        self.assertEqual(samples, expected)
        ciw.seed(0)
        samples = [round(Sq_div_Dt._sample(), 3) for _ in range(6)]
        expected = [0.2, 0.4, 0.6, 0.8, 0.2, 0.4]
        ciw.seed(0)
        samples = [round(Ex_div_Dt._sample(), 3) for _ in range(6)]
        expected = [5.0, 10.0, 15.0, 20.0, 5.0, 10.0]
        ciw.seed(0)
        samples = [round(Ex_div_Sq._sample(), 3) for _ in range(6)]
        expected = [5.0, 10.0, 15.0, 20.0, 5.0, 10.0]

        ### Test reprs
        self.assertEqual(str(Dt_plus_Sq), 'CombinedDistribution')
        self.assertEqual(str(Dt_plus_Ex), 'CombinedDistribution')
        self.assertEqual(str(Sq_plus_Ex), 'CombinedDistribution')
        self.assertEqual(str(Dt_plus_Sq_plus_Ex), 'CombinedDistribution')
        self.assertEqual(str(Dt_minus_Sq), 'CombinedDistribution')
        self.assertEqual(str(Dt_minus_Ex), 'CombinedDistribution')
        self.assertEqual(str(Dt_mult_Sq), 'CombinedDistribution')
        self.assertEqual(str(Dt_mult_Ex), 'CombinedDistribution')
        self.assertEqual(str(Sq_mult_Ex), 'CombinedDistribution')
        self.assertEqual(str(Dt_div_Sq), 'CombinedDistribution')
        self.assertEqual(str(Dt_div_Ex), 'CombinedDistribution')
        self.assertEqual(str(Sq_div_Dt), 'CombinedDistribution')
        self.assertEqual(str(Sq_div_Ex), 'CombinedDistribution')
        self.assertEqual(str(Ex_div_Dt), 'CombinedDistribution')
        self.assertEqual(str(Ex_div_Sq), 'CombinedDistribution')

    def test_state_dependent_distribution(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(4)],
            service_distributions=[StateDependent()],
            number_of_servers=[1])
        ciw.seed(0)
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(500)
        recs = Q.get_all_records()

        # Only samples 0.2, 0.15, 0.1, 0.05, or 0.0
        services = [round(r.service_time, 7) for r in recs if r.arrival_date > 100]
        self.assertLessEqual(set(services), {0.2, 0.15, 0.1, 0.05, 0.0})

        # Check average service time correct transformation of average queue size
        average_queue_size = sum(s*p for s, p in Q.statetracker.state_probabilities().items())
        self.assertEqual(round(average_queue_size, 7), 0.9468383)
        self.assertEqual(round((-0.05*average_queue_size) + 0.2, 7), 0.1526581)
        self.assertEqual(round(sum(services) / len(services), 7), 0.1529728)


    def test_phasetype_dist_object(self):
        initial_state = [0.3, 0.7, 0.0]
        absorbing_matrix = [
            [-5, 3, 2],
            [0, -4, 4],
            [0, 0, 0]
        ]
        Ph = ciw.dists.PhaseType(initial_state, absorbing_matrix)
        ciw.seed(5)
        samples = [round(Ph._sample(), 2) for _ in range(10)]
        expected = [0.34, 0.71, 0.64, 0.47, 0.03, 0.07, 0.21, 0.7, 0.04, 0.04]
        self.assertEqual(samples, expected)
        self.assertRaises(ValueError, ciw.dists.PhaseType, [-0.3, 0.7, 0.0], absorbing_matrix)
        self.assertRaises(ValueError, ciw.dists.PhaseType, [1.3, 0.7, 0.0], absorbing_matrix)
        self.assertRaises(ValueError, ciw.dists.PhaseType, [0.3, 0.9, 0.0], absorbing_matrix)
        self.assertRaises(ValueError, ciw.dists.PhaseType, initial_state, [[-3, 3], [7, -10, 3]])
        self.assertRaises(ValueError, ciw.dists.PhaseType, initial_state, [[-3, 3], [7, -7]])
        self.assertRaises(ValueError, ciw.dists.PhaseType, initial_state, [[-3, 3], [7, -7]])
        self.assertRaises(ValueError, ciw.dists.PhaseType, initial_state, [[-3, -3, 0], [1, -9, 8], [0, 0, 0]])
        self.assertRaises(ValueError, ciw.dists.PhaseType, initial_state, [[-3, 3, 0], [3, -9, 8], [0, 0, 0]])
        self.assertRaises(ValueError, ciw.dists.PhaseType, initial_state, [[-5, 5, 0], [4, -4, 0], [0, 0, 0]])
        self.assertRaises(ValueError, ciw.dists.PhaseType, initial_state, [[-5, 3, 2], [0, -4, 4], [0, 1, -1]])


    def test_erlang_dist_object(self):
        Er = ciw.dists.Erlang(5, 7)
        ciw.seed(5)
        samples = [round(Er._sample(), 2) for _ in range(10)]
        expected = [2.07, 1.21, 1.28, 1.75, 2.56, 0.5, 1.06, 1.72, 1.17, 1.49]
        self.assertEqual(samples, expected)
        expected_vector = [1, 0, 0, 0, 0, 0, 0, 0]
        expected_matrix = [
          [-5, 5, 0, 0, 0, 0, 0, 0],
          [0, -5, 5, 0, 0, 0, 0, 0],
          [0, 0, -5, 5, 0, 0, 0, 0],
          [0, 0, 0, -5, 5, 0, 0, 0],
          [0, 0, 0, 0, -5, 5, 0, 0],
          [0, 0, 0, 0, 0, -5, 5, 0],
          [0, 0, 0, 0, 0, 0, -5, 5],
          [0, 0, 0,0, 0, 0, 0, 0],
        ]
        self.assertEqual(Er.initial_state, expected_vector)
        self.assertEqual(Er.absorbing_matrix, expected_matrix)

        self.assertRaises(ValueError, ciw.dists.Erlang, -4, 2)
        self.assertRaises(ValueError, ciw.dists.Erlang, 4, -2)
        self.assertRaises(ValueError, ciw.dists.Erlang, -4, -2)

        many_samples = [round(Er.sample(), 4) for _ in range(1000)]
        # We would expect this to be  `num_phases` / `rate` = 7 / 5 = 1.4
        self.assertEqual(round(sum(many_samples) / 1000, 4), 1.4057)

    def test_sampling_erlang_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.Erlang(5, 7)],
            'service_distributions': [ciw.dists.Erlang(5, 7)],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nn.simulation.service_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [2.07, 1.21, 1.28, 1.75, 2.56]
        self.assertEqual(samples, expected)

        samples = [round(Nn.simulation.inter_arrival_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.5, 1.06, 1.72, 1.17, 1.49]
        self.assertEqual(samples, expected)


    @given(sizes=integers(min_value=1, max_value=10),
           rates=floats(min_value=0.1, max_value=20),
           rm=random_module())
    def test_sampling_erlang_dist_hypothesis(self, sizes, rates, rm):
        params = {
            'arrival_distributions': [ciw.dists.Erlang(rates, sizes)],
            'service_distributions': [ciw.dists.Erlang(rates, sizes)],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nw = Q.transitive_nodes[0]
        for itr in range(10): # Because repition happens in the simulation
            self.assertTrue(
                Nw.simulation.service_times[Nw.id_number][0]._sample() >= 0.0)
            self.assertTrue(
                Nw.simulation.inter_arrival_times[Nw.id_number][0]._sample() >= 0.0)


    def test_hyperexponential_dist_object(self):
        Hx = ciw.dists.HyperExponential([5, 7, 2, 1], [0.4, 0.1, 0.3, 0.2])
        ciw.seed(5)
        samples = [round(Hx._sample(), 2) for _ in range(10)]
        expected = [0.68, 1.43, 1.28, 0.13, 1.05, 0.12, 0.04, 0.43, 0.05, 0.5]
        self.assertEqual(samples, expected)
        expected_vector = [0.4, 0.1, 0.3, 0.2, 0]
        expected_matrix = [
            [-5, 0, 0, 0, 5],
            [0, -7, 0, 0, 7],
            [0, 0, -2, 0, 2],
            [0, 0, 0, -1, 1],
            [0, 0, 0, 0, 0]
        ]
        self.assertEqual(Hx.initial_state, expected_vector)
        self.assertEqual(Hx.absorbing_matrix, expected_matrix)

        self.assertRaises(ValueError, ciw.dists.HyperExponential, [5, -7, -2, 1], [0.4, 0.1, 0.3, 0.2])
        self.assertRaises(ValueError, ciw.dists.HyperExponential, [5, 7, 2, 1], [0.4, 5.1, 0.3, 0.2])
        self.assertRaises(ValueError, ciw.dists.HyperExponential, [5, 7, 2, 1], [0.4, -0.1, 0.3, 0.2])
        self.assertRaises(ValueError, ciw.dists.HyperExponential, [5, 7, 2, 1], [0.4, 0.8, 0.3, 0.2])

        many_samples = [round(Hx.sample(), 2) for _ in range(1000)]
        # We would expect this to be sum of the element-wise division of probabilities and rates:
        # (0.4 / 5) + (0.1 / 7) + (0.3 / 2) + (0.2 / 1) = 0.4442857142857143
        self.assertEqual(round(sum(many_samples) / 1000, 4), 0.416)

    def test_sampling_hyperexponential_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.HyperExponential([5, 7, 2, 1], [0.4, 0.1, 0.3, 0.2])],
            'service_distributions': [ciw.dists.HyperExponential([5, 7, 2, 1], [0.4, 0.1, 0.3, 0.2])],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nn.simulation.service_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.68, 1.43, 1.28, 0.13, 1.05]
        self.assertEqual(samples, expected)

        samples = [round(Nn.simulation.inter_arrival_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.12, 0.04, 0.43, 0.05, 0.5]
        self.assertEqual(samples, expected)


    def test_hypererlang_dist_object(self):
        Hg = ciw.dists.HyperErlang([5, 7, 2], [0.5, 0.3, 0.2], [3, 2, 5])
        ciw.seed(5)
        samples = [round(Hg._sample(), 2) for _ in range(10)]
        expected = [0.42, 3.71, 0.35, 0.38, 0.61, 0.25, 0.22, 3.46, 3.07, 1.69]
        self.assertEqual(samples, expected)
        expected_vector = [0.5, 0.0, 0.0, 0.3, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0]
        expected_matrix = [
            [-5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, -5, 5, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 5],
            [0, 0, 0, -7, 7, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, -7, 0, 0, 0, 0, 0, 7],
            [0, 0, 0, 0, 0, -2, 2, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, -2, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, -2, 2, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, -2, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.assertEqual(Hg.initial_state, expected_vector)
        self.assertEqual(Hg.absorbing_matrix, expected_matrix)

        self.assertRaises(ValueError, ciw.dists.HyperErlang, [5, -7, 2], [0.5, 0.3, 0.2], [3, 2, 5])
        self.assertRaises(ValueError, ciw.dists.HyperErlang, [5, 7, 2], [-0.5, 0.3, 0.2], [3, 2, 5])
        self.assertRaises(ValueError, ciw.dists.HyperErlang, [5, 7, 2], [0.5, 1.3, 0.2], [3, 2, 5])
        self.assertRaises(ValueError, ciw.dists.HyperErlang, [5, 7, 2], [0.5, 0.9, 0.2], [3, 2, 5])
        self.assertRaises(ValueError, ciw.dists.HyperErlang, [5, 7, 2], [0.5, 0.3, 0.2], [0, 2, 5])

        many_samples = [round(Hg.sample(), 2) for _ in range(1000)]
        # We would expect this to be sum of the element-wise multiplication of probabilities, inverse rates, and subphase lengths:
        # (0.5 * 3 / 5) + (0.3 * 2 / 7) + (0.2 * 5 / 2) = 0.8857142857142857
        self.assertEqual(round(sum(many_samples) / 1000, 4), 0.8744)

    def test_sampling_hypererlang_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.HyperErlang([5, 7, 2], [0.5, 0.3, 0.2], [3, 2, 5])],
            'service_distributions': [ciw.dists.HyperErlang([5, 7, 2], [0.5, 0.3, 0.2], [3, 2, 5])],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nn.simulation.service_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.42, 3.71, 0.35, 0.38, 0.61]

        self.assertEqual(samples, expected)

        samples = [round(Nn.simulation.inter_arrival_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [0.25, 0.22, 3.46, 3.07, 1.69]
        self.assertEqual(samples, expected)


    def test_coxian_dist_object(self):
        Cx = ciw.dists.Coxian([5, 4, 7, 2], [0.2, 0.5, 0.3, 1.0])
        ciw.seed(5)
        samples = [round(Cx._sample(), 2) for _ in range(10)]
        expected = [1.01, 0.53, 0.18, 0.17, 0.04, 1.09, 0.77, 0.81, 0.08, 0.43]
        self.assertEqual(samples, expected)
        expected_vector = [1.0, 0.0, 0.0, 0.0, 0.0]
        expected_matrix = [
            [-5, (0.8)*5, 0, 0, (0.2)*5],
            [0, -4, (0.5)*4, 0, (0.5)*4],
            [0, 0, -7, (0.7)*7, (0.3)*7],
            [0, 0, 0, -2, 2],
            [0, 0, 0, 0, 0]
        ]
        self.assertEqual(Cx.initial_state, expected_vector)
        self.assertEqual(Cx.absorbing_matrix, expected_matrix)

        self.assertRaises(ValueError, ciw.dists.Coxian, [5, -4, 7, 2], [0.2, 0.5, 0.3, 1.0])
        self.assertRaises(ValueError, ciw.dists.Coxian, [5, 4, 7, 2], [0.2, -0.5, 0.3, 1.0])
        self.assertRaises(ValueError, ciw.dists.Coxian, [5, 4, 7, 2], [0.2, 1.5, 0.3, 1.0])
        self.assertRaises(ValueError, ciw.dists.Coxian, [5, 4, 7, 2], [0.2, 0.5, 0.3, 0.6])

        many_samples = [round(Cx.sample(), 2) for _ in range(1000)]
        # We would expect this to be expected time to absorption of the underlying absobring Markov chain.
        # We can calculate this using Numpy:
        # >>> (np.linalg.inv(np.eye(4) - (np.matrix(absorbing_matrix) / 7 + np.eye(5))[:-1, :-1]) @ np.ones(4))[0, 0] / 7
        # 0.5971428571428571
        self.assertEqual(round(sum(many_samples) / 1000, 4), 0.6035)

    def test_sampling_coxian_dist(self):
        params = {
            'arrival_distributions': [ciw.dists.Coxian([5, 4, 7, 2], [0.2, 0.5, 0.3, 1.0])],
            'service_distributions': [ciw.dists.Coxian([5, 4, 7, 2], [0.2, 0.5, 0.3, 1.0])],
            'number_of_servers': [1],
            'routing': [[0.1]]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [round(Nn.simulation.service_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [1.01, 0.53, 0.18, 0.17, 0.04]

        self.assertEqual(samples, expected)

        samples = [round(Nn.simulation.inter_arrival_times[Nn.id_number][0]._sample(), 2) for _ in range(5)]
        expected = [1.09, 0.77, 0.81, 0.08, 0.43]
        self.assertEqual(samples, expected)


    def test_poissoninterval_dist_object(self):
        ciw.seed(5)
        Pi = ciw.dists.PoissonIntervals(
            rates=[5, 1.5, 3],
            endpoints=[3.2, 7.9, 10],
            max_sample_date=15
        )
        samples = [round(Pi._sample(), 4
            ) for _ in range(10)]
        expected = [0.0928, 0.2694, 0.4268, 0.701, 0.011, 0.239, 0.0966, 0.1567, 0.0834, 0.291]
        self.assertEqual(samples, expected)

        expected_dates = [0]
        for t in Pi.inter_arrivals:
            expected_dates.append(expected_dates[-1] + t)
        self.assertEqual(Pi.dates, expected_dates)
        self.assertLessEqual(Pi.dates[-1], Pi.max_sample_date)

        self.assertRaises(ValueError, ciw.dists.PoissonIntervals, [5, -1.5, 3], [3.2, 7.9, 10], 15)
        self.assertRaises(ValueError, ciw.dists.PoissonIntervals, [5, 1.5, 3], [3.2, 1.9, 10], 15)
        self.assertRaises(ValueError, ciw.dists.PoissonIntervals, [5, 1.5, 3], [-3.2, 7.9, 10], 15)
        self.assertRaises(ValueError, ciw.dists.PoissonIntervals, [5, 1.5, 3], [3.2, 7.9, 10], -15)
        self.assertRaises(ValueError, ciw.dists.PoissonIntervals, [5, 1.5, 3], [3.2, 7.9, 10], 0)
        self.assertRaises(ValueError, ciw.dists.PoissonIntervals, [5, 1.5, 3, 6], [3.2, 7.9, 10], 15)

    def test_poissoninterval_rate_zero(self):
        ciw.seed(5)
        Pi = ciw.dists.PoissonIntervals(
            rates=[10, 0],
            endpoints=[1, 2],
            max_sample_date=15
        )
        arrivals_when_rate_is_zero = [date for date in Pi.dates if int(date) % 2 == 1]
        self.assertEqual(arrivals_when_rate_is_zero, [])

    def test_poissoninterval_against_theory(self):
        """
        rates = [5, 1.5, 3]
        endpoints = [3.2, 7.9, 10]
        max_sample_date = 20
        (0.0, 3.2) --- Two lots of intervals of length 3.2, with rate 5.   Expected: 5x3.2x2 = 32
        (3.2, 7.9) --- Two lots of intervals of length 4.7, with rate 1.5. Expected: 1.5x4.7x2 = 14.1
        (7.9, 10)  --- Two lots of intervals of length 2.1, with rate 3.   Expected: 3x2.1x2 = 12.6
        """
        ciw.seed(0)
        n = 250
        distributions = [
            ciw.dists.PoissonIntervals(
                rates=[5, 1.5, 3],
                endpoints=[3.2, 7.9, 10],
                max_sample_date=20)
            for _ in range(n)
        ]
        counts = {
            (0, 3.2) : sum([sum([((r > 0) and (r < 3.2)) or ((r > 10) and (r < 13.2)) for r in Pi.dates]) for Pi in distributions]) / n,
            (3.2, 7.9): sum([sum([((r > 3.2) and (r < 7.9)) or ((r > 13.2) and (r < 17.9)) for r in Pi.dates]) for Pi in distributions]) / n,
            (7.9, 10): sum([sum([((r > 7.9) and (r < 10)) or ((r > 17.9) and (r < 20)) for r in Pi.dates]) for Pi in distributions]) / n
        }
        self.assertEqual(counts[(0, 3.2)],   31.756) ## expected 32
        self.assertEqual(counts[(3.2, 7.9)], 14.184) ## expected 14.1
        self.assertEqual(counts[(7.9, 10)],  12.748) ## expected 12.6

        """
        rates = [2, 0.6, 0.8, 12, 3]
        endpoints = [0.5, 10, 32, 40.3, 50]
        max_sample_date = 100
        (0.0, 0.5) --- Two lots of intervals of length 0.5, with rate 2.   Expected: 0.5x2x2 = 2
        (0.5, 10)  --- Two lots of intervals of length 9.5, with rate 0.6. Expected: 9.5x0.6x2 = 11.4
        (10, 32)   --- Two lots of intervals of length 22, with rate 0.8.  Expected: 22x0.8x2 = 35.2
        (32, 40.3) --- Two lots of intervals of length 8.3, with rate 12.  Expected: 8.3x12x2 = 199.2
        (40.3, 50) --- Two lots of intervals of length 9.7, with rate 3.   Expected: 9.7x3x2 = 58.2
        """
        ciw.seed(0)
        n = 250
        distributions = [
            ciw.dists.PoissonIntervals(
                rates=[2, 0.6, 0.8, 12, 3],
                endpoints=[0.5, 10, 32, 40.3, 50],
                max_sample_date=100)
            for _ in range(n)
        ]
        counts = {
            (0, 0.5) : sum([sum([((r > 0) and (r < 0.5)) or ((r > 50) and (r < 50.5)) for r in Pi.dates]) for Pi in distributions]) / n,
            (0.5, 10) : sum([sum([((r > 0.5) and (r < 10)) or ((r > 50.5) and (r < 60)) for r in Pi.dates]) for Pi in distributions]) / n,
            (10, 32) : sum([sum([((r > 10) and (r < 32)) or ((r > 60) and (r < 82)) for r in Pi.dates]) for Pi in distributions]) / n,
            (32, 40.3) : sum([sum([((r > 32) and (r < 40.3)) or ((r > 82) and (r < 90.3)) for r in Pi.dates]) for Pi in distributions]) / n,
            (40.3, 50) : sum([sum([((r > 40.3) and (r < 50)) or ((r > 90.3) and (r < 100)) for r in Pi.dates]) for Pi in distributions]) / n,
        }
        self.assertEqual(counts[(0, 0.5)],   2.016)   ## expected 2
        self.assertEqual(counts[(0.5, 10)],  11.4)    ## expected 11.4
        self.assertEqual(counts[(10, 32)],   35.324)  ## expected 35.2
        self.assertEqual(counts[(32, 40.3)], 198.968) ## expected 199.2
        self.assertEqual(counts[(40.3, 50)], 58.12)  ## expected 58.2

    def test_sampling_poissoninterval_dist(self):
        ciw.seed(5)
        params = {
            'arrival_distributions': [ciw.dists.PoissonIntervals(rates=[5, 1.5, 3], endpoints=[3.2, 7.9, 10], max_sample_date=15)],
            'service_distributions': [ciw.dists.PoissonIntervals(rates=[5, 1.5, 3], endpoints=[3.2, 7.9, 10], max_sample_date=15)],
            'number_of_servers': [1]
        }
        Q = ciw.Simulation(ciw.create_network(**params))
        Nt = Q.transitive_nodes[0]

        samples = [round(Nt.simulation.service_times[Nt.id_number][0]._sample(), 4) for _ in range(10)]
        expected = [0.0108, 0.0623, 0.1092, 0.026, 0.2578, 0.0648, 0.4333, 0.0275, 0.0187, 0.0707]
        self.assertEqual(samples, expected)

        samples = [round(Nt.simulation.inter_arrival_times[Nt.id_number][0]._sample(), 4) for _ in range(10)]
        expected = [0.2694, 0.4268, 0.701, 0.011, 0.239, 0.0966, 0.1567, 0.0834, 0.291, 0.006]
        self.assertEqual(samples, expected)

