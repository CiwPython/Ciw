import unittest
import ciw
from hypothesis import given
from hypothesis.strategies import floats, integers, lists, random_module


class TestServiceCentre(unittest.TestCase):

    def test_init_method(self):
        number_of_servers = 2
        queueing_capacity = 'Inf'
        class_change_matrix = [[0.2, 0.8],
                               [1.0, 0.0]]
        schedule = None
        SC = ciw.ServiceCentre(number_of_servers,
                               queueing_capacity,
                               class_change_matrix,
                               schedule)
        self.assertEqual(SC.number_of_servers, number_of_servers)
        self.assertEqual(SC.queueing_capacity, queueing_capacity)
        self.assertEqual(SC.class_change_matrix, class_change_matrix)
        self.assertEqual(SC.schedule, schedule)

    @given(number_of_servers=integers(min_value=1),
           queueing_capacity=integers(min_value=0),
           class_change_prob1=floats(min_value=0.0, max_value=1.0),
           class_change_prob2=floats(min_value=0.0, max_value=1.0))
    def test_init_method_h(self, number_of_servers, queueing_capacity, class_change_prob1, class_change_prob2):
        class_change_matrix = [[class_change_prob1, 1 - class_change_prob1],
                               [class_change_prob2, 1 - class_change_prob2]]
        schedule = None
        SC = ciw.ServiceCentre(number_of_servers,
                               queueing_capacity,
                               class_change_matrix,
                               schedule)
        self.assertEqual(SC.number_of_servers, number_of_servers)
        self.assertEqual(SC.queueing_capacity, queueing_capacity)
        self.assertEqual(SC.class_change_matrix, class_change_matrix)
        self.assertEqual(SC.schedule, schedule)


class TestCustomerClass(unittest.TestCase):

    def test_init_method(self):
        arrival_distributions = [["Uniform", 4.0, 9.0],
                                 ["Exponential", 5],
                                 ["Gamma", 0.6, 1.2]]
        service_distributions = [["Gamma", 4.0, 9.0],
                                 ["Uniform", 0.6, 1.2],
                                 ["Exponential", 5]]
        transition_matrix = [[.2, .6, .2], [0, 0, 0], [.5, 0, 0]]

        CC = ciw.CustomerClass(arrival_distributions,
                               service_distributions,
                               transition_matrix)
        self.assertEqual(CC.arrival_distributions, arrival_distributions)
        self.assertEqual(CC.service_distributions, service_distributions)
        self.assertEqual(CC.transition_matrix, transition_matrix)
