import unittest
import ciw
import math
from math import sqrt, exp, pi, erf
import numpy as np
import statistics as st
from csv import reader
from random import random, choice
from hypothesis import given
from hypothesis.strategies import floats, integers, lists, random_module, text
import os
import tqdm


def import_empirical(dist_file):
    """
    Imports an empirical distribution from a .csv file
    """
    root = os.getcwd()
    file_name = root + "/" + dist_file
    empirical_file = open(file_name, "r")
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
        if int(str(val * 10)[0]) % 2 == 0:
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
        return max((-0.05 * n) + 0.2, 0)


def compare_theoretical_to_observed(D, n, places, self):
    samples = [D.sample() for _ in range(n)]
    if D.mean is not None:
        self.assertAlmostEqual(np.mean(samples), D.mean, places=places)
    if not math.isnan(D.variance):
        self.assertAlmostEqual(np.var(samples), D.variance, places=places)
    if not math.isnan(D.sd):
        self.assertAlmostEqual(np.std(samples), D.sd, places=places)
    if not math.isnan(D.median):
        self.assertAlmostEqual(np.median(samples), D.median, places=places)
    if not math.isnan(D.lower_limit):
        self.assertTrue(min(samples) >= D.lower_limit)
    if not math.isnan(D.upper_limit):
        self.assertTrue(max(samples) <= D.upper_limit)


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
        Sq_short = ciw.dists.Sequential([3.3, 10.1])
        Sq = ciw.dists.Sequential([3.3, 3.3, 4.4, 3.3, 4.4])
        Pf = ciw.dists.Pmf([1.1, 2.2, 3.3], [0.3, 0.2, 0.5])
        Ph = ciw.dists.PhaseType([1, 0, 0], [[-3, 2, 1], [1, -5, 4], [0, 0, 0]])
        Er = ciw.dists.Erlang(4.5, 8)
        Hx = ciw.dists.HyperExponential([4, 7, 2], [0.3, 0.1, 0.6])
        He = ciw.dists.HyperErlang([4, 7, 2], [0.3, 0.1, 0.6], [2, 2, 7])
        Cx = ciw.dists.Coxian([4, 7, 2], [0.3, 0.2, 1.0])
        Pi = ciw.dists.PoissonIntervals(rates=[5, 1.5, 3], endpoints=[3.2, 7.9, 10], max_sample_date=15)
        Po = ciw.dists.Poisson(rate=1.5)
        Ge = ciw.dists.Geometric(prob=0.3)
        Bi = ciw.dists.Binomial(n=20, prob=0.7)
        self.assertEqual(str(Di), "Distribution")
        self.assertEqual(str(Un), "Uniform(lower=3.4, upper=6.7)")
        self.assertEqual(str(Dt), "Deterministic(value=1.1)")
        self.assertEqual(str(Tr), "Triangular(lower=1.1, mode=2.2, upper=3.3)")
        self.assertEqual(str(Ex), "Exponential(rate=0.4)")
        self.assertEqual(str(Ga), "Gamma(shape=2.1, scale=4.1)")
        self.assertEqual(str(No), "Normal(mean=5.5, sd=0.6)")
        self.assertEqual(str(Ln), "Lognormal(mean=5.5, sd=3.6)")
        self.assertEqual(str(Wb), "Weibull(shape=9.9, scale=8.8)")
        self.assertEqual(str(Em), "Empirical")
        self.assertEqual(str(Sq_short), "Sequential([3.3, 10.1])")
        self.assertEqual(str(Sq), "Sequential([3.3, ..., 4.4])")
        self.assertEqual(str(Pf), "Pmf(values=[1.1, 2.2, 3.3], probs=[0.3, 0.2, 0.5])")
        self.assertEqual(str(Ph), "PhaseType")
        self.assertEqual(str(Er), "Erlang(rate=4.5, k=8)")
        self.assertEqual(str(Hx), "HyperExponential")
        self.assertEqual(str(He), "HyperErlang")
        self.assertEqual(str(Cx), "Coxian")
        self.assertEqual(str(Pi), "PoissonIntervals")
        self.assertEqual(str(Po), "Poisson(rate=1.5)")
        self.assertEqual(str(Ge), "Geometric(prob=0.3)")
        self.assertEqual(str(Bi), "Binomial(n=20, prob=0.7)")

    def test_distribution_parent_is_useless(self):
        D = ciw.dists.Distribution()
        self.assertEqual(str(D), "Distribution")
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
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Uniform(2.2, 3.3)],
            service_distributions=[ciw.dists.Uniform(2.2, 3.3)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nu = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nu.simulation.service_times[Nu.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [2.89, 3.02, 3.07, 3.24, 3.01]
        self.assertEqual(samples, expected)

        samples = [
            round(Nu.simulation.inter_arrival_times[Nu.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [3.21, 2.23, 2.71, 3.24, 2.91]
        self.assertEqual(samples, expected)

    @given(
        u=lists(
            floats(min_value=0.0, max_value=10000), min_size=2, max_size=2, unique=True
        ).map(sorted),
        rm=random_module(),
    )
    def test_sampling_uniform_dist_hypothesis(self, u, rm):
        ul, uh = u[0], u[1]
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Uniform(ul, uh)],
            service_distributions=[ciw.dists.Uniform(ul, uh)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nu = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(
                ul <= Nu.simulation.service_times[Nu.id_number]['Customer']._sample() <= uh
            )
            self.assertTrue(
                ul <= Nu.simulation.inter_arrival_times[Nu.id_number]['Customer']._sample() <= uh
            )
    
    def test_uniform_summary_stats(self):
        """
        Test that the mean of a Uniform distribution is computed correctly.
        """
        U = ciw.dists.Uniform(2.2, 3.3)
        expected_mean = (2.2 + 3.3) / 2
        self.assertEqual(U.mean, expected_mean)
        expected_variance = ((3.3 - 2.2) ** 2) / 12
        self.assertEqual(U.variance, expected_variance)
        self.assertEqual(U.sd, math.sqrt(((3.3 - 2.2) ** 2) / 12))
        self.assertEqual(U.median, (2.2 + 3.3) / 2)
        self.assertEqual(U.lower_limit, 2.2)
        self.assertEqual(U.upper_limit, 3.3)

    def test_deterministic_dist_object(self):
        D = ciw.dists.Deterministic(4.4)
        ciw.seed(5)
        samples = [round(D._sample(), 2) for _ in range(10)]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)
        self.assertRaises(ValueError, ciw.dists.Deterministic, -4.4)

    def test_sampling_deterministic_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(4.4)],
            service_distributions=[ciw.dists.Deterministic(4.4)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nd = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nd.simulation.service_times[Nd.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)

        samples = [
            round(Nd.simulation.inter_arrival_times[Nd.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [4.40, 4.40, 4.40, 4.40, 4.40]
        self.assertEqual(samples, expected)

    @given(d=floats(min_value=0.0, max_value=10000), rm=random_module())
    def test_sampling_deterministic_dist_hypothesis(self, d, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(d)],
            service_distributions=[ciw.dists.Deterministic(d)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nd = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertEqual(Nd.simulation.service_times[Nd.id_number]['Customer']._sample(), d)
            self.assertEqual(
                Nd.simulation.inter_arrival_times[Nd.id_number]['Customer']._sample(), d
            )

    def test_deterministic_summary_stats(self):
        D = ciw.dists.Deterministic(4.4)
        self.assertEqual(D.mean, 4.4)
        self.assertEqual(D.variance, 0.0)
        self.assertEqual(D.sd, 0.0)
        self.assertEqual(D.median, 4.4)
        self.assertEqual(D.upper_limit, 4.4)
        self.assertEqual(D.lower_limit, 4.4)

    def test_triangular_dist_object(self):
        Tr = ciw.dists.Triangular(1.1, 1.5, 6.6)
        ciw.seed(5)
        samples = [round(Tr._sample(), 2) for _ in range(10)]
        expected = [3.35, 3.91, 4.20, 5.33, 3.90, 5.12, 1.35, 2.73, 5.34, 3.46]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Triangular, -4.4, -0.3, 1.4)
        self.assertRaises(ValueError, ciw.dists.Triangular, 1.3, 2.5, 1.0)

    def test_sampling_triangular_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Triangular(1.1, 1.5, 6.6)],
            service_distributions=[ciw.dists.Triangular(1.1, 1.5, 6.6)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nt = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nt.simulation.service_times[Nt.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [3.35, 3.91, 4.20, 5.33, 3.90]
        self.assertEqual(samples, expected)

        samples = [
            round(Nt.simulation.inter_arrival_times[Nt.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [5.12, 1.35, 2.73, 5.34, 3.46]
        self.assertEqual(samples, expected)

    @given(
        t=lists(floats(min_value=0.0, max_value=10000), min_size=3, max_size=3, unique=True).map(sorted),
        rm=random_module(),
    )
    def test_sampling_triangular_dist_hypothesis(self, t, rm):
        tl, tm, th = t[0], t[1], t[2]
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Triangular(tl, tm, th)],
            service_distributions=[ciw.dists.Triangular(tl, tm, th)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nt = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(tl <= Nt.simulation.service_times[Nt.id_number]['Customer']._sample() <= th)
            self.assertTrue(tl <= Nt.simulation.inter_arrival_times[Nt.id_number]['Customer']._sample() <= th)

    def test_triangular_summary_stats(self):
        a, b, c = 1.1, 6.6, 2.2
        T = ciw.dists.Triangular(a, c, b)
        expected_mean = (1.1 + 2.2 + 6.6) / 3
        self.assertEqual(T.mean, expected_mean)
        expected_variance = (a**2 + b**2 + c**2 - a*b - a*c - b*c) / 18
        self.assertEqual(T.variance, expected_variance)
        self.assertEqual(T.sd, math.sqrt(expected_variance))
        mid = (a + b) / 2.0
        expected_median = b - math.sqrt((b - a) * (b - c) / 2.0)
        self.assertEqual(T.median, expected_median)
        self.assertEqual(T.upper_limit, b)
        self.assertEqual(T.lower_limit, a)

    def test_triangular_median_right_mode_branch(self):
        a, b, c = 1.0, 8.0, 7.0   # mode c is to the right of the midpoint
        T = ciw.dists.Triangular(a, c, b)
        mid = (a + b) / 2.0
        self.assertTrue(c >= mid)  
        expected = a + math.sqrt((b - a) * (c - a) / 2.0)
        self.assertEqual(T.median, expected)


    def test_exponential_dist_object(self):
        E = ciw.dists.Exponential(4.4)
        ciw.seed(5)
        samples = [round(E._sample(), 2) for _ in range(10)]
        expected = [0.22, 0.31, 0.36, 0.65, 0.31, 0.58, 0.01, 0.14, 0.65, 0.24]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Exponential, -4.4)
        self.assertRaises(ValueError, ciw.dists.Exponential, 0.0)

    def test_sampling_exponential_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(4.4)],
            service_distributions=[ciw.dists.Exponential(4.4)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Ne = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Ne.simulation.service_times[Ne.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.22, 0.31, 0.36, 0.65, 0.31]
        self.assertEqual(samples, expected)

        samples = [
            round(Ne.simulation.inter_arrival_times[Ne.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.58, 0.01, 0.14, 0.65, 0.24]
        self.assertEqual(samples, expected)

    @given(e=floats(min_value=0.001, max_value=10000), rm=random_module())
    def test_sampling_exponential_dist_hypothesis(self, e, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(e)],
            service_distributions=[ciw.dists.Exponential(e)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Ne = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(
                Ne.simulation.service_times[Ne.id_number]['Customer']._sample() >= 0.0
            )
            self.assertTrue(
                Ne.simulation.inter_arrival_times[Ne.id_number]['Customer']._sample() >= 0.0
            )
    def test_exponential_summary_stats(self):
        """
        Test that the mean of the Exponential distribution is computed correctly.
        """
        E = ciw.dists.Exponential(4.4)
        expected_mean = 1 / 4.4
        self.assertEqual(E.mean, expected_mean)
        expected_variance = 1 / (4.4 ** 2)
        self.assertEqual(E.variance, expected_variance)
        self.assertEqual(E.sd, 1.0 / 4.4)
        self.assertEqual(E.median, math.log(2.0) / 4.4)
        self.assertTrue(math.isinf(E.upper_limit))
        self.assertEqual(E.lower_limit, 0.0)

    def test_gamma_dist_object(self):
        G = ciw.dists.Gamma(0.6, 1.2)
        ciw.seed(5)
        samples = [round(G._sample(), 2) for _ in range(10)]
        expected = [0.0, 2.59, 1.92, 0.47, 0.61, 0.00, 1.07, 1.15, 0.75, 0.00]
        self.assertEqual(samples, expected)

    def test_sampling_gamma_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Gamma(0.6, 1.2)],
            service_distributions=[ciw.dists.Gamma(0.6, 1.2)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Ng = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Ng.simulation.service_times[Ng.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.0, 2.59, 1.92, 0.47, 0.61]
        self.assertEqual(samples, expected)

        samples = [
            round(Ng.simulation.inter_arrival_times[Ng.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.00, 1.07, 1.15, 0.75, 0.00]
        self.assertEqual(samples, expected)

    @given(
        ga=floats(min_value=0.001, max_value=10000),
        gb=floats(min_value=0.001, max_value=10000),
        rm=random_module(),
    )
    def test_sampling_gamma_dist_hypothesis(self, ga, gb, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Gamma(ga, gb)],
            service_distributions=[ciw.dists.Gamma(ga, gb)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Ng = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(
                Ng.simulation.service_times[Ng.id_number]['Customer']._sample() >= 0.0
            )
            self.assertTrue(
                Ng.simulation.inter_arrival_times[Ng.id_number]['Customer']._sample() >= 0.0
            )
    
    def test_gamma_summary_stats(self):
        G = ciw.dists.Gamma(0.6, 1.2)
        expected_mean = 0.6 * 1.2
        expected_variance = 0.6 * (1.2 ** 2)
        self.assertEqual(G.sd, math.sqrt(G.variance))
        self.assertTrue(math.isnan(G.median))
        self.assertTrue(math.isinf(G.upper_limit))
        self.assertEqual(G.lower_limit, 0.0)

    def test_lognormal_dist_object(self):
        Ln = ciw.dists.Lognormal(0.8, 0.2)
        ciw.seed(5)
        samples = [round(Ln._sample(), 2) for _ in range(10)]
        expected = [2.62, 1.64, 2.19, 2.31, 2.48, 2.51, 2.33, 1.96, 2.32, 2.70]
        self.assertEqual(samples, expected)

    def test_sampling_lognormal_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Lognormal(0.8, 0.2)],
            service_distributions=[ciw.dists.Lognormal(0.8, 0.2)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nl = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nl.simulation.service_times[Nl.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [2.62, 1.64, 2.19, 2.31, 2.48]
        self.assertEqual(samples, expected)

        samples = [
            round(Nl.simulation.inter_arrival_times[Nl.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [2.51, 2.33, 1.96, 2.32, 2.70]
        self.assertEqual(samples, expected)

    @given(
        lm=floats(min_value=-200, max_value=200),
        lsd=floats(min_value=0.001, max_value=80),
        rm=random_module(),
    )
    def test_sampling_lognormal_dist_hypothesis(self, lm, lsd, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Lognormal(lm, lsd)],
            service_distributions=[ciw.dists.Lognormal(lm, lsd)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nl = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(Nl.simulation.service_times[Nl.id_number]['Customer']._sample() >= 0.0)
            self.assertTrue(Nl.simulation.inter_arrival_times[Nl.id_number]['Customer']._sample() >= 0.0)

    def test_lognormal_summary_stats(self):
        mu = 0.7
        sigma = 0.4
        L = ciw.dists.Lognormal(mu, sigma)

        expected_mean = math.exp(mu + (sigma ** 2) / 2)
        expected_variance = (math.exp(sigma ** 2) - 1) * math.exp(2 * mu + sigma ** 2)
        self.assertEqual(L.mean, expected_mean)
        self.assertEqual(L.variance, expected_variance)
        self.assertEqual(L.sd, math.sqrt(L.variance))
        self.assertEqual(L.median, math.exp(0.7))
        self.assertTrue(math.isinf(L.upper_limit))
        self.assertEqual(L.lower_limit, 0.0)

    def test_weibull_dist_object(self):
        W = ciw.dists.Weibull(0.9, 0.8)
        ciw.seed(5)
        samples = [round(W._sample(), 2) for _ in range(10)]
        expected = [0.87, 1.31, 1.60, 3.34, 1.31, 2.91, 0.01, 0.50, 3.36, 0.95]
        self.assertEqual(samples, expected)

    def test_sampling_weibull_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Weibull(0.9, 0.8)],
            service_distributions=[ciw.dists.Weibull(0.9, 0.8)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nw = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nw.simulation.service_times[Nw.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.87, 1.31, 1.60, 3.34, 1.31]
        self.assertEqual(samples, expected)

        samples = [
            round(Nw.simulation.inter_arrival_times[Nw.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [2.91, 0.01, 0.50, 3.36, 0.95]
        self.assertEqual(samples, expected)

    @given(
        wa=floats(min_value=0.01, max_value=200),
        wb=floats(min_value=0.01, max_value=200),
        rm=random_module(),
    )
    def test_sampling_weibull_dist_hypothesis(self, wa, wb, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Weibull(wa, wb)],
            service_distributions=[ciw.dists.Weibull(wa, wb)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nw = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(
                Nw.simulation.service_times[Nw.id_number]['Customer']._sample() >= 0.0
            )
            self.assertTrue(
                Nw.simulation.inter_arrival_times[Nw.id_number]['Customer']._sample() >= 0.0
            )

    def test_weibull_summary_stats(self):
        W = ciw.dists.Weibull(0.8, 0.9)
        expected_mean = 0.8 * math.gamma(1 + 1 / 0.9)
        g1 = math.gamma(1 + 1 / 0.9)
        g2 = math.gamma(1 + 2 / 0.9)
        expected_variance = (0.8 ** 2) * (g2 - g1 ** 2)
        self.assertEqual(W.variance, expected_variance)
        self.assertEqual(W.sd, math.sqrt(W.variance))
        self.assertEqual(W.median, 0.8 * (math.log(2) ** (1.0 / 0.9)))
        self.assertTrue(math.isinf(W.upper_limit))
        self.assertEqual(W.lower_limit, 0.0)

    def test_normal_dist_object(self):
        N = ciw.dists.Normal(0.5, 0.1)
        ciw.seed(5)
        samples = [round(N._sample(), 2) for _ in range(10)]
        expected = [0.58, 0.35, 0.49, 0.52, 0.55, 0.56, 0.52, 0.44, 0.52, 0.60]
        self.assertEqual(samples, expected)

    def test_sampling_normal_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Normal(0.5, 0.1)],
            service_distributions=[ciw.dists.Normal(0.5, 0.1)],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nn.simulation.service_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.58, 0.35, 0.49, 0.52, 0.55]
        self.assertEqual(samples, expected)

        samples = [
            round(Nn.simulation.inter_arrival_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.56, 0.52, 0.44, 0.52, 0.60]
        self.assertEqual(samples, expected)

    @given(
        nm=floats(min_value=0.01, max_value=20),
        ns=floats(min_value=0.0001, max_value=5),
        rm=random_module(),
    )
    def test_sampling_normal_dist_hypothesis(self, nm, ns, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Normal(nm, ns)],
            service_distributions=[ciw.dists.Normal(nm, ns)],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Nw = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(Nw.simulation.service_times[Nw.id_number]['Customer']._sample() >= 0.0)
            self.assertTrue(Nw.simulation.inter_arrival_times[Nw.id_number]['Customer']._sample() >= 0.0)
    
    def test_normal_truncated_summary_stats(self):
        N = ciw.dists.Normal(5.0, 1.0)
        mu = N._mean
        sd = N._sd
        z = mu / sd
        phi = (1 / sqrt(2 * pi)) * exp(-0.5 * z**2)
        Phi = 0.5 * (1 + erf(z / sqrt(2)))
        expected_mean = mu + sd * (phi / Phi)
        expected_variance = sd**2 * (1 - z * (phi / Phi) - (phi / Phi)**2)
        self.assertEqual(N.mean, expected_mean)
        self.assertEqual(N.variance, expected_variance)
        self.assertEqual(N.sd, math.sqrt(N.variance))
        Norm = st.NormalDist(0, 1)
        target = 1.0 - 0.5 * Norm.cdf(z)
        expected_med = mu + sd * Norm.inv_cdf(target)
        self.assertEqual(N.median, expected_med)
        self.assertTrue(math.isinf(N.upper_limit))
        self.assertEqual(N.lower_limit, 0.0)

    def test_empirical_dist_object(self):
        Em = ciw.dists.Empirical([8.0, 8.0, 8.0, 8.8, 8.8, 12.3])
        ciw.seed(5)
        samples = [round(Em._sample(), 2) for _ in range(10)]
        expected = [8.8, 8.8, 8.8, 12.3, 8.8, 12.3, 8.0, 8.0, 12.3, 8.8]
        self.assertEqual(samples, expected)
        self.assertRaises(ValueError, ciw.dists.Empirical, [-4.4, -0.3, 1.4, 1.4])

    def test_sampling_empirical_dist(self):
        my_empirical_dist = [8.0, 8.0, 8.0, 8.8, 8.8, 12.3]
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Empirical(import_empirical("tests/sample_empirical_dist.csv"))],
            service_distributions=[ciw.dists.Empirical(my_empirical_dist)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nem = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nem.simulation.service_times[Nem.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [8.8, 8.8, 8.8, 12.3, 8.8]
        self.assertEqual(samples, expected)

        samples = [
            round(Nem.simulation.inter_arrival_times[Nem.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [7.3, 7.0, 7.7, 7.3, 7.1]
        self.assertEqual(samples, expected)

    @given(
        dist=lists(floats(min_value=0.001, max_value=10000), min_size=1, max_size=20),
        rm=random_module(),
    )
    def test_sampling_empirical_dist_hypothesis(self, dist, rm):
        my_empirical_dist = dist
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Empirical(my_empirical_dist)],
            service_distributions=[ciw.dists.Empirical(import_empirical("tests/sample_empirical_dist.csv"))],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nem = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(
                Nem.simulation.service_times[Nem.id_number]['Customer']._sample()
                in set([7.0, 7.1, 7.2, 7.3, 7.7, 7.8])
            )
            self.assertTrue(
                Nem.simulation.inter_arrival_times[Nem.id_number]['Customer']._sample()
                in set(my_empirical_dist)
            )

    def test_empirical_summary_stats(self):
        values = [8.0, 8.0, 8.0, 8.8, 8.8, 12.3]
        Em = ciw.dists.Empirical(values)
        expected_mean = sum(values) / len(values)
        self.assertEqual(Em.mean, expected_mean)
        mean = sum(values) / len(values)
        expected_variance = sum((x - mean) ** 2 for x in values) / len(values)
        self.assertEqual(Em.variance, expected_variance)
        self.assertEqual(Em.sd, math.sqrt(Em.variance))
        self.assertEqual(Em.median, (8.0 + 8.8) / 2.0)
        self.assertEqual(Em.upper_limit, 12.3)
        self.assertEqual(Em.lower_limit, 8.0)

    def test_empirical_median(self):
        # even
        Em = ciw.dists.Empirical([1, 2, 3, 6])
        self.assertEqual(Em.median, 2.5)
        self.assertEqual(Em.mean, 3)
        # odd
        values = [5.0, 7.0, 9.0]  
        E = ciw.dists.Empirical(values)
        self.assertEqual(E.median, 7.0) 
        self.assertEqual(E.mean, 7.0) 

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
        custom_dist_values = [3.7, 3.8, 4.1]
        custom_dist_probs = [0.2, 0.5, 0.3]
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Pmf(custom_dist_values, custom_dist_probs)],
            service_distributions=[ciw.dists.Pmf(custom_dist_values, custom_dist_probs)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nc = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nc.simulation.service_times[Nc.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [3.8, 4.1, 4.1, 4.1, 4.1]
        self.assertEqual(samples, expected)

        samples = [
            round(Nc.simulation.inter_arrival_times[Nc.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [4.1, 3.7, 3.8, 4.1, 3.8]
        self.assertEqual(samples, expected)

    @given(
        custs=lists(floats(min_value=0.001, max_value=10000), min_size=2, unique=True),
        rm=random_module(),
    )
    def test_sampling_pmf_dist_hypothesis(self, custs, rm):
        cust_vals = [round(i, 10) for i in custs]
        numprobs = len(cust_vals)
        probs = [1.0 / (numprobs + 1) for i in range(numprobs - 1)]
        probs.append(1.0 - sum(probs))
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Pmf(cust_vals, probs)],
            service_distributions=[ciw.dists.Pmf(cust_vals, probs)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nc = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(Nc.simulation.service_times[Nc.id_number]['Customer']._sample() in set(cust_vals))
            self.assertTrue(Nc.simulation.inter_arrival_times[Nc.id_number]['Customer']._sample() in set(cust_vals))


    def test_pmf_summary_stats(self):
        values = [3.7, 3.8, 4.1]
        probs = [0.2, 0.5, 0.3]
        P = ciw.dists.Pmf(values, probs)
        expected_mean = sum(v * p for v, p in zip(values, probs))
        self.assertEqual(P.mean, expected_mean)
        expected_variance = sum(p * (v - expected_mean) ** 2 for v, p in zip(values, probs))
        self.assertEqual(P.variance, expected_variance)
        self.assertEqual(P.sd, math.sqrt(P.variance))
        self.assertEqual(P.median, 3.8)
        self.assertEqual(P.upper_limit, 4.1)
        self.assertEqual(P.lower_limit, 3.7)

    def test_pmf_median_fallback(self):
        # Force sum of probs < 1.0 to trigger fallback
        P = ciw.dists.Pmf.__new__(ciw.dists.Pmf) 
        P.values = [1.0, 2.0, 3.0]
        P.probs = [0.1, 0.1, 0.1]  # sum = 0.3, so cumulative never reaches 0.5
        self.assertEqual(P.median, 3.0)  


    def test_custom_dist_object(self):
        CD = CustomDist()
        ciw.seed(5)
        samples = [round(CD._sample(), 2) for _ in range(10)]
        expected = [1.25, 0.37, 0.4, 0.47, 0.37, 0.46, 0.06, 0.93, 0.47, 1.3]
        self.assertEqual(samples, expected)

    def test_custom_dist(self):
        N = ciw.create_network(
            arrival_distributions=[CustomDist(), CustomDist()],
            service_distributions=[CustomDist(), CustomDist()],
            number_of_servers=[1, 1],
            routing=[[0.1, 0.1], [0.1, 0.1]],
        )
        Q = ciw.Simulation(N)
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ciw.seed(5)

        samples = [
            round(N1.simulation.service_times[N1.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [1.25, 0.37, 0.4, 0.47, 0.37]
        self.assertEqual(samples, expected)

        samples = [
            round(N2.simulation.service_times[N2.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.46, 0.06, 0.93, 0.47, 1.30]
        self.assertEqual(samples, expected)

        samples = [
            round(N1.simulation.inter_arrival_times[N1.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.45, 0.06, 0.94, 0.49, 0.27]
        self.assertEqual(samples, expected)

        samples = [
            round(N2.simulation.inter_arrival_times[N2.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.29, 0.03, 0.43, 0.56, 0.46]
        self.assertEqual(samples, expected)

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
        N = ciw.create_network(
            arrival_distributions=[TimeDependentDist1(), TimeDependentDist2()],
            service_distributions=[TimeDependentDist1(), TimeDependentDist2()],
            number_of_servers=[1, 1],
            routing=[[0.1, 0.1], [0.1, 0.1]],
        )
        Q = ciw.Simulation(N)
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        ind = ciw.Individual(0)
        ciw.seed(5)

        samples = []
        for t in [3.0, 9.0, 9.0, 11.0, 11.0]:
            samples.append(round(N1.simulation.service_times[N1.id_number]['Customer']._sample(t), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            samples.append(round(N2.simulation.service_times[N2.id_number]['Customer']._sample(t), 2))
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
            samples.append(round(N1.simulation.inter_arrival_times[N1.id_number]['Customer']._sample(t), 2))
        expected = [3.0, 3.0, 3.0, 5.0, 5.0]
        self.assertEqual(samples, expected)

        samples = []
        for t in [4.0, 4.0, 17.0, 22.0, 22.0]:
            samples.append(round(N2.simulation.inter_arrival_times[N2.id_number]['Customer']._sample(t), 2))
        expected = [2.0, 2.0, 8.5, 8.0, 8.0]
        self.assertEqual(samples, expected)

    def test_broken_dist_object(self):
        B = BrokenDist()
        ciw.seed(5)
        self.assertRaises(ValueError, B._sample)

    def test_timedependent_exact(self):
        N = ciw.create_network(
            arrival_distributions=[TimeDependentDist1(), TimeDependentDist2()],
            service_distributions=[TimeDependentDist1(), TimeDependentDist2()],
            number_of_servers=[1, 1],
            routing=[[0.1, 0.1], [0.1, 0.1]],
        )
        Q = ciw.Simulation(N, exact=26)
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
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.2, 0.4, 0.6, 0.8])],
            service_distributions=[ciw.dists.Sequential([0.9, 0.7, 0.5, 0.3, 0.1])],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Ns = Q.transitive_nodes[0]

        samples = [
            round(Ns.simulation.service_times[Ns.id_number]['Customer']._sample(), 2)
            for _ in range(7)
        ]
        expected = [0.9, 0.7, 0.5, 0.3, 0.1, 0.9, 0.7]
        self.assertEqual(samples, expected)

        # First arrival will be offset by 1, as first customer's inter-arrival
        # time has already been sampled by the arrival node
        samples = [
            round(Ns.simulation.inter_arrival_times[Ns.id_number]['Customer']._sample(), 2)
            for _ in range(6)
        ]
        expected = [0.4, 0.6, 0.8, 0.2, 0.4, 0.6]
        self.assertEqual(samples, expected)

    @given(
        dist1=lists(floats(min_value=0.001, max_value=10000), min_size=1, max_size=20),
        dist2=lists(floats(min_value=0.001, max_value=10000), min_size=1, max_size=20),
    )
    def test_sampling_sequential_dist_hypothesis(self, dist1, dist2):
        sequential_dist_1 = dist1
        sequential_dist_2 = dist2
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential(sequential_dist_1)],
            service_distributions=[ciw.dists.Sequential(sequential_dist_2)],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Ns = Q.transitive_nodes[0]

        len1 = len(sequential_dist_1)
        len2 = len(sequential_dist_2)

        expected_inter_arrival_times = (
            3 * sequential_dist_1 + sequential_dist_1[:1]
        )
        expected_service_times = 3 * sequential_dist_2

        inter_arrivals = [
            Ns.simulation.inter_arrival_times[Ns.id_number]['Customer']._sample()
            for _ in range(3 * len1)
        ]
        services = [
            Ns.simulation.service_times[Ns.id_number]['Customer']._sample()
            for _ in range(3 * len2)
        ]
        self.assertEqual(inter_arrivals, expected_inter_arrival_times[1:])
        self.assertEqual(services, expected_service_times)

    def test_sequential_summary_stats(self):
        values = [0.9, 0.7, 0.5, 0.3, 0.1]
        S = ciw.dists.Sequential(values)
        expected_mean = sum(values) / len(values)
        self.assertEqual(S.mean, expected_mean)
        expected_variance = sum((x - expected_mean) ** 2 for x in values) / len(values)
        self.assertEqual(S.variance, expected_variance)
        self.assertEqual(S.sd, math.sqrt(S.variance))
        self.assertEqual(S.median, 0.5)
        self.assertEqual(S.upper_limit, 0.9)
        self.assertEqual(S.lower_limit, 0.1)

        values = [0.7, 0.5, 0.3, 0.1]
        S = ciw.dists.Sequential(values)
        expected_mean = sum(values) / len(values)
        self.assertEqual(S.mean, expected_mean)
        expected_variance = sum((x - expected_mean) ** 2 for x in values) / len(values)
        self.assertEqual(S.variance, expected_variance)
        self.assertEqual(S.sd, math.sqrt(S.variance))
        self.assertEqual(S.median, 0.4)
        self.assertEqual(S.upper_limit, 0.7)
        self.assertEqual(S.lower_limit, 0.1)


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
        self.assertEqual(str(Dt_plus_Sq), "CombinedDistribution")
        self.assertEqual(str(Dt_plus_Ex), "CombinedDistribution")
        self.assertEqual(str(Sq_plus_Ex), "CombinedDistribution")
        self.assertEqual(str(Dt_plus_Sq_plus_Ex), "CombinedDistribution")
        self.assertEqual(str(Dt_minus_Sq), "CombinedDistribution")
        self.assertEqual(str(Dt_minus_Ex), "CombinedDistribution")
        self.assertEqual(str(Dt_mult_Sq), "CombinedDistribution")
        self.assertEqual(str(Dt_mult_Ex), "CombinedDistribution")
        self.assertEqual(str(Sq_mult_Ex), "CombinedDistribution")
        self.assertEqual(str(Dt_div_Sq), "CombinedDistribution")
        self.assertEqual(str(Dt_div_Ex), "CombinedDistribution")
        self.assertEqual(str(Sq_div_Dt), "CombinedDistribution")
        self.assertEqual(str(Sq_div_Ex), "CombinedDistribution")
        self.assertEqual(str(Ex_div_Dt), "CombinedDistribution")
        self.assertEqual(str(Ex_div_Sq), "CombinedDistribution")

    def test_combined_add_summary_stats(self):
        # A: N(5, sd=1) -> mean=5, var=1
        # B: N(2, sd=0.5) -> mean=2, var=0.25
        A = ciw.dists.Normal(5.0, 1.0)
        B = ciw.dists.Normal(2.0, 0.5)

        C = A + B
        expected_mean = A.mean + B.mean                     # 5 + 2 = 7
        expected_var  = A.variance + B.variance             # 1 + 0.25 = 1.25
        self.assertEqual(C.mean, expected_mean)
        self.assertEqual(C.variance, expected_var)
        self.assertEqual(C.upper_limit, float('inf'))
        self.assertEqual(C.lower_limit, 0)

    def test_combined_sub_summary_stats(self):
        A = ciw.dists.Normal(5.0, 1.0)
        B = ciw.dists.Normal(2.0, 0.5)

        C = A - B
        expected_mean = A.mean - B.mean                     # 5 - 2 = 3
        expected_var  = A.variance + B.variance             # 1 + 0.25 = 1.25
        self.assertEqual(C.mean, expected_mean)
        self.assertEqual(C.variance, expected_var)
        self.assertTrue(math.isnan(C.upper_limit))
        self.assertTrue(math.isnan(C.lower_limit))

    def test_combined_mul_summary_stats(self):
        # Product moments (independent):
        # E[AB] = mA mB
        # Var(AB) = vA vB + mB^2 vA + mA^2 vB
        A = ciw.dists.Normal(5.0, 1.0)    # mA=5, vA=1
        B = ciw.dists.Normal(2.0, 0.5)    # mB=2, vB=0.25

        C = A * B
        expected_mean = A.mean * B.mean                   # 10
        expected_var  = (
            A.variance * B.variance                      # 1 * 0.25 = 0.25
            + (B.mean ** 2) * A.variance                 # 4 * 1 = 4
            + (A.mean ** 2) * B.variance                 # 25 * 0.25 = 6.25
        )                                                # total = 10.5
        self.assertEqual(C.mean, expected_mean)
        self.assertEqual(C.variance, expected_var)

    def test_combined_div_summary_stats(self):
        # Division uses the delta-method approximation implemented in your properties:
        # E[A/B] = mA / mB
        # Var(A/B) = vA / mB^2 + (mA^2 * vB) / mB^4   (requires mB != 0)
        A = ciw.dists.Normal(5.0, 1.0)    # mA=5, vA=1
        B = ciw.dists.Normal(2.0, 0.5)    # mB=2, vB=0.25

        C = A / B
        expected_mean = A.mean / B.mean  # 2.5
        expected_var  = (
            A.variance / (B.mean ** 2)  # 1 / 4 = 0.25
            + (A.mean ** 2) * B.variance / (B.mean ** 4) # 25 * 0.25 / 16 = 0.390625
        ) # total = 0.640625
        self.assertEqual(C.mean, expected_mean)
        self.assertEqual(C.variance, expected_var)

    def test_combined_div_by_zero(self):
        A = ciw.dists.Normal(5, 1)
        B = ciw.dists.Deterministic(0)
        C = A / B
        self.assertTrue(math.isnan(C.mean))

    def test_mixture_distributions(self):
        ciw.seed(0)
        D1 = ciw.dists.Deterministic(1.0)
        D5 = ciw.dists.Deterministic(5.0)
        D8 = ciw.dists.Deterministic(8.0)

        Mixted_100 = ciw.dists.MixtureDistribution(dists=[D1, D5, D8], probs=[1, 0, 0])
        m100_samples = [Mixted_100.sample() for _ in range(10)]
        m100_expected = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.assertEqual(str(Mixted_100), 'MixtureDistribution')
        self.assertEqual(m100_samples, m100_expected)

        Mixted_010 = ciw.dists.MixtureDistribution(dists=[D1, D5, D8], probs=[0, 1, 0])
        m010_samples = [Mixted_010.sample() for _ in range(10)]
        m010_expected = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
        self.assertEqual(str(Mixted_010), 'MixtureDistribution')
        self.assertEqual(m010_samples, m010_expected)

        Mixted_001 = ciw.dists.MixtureDistribution(dists=[D1, D5, D8], probs=[0, 0, 1])
        m001_samples = [Mixted_001.sample() for _ in range(10)]
        m001_expected = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
        self.assertEqual(str(Mixted_001), 'MixtureDistribution')
        self.assertEqual(m001_samples, m001_expected)

        Mixted_eq = ciw.dists.MixtureDistribution(dists=[D1, D5, D8], probs=[1/3, 1/3, 1/3])
        meq_samples = [Mixted_eq.sample() for _ in range(10)]
        meq_expected = [5, 8, 1, 8, 5, 1, 8, 5, 8, 8]
        self.assertEqual(str(Mixted_eq), 'MixtureDistribution')
        self.assertEqual(meq_samples, meq_expected)

    def test_mixture_summary_stats(self):
        c1 = ciw.dists.Normal(0.0, 1.0)  
        c2 = ciw.dists.Normal(3.0, 2.0)  
        probs = [0.6, 0.4]
        M = ciw.dists.MixtureDistribution([c1, c2], probs)

        expected_mean = probs[0] * c1.mean + probs[1] * c2.mean
        self.assertEqual(M.mean, expected_mean)
        expected_variance = (
            probs[0] * (c1.variance + c1.mean ** 2) +
            probs[1] * (c2.variance + c2.mean ** 2)
        ) - expected_mean ** 2
        self.assertEqual(M.variance, expected_variance)

        D = ciw.dists.Deterministic(3.0)
        U = ciw.dists.Uniform(2.0, 4.0)
        M = ciw.dists.MixtureDistribution([D, U], [0.5, 0.5])
        self.assertEqual(M.sd, math.sqrt(M.variance))
        self.assertTrue(math.isnan(M.median))
        self.assertTrue(M.upper_limit, 4.0)
        self.assertTrue(M.lower_limit, 2.0)

    def test_state_dependent_distribution(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(4)],
            service_distributions=[StateDependent()],
            number_of_servers=[1],
        )
        ciw.seed(0)
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(500)
        recs = Q.get_all_records()

        # Only samples 0.2, 0.15, 0.1, 0.05, or 0.0
        services = [round(r.service_time, 7) for r in recs if r.arrival_date > 100]
        self.assertLessEqual(set(services), {0.2, 0.15, 0.1, 0.05, 0.0})

        # Check average service time correct transformation of average queue size
        average_queue_size = sum(
            s * p for s, p in Q.statetracker.state_probabilities().items()
        )
        self.assertEqual(round(average_queue_size, 7), 0.9468383)
        self.assertEqual(round((-0.05 * average_queue_size) + 0.2, 7), 0.1526581)
        self.assertEqual(round(sum(services) / len(services), 7), 0.1529728)

    def test_phasetype_dist_object(self):
        initial_state = [0.3, 0.7, 0.0]
        absorbing_matrix = [[-5, 3, 2], [0, -4, 4], [0, 0, 0]]
        Ph = ciw.dists.PhaseType(initial_state, absorbing_matrix)
        ciw.seed(5)
        samples = [round(Ph._sample(), 2) for _ in range(10)]
        expected = [0.34, 0.71, 0.64, 0.47, 0.03, 0.07, 0.21, 0.7, 0.04, 0.04]
        self.assertEqual(samples, expected)
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            [-0.3, 0.7, 0.0],
            absorbing_matrix
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            [1.3, 0.7, 0.0],
            absorbing_matrix
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            [0.3, 0.9, 0.0],
            absorbing_matrix
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            initial_state,
            [[-3, 3], [7, -10, 3]]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            initial_state,
            [[-3, 3], [7, -7]]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            initial_state,
            [[-3, 3], [7, -7]]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            initial_state,
            [[-3, -3, 0], [1, -9, 8], [0, 0, 0]],
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            initial_state,
            [[-3, 3, 0], [3, -9, 8], [0, 0, 0]],
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            initial_state,
            [[-5, 5, 0], [4, -4, 0], [0, 0, 0]],
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PhaseType,
            initial_state,
            [[-5, 3, 2], [0, -4, 4], [0, 1, -1]],
        )

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
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        self.assertEqual(Er.initial_state, expected_vector)
        self.assertEqual(Er.absorbing_matrix, expected_matrix)
        self.assertRaises(ValueError, ciw.dists.Erlang, -4, 2)
        self.assertRaises(ValueError, ciw.dists.Erlang, 4, -2)
        self.assertRaises(ValueError, ciw.dists.Erlang, -4, -2)

        many_samples = [round(Er.sample(), 4) for _ in range(1000)]
        # We would expect this to be  `num_phases` / `rate` = 7 / 5 = 1.4
        self.assertEqual(round(sum(many_samples) / 1000, 4), 1.4057)

    def test_phasetype_summary_stats(self):
        initial_state = [0.3, 0.7, 0.0]
        absorbing_matrix = [
            [-5, 3, 2],
            [0, -4, 4],
            [0, 0, 0]
        ]
        Ph = ciw.dists.PhaseType(initial_state, absorbing_matrix)
        # Extract transient generator Q and initial vector alpha
        Q = np.array(absorbing_matrix)[:-1, :-1]        # Top-left 2x2 submatrix
        alpha = np.array(initial_state[:-1])            # First 2 entries
        invQ = np.linalg.inv(-Q)
        ones = np.ones(len(Q))

        # First moment: E[T] = Î± (-Q)^-1 1
        expected_mean = float(alpha @ invQ @ ones)

        # Second moment: E[T^2] = 2 Î± (-Q)^-2 1
        expected_second_moment = float(2 * alpha @ invQ @ invQ @ ones)

        # Variance: Var(T) = E[T^2] - (E[T])^2
        expected_variance = expected_second_moment - expected_mean ** 2

        # Assertions
        self.assertEqual(Ph.mean, expected_mean)
        self.assertEqual(Ph.variance, expected_variance)

    def test_sampling_erlang_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Erlang(5, 7)],
            service_distributions=[ciw.dists.Erlang(5, 7)],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nn.simulation.service_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [2.07, 1.21, 1.28, 1.75, 2.56]
        self.assertEqual(samples, expected)

        samples = [
            round(Nn.simulation.inter_arrival_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.5, 1.06, 1.72, 1.17, 1.49]
        self.assertEqual(samples, expected)

    @given(
        sizes=integers(min_value=1, max_value=10),
        rates=floats(min_value=0.1, max_value=20),
        rm=random_module(),
    )
    def test_sampling_erlang_dist_hypothesis(self, sizes, rates, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Erlang(rates, sizes)],
            service_distributions=[ciw.dists.Erlang(rates, sizes)],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Nw = Q.transitive_nodes[0]
        for itr in range(10):  # Because repition happens in the simulation
            self.assertTrue(Nw.simulation.service_times[Nw.id_number]['Customer']._sample() >= 0.0)
            self.assertTrue(Nw.simulation.inter_arrival_times[Nw.id_number]['Customer']._sample() >= 0.0)

    def test_erlang_summary_stats(self):
        rate = 5.0
        k = 7
        Er = ciw.dists.Erlang(rate, k)
        expected_mean = k / rate
        expected_variance = k / (rate ** 2)
        self.assertEqual(Er.mean, expected_mean)
        self.assertEqual(Er.variance, expected_variance)
        self.assertTrue(math.isnan(Er.median))
        self.assertEqual(Er.lower_limit, 0)
        self.assertEqual(Er.upper_limit, float('inf'))

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
            [0, 0, 0, 0, 0],
        ]
        self.assertEqual(Hx.initial_state, expected_vector)
        self.assertEqual(Hx.absorbing_matrix, expected_matrix)

        self.assertRaises(
            ValueError,
            ciw.dists.HyperExponential,
            [5, -7, -2, 1],
            [0.4, 0.1, 0.3, 0.2]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.HyperExponential,
            [5, 7, 2, 1],
            [0.4, 5.1, 0.3, 0.2]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.HyperExponential,
            [5, 7, 2, 1],
            [0.4, -0.1, 0.3, 0.2]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.HyperExponential,
            [5, 7, 2, 1],
            [0.4, 0.8, 0.3, 0.2]
        )

        many_samples = [round(Hx.sample(), 2) for _ in range(1000)]
        # We would expect this to be sum of the element-wise division of probabilities and rates:
        # (0.4 / 5) + (0.1 / 7) + (0.3 / 2) + (0.2 / 1) = 0.4442857142857143
        self.assertEqual(round(sum(many_samples) / 1000, 4), 0.416)

    def test_sampling_hyperexponential_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.HyperExponential([5, 7, 2, 1], [0.4, 0.1, 0.3, 0.2])],
            service_distributions=[ciw.dists.HyperExponential([5, 7, 2, 1], [0.4, 0.1, 0.3, 0.2])],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nn.simulation.service_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.68, 1.43, 1.28, 0.13, 1.05]
        self.assertEqual(samples, expected)

        samples = [
            round(Nn.simulation.inter_arrival_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.12, 0.04, 0.43, 0.05, 0.5]
        self.assertEqual(samples, expected)

    def test_hyperexponential_summary_stats(self):
        rates = [5, 2, 10]
        probs = [0.3, 0.5, 0.2]
        Hx = ciw.dists.HyperExponential(rates, probs)

        expected_mean = sum(p / r for p, r in zip(probs, rates))
        expected_variance = sum(2 * p / (r ** 2) for p, r in zip(probs, rates)) - expected_mean ** 2

        self.assertEqual(Hx.mean, expected_mean)
        self.assertEqual(Hx.variance, expected_variance)
        self.assertTrue(math.isnan(Hx.median))
        self.assertEqual(Hx.lower_limit, 0)
        self.assertEqual(Hx.upper_limit, float('inf'))

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
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        self.assertEqual(Hg.initial_state, expected_vector)
        self.assertEqual(Hg.absorbing_matrix, expected_matrix)

        self.assertRaises(
            ValueError,
            ciw.dists.HyperErlang,
            [5, -7, 2],
            [0.5, 0.3, 0.2],
            [3, 2, 5]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.HyperErlang,
            [5, 7, 2],
            [-0.5, 0.3, 0.2],
            [3, 2, 5]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.HyperErlang,
            [5, 7, 2],
            [0.5, 1.3, 0.2],
            [3, 2, 5]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.HyperErlang,
            [5, 7, 2],
            [0.5, 0.9, 0.2],
            [3, 2, 5]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.HyperErlang,
            [5, 7, 2],
            [0.5, 0.3, 0.2],
            [0, 2, 5]
        )

        many_samples = [round(Hg.sample(), 2) for _ in range(1000)]
        # We would expect this to be sum of the element-wise multiplication of probabilities, inverse rates, and subphase lengths:
        # (0.5 * 3 / 5) + (0.3 * 2 / 7) + (0.2 * 5 / 2) = 0.8857142857142857
        self.assertEqual(round(sum(many_samples) / 1000, 4), 0.8744)

    def test_sampling_hypererlang_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.HyperErlang([5, 7, 2], [0.5, 0.3, 0.2], [3, 2, 5])],
            service_distributions=[ciw.dists.HyperErlang([5, 7, 2], [0.5, 0.3, 0.2], [3, 2, 5])],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nn.simulation.service_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.42, 3.71, 0.35, 0.38, 0.61]

        self.assertEqual(samples, expected)

        samples = [
            round(Nn.simulation.inter_arrival_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [0.25, 0.22, 3.46, 3.07, 1.69]
        self.assertEqual(samples, expected)

    def test_hypererlang_summary_stats(self):
        rates   = [5, 2, 10]
        probs   = [0.3, 0.5, 0.2]
        lengths = [3, 2, 4]   # k_i (number of Erlang phases per branch)
        He = ciw.dists.HyperErlang(rates=rates, probs=probs, phase_lengths=lengths)
        expected_mean = sum(p * k / r for p, r, k in zip(probs, rates, lengths))
        expected_second_moment = sum(
            p * (k * (k + 1)) / (r ** 2) for p, r, k in zip(probs, rates, lengths)
        )
        expected_variance = expected_second_moment - expected_mean ** 2
        self.assertEqual(He.mean, expected_mean)
        self.assertEqual(He.variance, expected_variance)
        self.assertTrue(math.isnan(He.median))
        self.assertEqual(He.lower_limit, 0)
        self.assertEqual(He.upper_limit, float('inf'))



    def test_coxian_dist_object(self):
        Cx = ciw.dists.Coxian([5, 4, 7, 2], [0.2, 0.5, 0.3, 1.0])
        ciw.seed(5)
        samples = [round(Cx._sample(), 2) for _ in range(10)]
        expected = [1.01, 0.53, 0.18, 0.17, 0.04, 1.09, 0.77, 0.81, 0.08, 0.43]
        self.assertEqual(samples, expected)
        expected_vector = [1.0, 0.0, 0.0, 0.0, 0.0]
        expected_matrix = [
            [-5, (0.8) * 5, 0, 0, (0.2) * 5],
            [0, -4, (0.5) * 4, 0, (0.5) * 4],
            [0, 0, -7, (0.7) * 7, (0.3) * 7],
            [0, 0, 0, -2, 2],
            [0, 0, 0, 0, 0],
        ]
        self.assertEqual(Cx.initial_state, expected_vector)
        self.assertEqual(Cx.absorbing_matrix, expected_matrix)

        self.assertRaises(
            ValueError,
            ciw.dists.Coxian,
            [5, -4, 7, 2],
            [0.2, 0.5, 0.3, 1.0]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.Coxian,
            [5, 4, 7, 2],
            [0.2, -0.5, 0.3, 1.0]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.Coxian,
            [5, 4, 7, 2],
            [0.2, 1.5, 0.3, 1.0]
        )
        self.assertRaises(
            ValueError,
            ciw.dists.Coxian,
            [5, 4, 7, 2],
            [0.2, 0.5, 0.3, 0.6]
        )

        many_samples = [round(Cx.sample(), 2) for _ in range(1000)]
        # We would expect this to be expected time to absorption of the underlying absobring Markov chain.
        # We can calculate this using Numpy:
        # >>> (np.linalg.inv(np.eye(4) - (np.matrix(absorbing_matrix) / 7 + np.eye(5))[:-1, :-1]) @ np.ones(4))[0, 0] / 7
        # 0.5971428571428571
        self.assertEqual(round(sum(many_samples) / 1000, 4), 0.6035)

    def test_sampling_coxian_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Coxian([5, 4, 7, 2], [0.2, 0.5, 0.3, 1.0])],
            service_distributions=[ciw.dists.Coxian([5, 4, 7, 2], [0.2, 0.5, 0.3, 1.0])],
            number_of_servers=[1],
            routing=[[0.1]],
        )
        Q = ciw.Simulation(N)
        Nn = Q.transitive_nodes[0]
        ciw.seed(5)

        samples = [
            round(Nn.simulation.service_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [1.01, 0.53, 0.18, 0.17, 0.04]

        self.assertEqual(samples, expected)

        samples = [
            round(Nn.simulation.inter_arrival_times[Nn.id_number]['Customer']._sample(), 2)
            for _ in range(5)
        ]
        expected = [1.09, 0.77, 0.81, 0.08, 0.43]
        self.assertEqual(samples, expected)

    def test_coxian_summary_stats(self):
        rates = [5, 4, 7, 2]
        probs = [0.2, 0.5, 0.3, 1.0]  # Prob of absorbing at each phase
        Cx = ciw.dists.Coxian(rates, probs)

        # Recompute mean and variance using matrix-based method
    
        Q = np.array(Cx.absorbing_matrix)[:-1, :-1]
        alpha = np.array(Cx.initial_state[:-1])
        ones = np.ones(len(Q))
        invQ = np.linalg.inv(-Q)

        expected_mean = float(alpha @ invQ @ ones)
        second_moment = float(2 * alpha @ invQ @ invQ @ ones)
        expected_variance = second_moment - expected_mean ** 2

        self.assertEqual(Cx.mean, expected_mean)
        self.assertEqual(Cx.variance, expected_variance)
        self.assertTrue(math.isnan(Cx.median))
        self.assertEqual(Cx.lower_limit, 0)
        self.assertEqual(Cx.upper_limit, float('inf'))

    def test_poissoninterval_dist_object(self):
        ciw.seed(5)
        Pi = ciw.dists.PoissonIntervals(
            rates=[5, 1.5, 3], endpoints=[3.2, 7.9, 10], max_sample_date=15
        )
        samples = [round(Pi._sample(), 4) for _ in range(10)]
        expected = [0.0928, 0.2694, 0.4268, 0.701, 0.011, 0.239, 0.0966, 0.1567, 0.0834, 0.291,]
        self.assertEqual(samples, expected)

        expected_dates = [0]
        for t in Pi.inter_arrivals:
            expected_dates.append(expected_dates[-1] + t)
        self.assertEqual(Pi.dates, expected_dates[:-1])
        self.assertLessEqual(Pi.dates[-1], Pi.max_sample_date)

        self.assertRaises(
            ValueError,
            ciw.dists.PoissonIntervals,
            [5, -1.5, 3],
            [3.2, 7.9, 10],
            15
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PoissonIntervals,
            [5, 1.5, 3],
            [3.2, 1.9, 10],
            15
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PoissonIntervals,
            [5, 1.5, 3],
            [-3.2, 7.9, 10],
            15
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PoissonIntervals,
            [5, 1.5, 3],
            [3.2, 7.9, 10],
            -15
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PoissonIntervals,
            [5, 1.5, 3],
            [3.2, 7.9, 10],
            0
        )
        self.assertRaises(
            ValueError,
            ciw.dists.PoissonIntervals,
            [5, 1.5, 3, 6],
            [3.2, 7.9, 10],
            15
        )

    def test_poissoninterval_rate_zero(self):
        ciw.seed(5)
        Pi = ciw.dists.PoissonIntervals(
            rates=[10, 0], endpoints=[1, 2], max_sample_date=15.5
        )
        arrivals_when_rate_is_zero = [date for date in Pi.dates if int(date) % 2 == 1]
        self.assertEqual(arrivals_when_rate_is_zero, [])
        final_date = Pi.dates[-1]
        self.assertTrue(final_date < 15)

        ciw.seed(5)
        Pi = ciw.dists.PoissonIntervals(
            rates=[0, 0], endpoints=[1, 2], max_sample_date=15.5
        )
        arrivals_when_rate_is_zero = [date for date in Pi.dates if int(date) % 2 == 1]
        self.assertEqual(arrivals_when_rate_is_zero, [])
        self.assertEqual(Pi.sample(), float("inf"))

        ciw.seed(5)
        Pi = ciw.dists.PoissonIntervals(
            rates=[3, 2, 0], endpoints=[1, 2, 10], max_sample_date=9
        )
        final_date = Pi.dates[-1]
        self.assertTrue(final_date < 2)
        
        t = 0
        arrivals = []
        while t < 8:
            t += Pi.sample()
            arrivals.append(t)
        final_sample = arrivals[-1]
        final_arrival = arrivals[-2]
        self.assertEqual(final_sample, float('inf'))
        self.assertEqual(final_arrival, final_date)

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
                max_sample_date=20
            ) for _ in range(n)
        ]
        counts = {
            (0, 3.2): sum(
                [
                    sum(
                        [
                            ((r > 0) and (r < 3.2)) or ((r > 10) and (r < 13.2))
                            for r in Pi.dates
                        ]
                    )
                    for Pi in distributions
                ]
            )
            / n,
            (3.2, 7.9): sum(
                [
                    sum(
                        [
                            ((r > 3.2) and (r < 7.9)) or ((r > 13.2) and (r < 17.9))
                            for r in Pi.dates
                        ]
                    )
                    for Pi in distributions
                ]
            )
            / n,
            (7.9, 10): sum(
                [
                    sum(
                        [
                            ((r > 7.9) and (r < 10)) or ((r > 17.9) and (r < 20))
                            for r in Pi.dates
                        ]
                    )
                    for Pi in distributions
                ]
            )
            / n,
        }
        self.assertEqual(counts[(0, 3.2)], 31.756)  ## expected 32
        self.assertEqual(counts[(3.2, 7.9)], 14.184)  ## expected 14.1
        self.assertEqual(counts[(7.9, 10)], 12.748)  ## expected 12.6

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
                max_sample_date=100,
            )
            for _ in range(n)
        ]
        counts = {
            (0, 0.5): sum(
                [
                    sum(
                        [
                            ((r > 0) and (r < 0.5)) or ((r > 50) and (r < 50.5))
                            for r in Pi.dates
                        ]
                    )
                    for Pi in distributions
                ]
            )
            / n,
            (0.5, 10): sum(
                [
                    sum(
                        [
                            ((r > 0.5) and (r < 10)) or ((r > 50.5) and (r < 60))
                            for r in Pi.dates
                        ]
                    )
                    for Pi in distributions
                ]
            )
            / n,
            (10, 32): sum(
                [
                    sum(
                        [
                            ((r > 10) and (r < 32)) or ((r > 60) and (r < 82))
                            for r in Pi.dates
                        ]
                    )
                    for Pi in distributions
                ]
            )
            / n,
            (32, 40.3): sum(
                [
                    sum(
                        [
                            ((r > 32) and (r < 40.3)) or ((r > 82) and (r < 90.3))
                            for r in Pi.dates
                        ]
                    )
                    for Pi in distributions
                ]
            )
            / n,
            (40.3, 50): sum(
                [
                    sum(
                        [
                            ((r > 40.3) and (r < 50)) or ((r > 90.3) and (r < 100))
                            for r in Pi.dates
                        ]
                    )
                    for Pi in distributions
                ]
            )
            / n,
        }
        self.assertEqual(counts[(0, 0.5)], 2.016)  ## expected 2
        self.assertEqual(counts[(0.5, 10)], 11.4)  ## expected 11.4
        self.assertEqual(counts[(10, 32)], 35.324)  ## expected 35.2
        self.assertEqual(counts[(32, 40.3)], 198.968)  ## expected 199.2
        self.assertEqual(counts[(40.3, 50)], 58.12)  ## expected 58.2

    def test_sampling_poissoninterval_dist(self):
        ciw.seed(5)
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.PoissonIntervals(
                rates=[5, 1.5, 3],
                endpoints=[3.2, 7.9, 10],
                max_sample_date=15)],
            service_distributions=[ciw.dists.PoissonIntervals(
                rates=[5, 1.5, 3],
                endpoints=[3.2, 7.9, 10],
                max_sample_date=15)],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Nt = Q.transitive_nodes[0]

        samples = [
            round(Nt.simulation.service_times[Nt.id_number]['Customer']._sample(), 4)
            for _ in range(10)
        ]
        expected = [0.0108, 0.0623, 0.1092, 0.026, 0.2578, 0.0648, 0.4333, 0.0275, 0.0187, 0.0707,]
        self.assertEqual(samples, expected)

        samples = [
            round(Nt.simulation.inter_arrival_times[Nt.id_number]['Customer']._sample(), 4)
            for _ in range(10)
        ]
        expected = [0.2694, 0.4268, 0.701, 0.011, 0.239, 0.0966, 0.1567, 0.0834, 0.291, 0.006,]
        self.assertEqual(samples, expected)

    def test_poisson_dist_object(self):
        Po = ciw.dists.Poisson(1.5)
        ciw.seed(5)
        samples = [Po._sample() for _ in range(10)]
        expected = [3, 0, 1, 0, 0, 2, 4, 2, 1, 1]
        self.assertEqual(samples, expected)
        self.assertRaises(ValueError, ciw.dists.Poisson, -1.5)

    def test_sampling_poisson_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(0)],
            batching_distributions=[ciw.dists.Poisson(1.5)],
            number_of_servers=[1],
        )
        ciw.seed(5)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(10.5)
        recs = Q.get_all_records()

        samples = [len([r for r in recs if r.arrival_date == t]) for t in range(1, 11)]
        expected = [3, 0, 1, 0, 0, 2, 4, 2, 1, 1]
        self.assertEqual(samples, expected)

    def test_poisson_summary_stats(self):
        P = ciw.dists.Poisson(1.5)
        self.assertEqual(P.mean, 1.5)
        self.assertEqual(P.variance, 1.5)
        self.assertEqual(P.sd, math.sqrt(P.variance))
        self.assertEqual(P.median, 1)
        self.assertEqual(P.lower_limit, 0)
        self.assertEqual(P.upper_limit, float("inf"))

    def test_poissonintervals_summary_stats(self):
        Pi = ciw.dists.PoissonIntervals(
            rates=[5, 1.5, 3],
            endpoints=[3.2, 7.9, 10],
            max_sample_date=15
        )
        sd = Pi.sd
        self.assertTrue((sd == sd) or math.isnan(sd))
        self.assertTrue(math.isnan(Pi.median))
        self.assertTrue(math.isinf(Pi.upper_limit))
        self.assertEqual(Pi.lower_limit, 0.0)

    def test_geometric_dist_object(self):
        Ge = ciw.dists.Geometric(0.3)
        ciw.seed(5)
        samples = [Ge._sample() for _ in range(10)]
        expected = [6, 3, 4, 2, 1, 2, 2, 1, 1, 3]
        self.assertEqual(samples, expected)
        self.assertRaises(ValueError, ciw.dists.Geometric, -0.5)
        self.assertRaises(ValueError, ciw.dists.Geometric, 1.4)

    def test_sampling_geometric_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(0)],
            batching_distributions=[ciw.dists.Geometric(0.3)],
            number_of_servers=[1],
        )
        ciw.seed(5)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(10.5)
        recs = Q.get_all_records()

        samples = [len([r for r in recs if r.arrival_date == t]) for t in range(1, 11)]
        expected = [6, 3, 4, 2, 1, 2, 2, 1, 1, 3]
        self.assertEqual(samples, expected)

    def test_geometric_summary_stats(self):
        G = ciw.dists.Geometric(0.3)
        expected_mean = 1 / 0.3
        self.assertEqual(G.mean, expected_mean)
        expected_variance = (1 - 0.3) / (0.3 ** 2)
        self.assertEqual(G.variance, expected_variance)
        self.assertTrue(math.isinf(G.upper_limit))
        self.assertEqual(G.lower_limit, 0)
        self.assertEqual(G.median, 2)

    def test_binomial_dist_object(self):
        Bi = ciw.dists.Binomial(20, 0.4)
        ciw.seed(5)
        samples = [Bi._sample() for _ in range(10)]
        expected = [10, 10, 8, 7, 5, 7, 7, 4, 4, 15]
        self.assertEqual(samples, expected)

        self.assertRaises(ValueError, ciw.dists.Binomial, 20, -0.5)
        self.assertRaises(ValueError, ciw.dists.Binomial, 20, 1.4)
        self.assertRaises(ValueError, ciw.dists.Binomial, -5, 0.2)
        self.assertRaises(ValueError, ciw.dists.Binomial, 13.5, 0.2)

    def test_sampling_binomial_dist(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1)],
            service_distributions=[ciw.dists.Deterministic(0)],
            batching_distributions=[ciw.dists.Binomial(20, 0.4)],
            number_of_servers=[1],
        )
        ciw.seed(5)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(10.5)
        recs = Q.get_all_records()

        samples = [len([r for r in recs if r.arrival_date == t]) for t in range(1, 11)]
        expected = [10, 10, 8, 7, 5, 7, 7, 4, 4, 15]
        self.assertEqual(samples, expected)

    def test_binomial_summary_stats(self):
        B = ciw.dists.Binomial(20, 0.4)
        expected_mean = 20 * 0.4
        self.assertEqual(B.mean, expected_mean)
        expected_variance = 20 * 0.4 * (1 - 0.4)
        self.assertEqual(B.variance, expected_variance)
        self.assertEqual(B.median, 8)
        self.assertEqual(B.lower_limit, 0)
        self.assertTrue(math.isinf(B.upper_limit))

    def test_base_distribution_properties(self):
        """Test base Distribution class default properties"""
        base = ciw.dists.Distribution()
        self.assertTrue(math.isnan(base.mean))
        self.assertTrue(math.isnan(base.variance))
        self.assertTrue(math.isnan(base.upper_limit))
        self.assertTrue(math.isnan(base.lower_limit))

    def test_combined_division_by_zero(self):
        """Test division variance when denominator mean is zero"""
        d1 = ciw.dists.Deterministic(5.0)
        d2 = ciw.dists.Deterministic(0.0)
        combined = d1 / d2
        self.assertTrue(math.isnan(combined.variance))

    def test_mixture_nan_limits(self):
        """Test MixtureDistribution NaN limit handling"""
        class NaNDist(ciw.dists.Distribution):
            @property
            def upper_limit(self): 
                return float('nan')
            @property
            def lower_limit(self): 
                return float('nan')
        
        mixture = ciw.dists.MixtureDistribution([NaNDist(), ciw.dists.Deterministic(1)], [0.5, 0.5])
        self.assertTrue(math.isnan(mixture.median))
        self.assertTrue(math.isnan(mixture.upper_limit))
        self.assertTrue(math.isnan(mixture.lower_limit))

    def test_comparing_theoretical_to_observed(self):
        ciw.seed(0)
        Un = ciw.dists.Uniform(0.41, 2.75)
        Dt = ciw.dists.Deterministic(1.1)
        Tr = ciw.dists.Triangular(1.1, 2.2, 3.3)
        Ex = ciw.dists.Exponential(0.8)
        Ga = ciw.dists.Gamma(3.1, 0.2)
        No = ciw.dists.Normal(50.5, 2.6)
        No_trunc = ciw.dists.Normal(1, 2)
        Ln = ciw.dists.Lognormal(0.35, 0.16)
        Wb = ciw.dists.Weibull(88.6, 99.1)
        Em = ciw.dists.Empirical([3.3, 3.3, 4.4, 3.3, 4.4])
        Sq = ciw.dists.Sequential([3.3, 3.3, 4.4, 3.3, 4.4])
        Pf = ciw.dists.Pmf([1.1, 2.2, 3.3], [0.31, 0.21, 0.48])
        Ph = ciw.dists.PhaseType([1, 0, 0], [[-3, 2, 1], [1, -5, 4], [0, 0, 0]])
        Er = ciw.dists.Erlang(4.5, 8)
        Hx = ciw.dists.HyperExponential([7, 12, 5], [0.3, 0.1, 0.6])
        He = ciw.dists.HyperErlang([8, 15, 9], [0.3, 0.1, 0.6], [2, 2, 7])
        Cx = ciw.dists.Coxian([4, 7, 2], [0.3, 0.2, 1.0])
        Pi = ciw.dists.PoissonIntervals(rates=[10, 4.5, 7], endpoints=[3.2, 7.9, 10], max_sample_date=4000)
        Po = ciw.dists.Poisson(rate=0.6)
        Ge = ciw.dists.Geometric(prob=0.49)
        Bi = ciw.dists.Binomial(n=12, prob=0.8)

        params_set = [
            (Un, 10000, 2),
            (Dt, 500, 5),
            (Tr, 10000, 2),
            (Ex, 15000, 1),
            (Ga, 10000, 1),
            (No, 10000, 1),
            (No_trunc, 10000, 1),
            (Ln, 10000, 2),
            (Wb, 10000, 1),
            (Em, 10000, 2),
            (Sq, 10000, 2),
            (Pf, 10000, 1),
            (Ph, 10000, 2),
            (Er, 10000, 1),
            (Hx, 13000, 2),
            (He, 12000, 2),
            (Cx, 15000, 2),
            (Pi, 15000, 2),
            (Po, 20000, 2),
            (Ge, 17000, 1),
            (Bi, 10000, 1)
        ]
        for params in tqdm.tqdm(params_set):
            ciw.seed(0)
            D, n, places = params
            compare_theoretical_to_observed(D=D, n=n, places=places, self=self)
