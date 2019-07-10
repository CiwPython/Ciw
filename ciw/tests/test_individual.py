import unittest
import ciw
from hypothesis import given
from hypothesis.strategies import integers


class TestIndividual(unittest.TestCase):
    def test_init_method_1(self):
        i = ciw.Individual(22, 3)
        self.assertEqual(i.customer_class, 3)
        self.assertEqual(i.previous_class, 3)
        self.assertEqual(i.priority_class, 0)
        self.assertEqual(i.id_number, 22)
        self.assertEqual(i.service_start_date, False)
        self.assertEqual(i.service_time, False)
        self.assertEqual(i.service_end_date, False)
        self.assertEqual(i.arrival_date, False)
        self.assertEqual(i.destination, False)
        self.assertEqual(i.queue_size_at_arrival, False)
        self.assertEqual(i.queue_size_at_departure, False)
        self.assertEqual(i.data_records, [])

    def test_init_method_2(self):
        i = ciw.Individual(5)
        self.assertEqual(i.customer_class, 0)
        self.assertEqual(i.previous_class, 0)
        self.assertEqual(i.priority_class, 0)
        self.assertEqual(i.id_number, 5)
        self.assertEqual(i.service_start_date, False)
        self.assertEqual(i.service_time, False)
        self.assertEqual(i.service_end_date, False)
        self.assertEqual(i.arrival_date, False)
        self.assertEqual(i.destination, False)
        self.assertEqual(i.queue_size_at_arrival, False)
        self.assertEqual(i.queue_size_at_departure, False)
        self.assertEqual(i.data_records, [])

    def test_init_method_3(self):
        i = ciw.Individual(5, 0, 2)
        self.assertEqual(i.customer_class, 0)
        self.assertEqual(i.previous_class, 0)
        self.assertEqual(i.priority_class, 2)
        self.assertEqual(i.id_number, 5)
        self.assertEqual(i.service_start_date, False)
        self.assertEqual(i.service_time, False)
        self.assertEqual(i.service_end_date, False)
        self.assertEqual(i.arrival_date, False)
        self.assertEqual(i.destination, False)
        self.assertEqual(i.queue_size_at_arrival, False)
        self.assertEqual(i.queue_size_at_departure, False)
        self.assertEqual(i.data_records, [])

    def test_repr_method(self):
        i = ciw.Individual(3, 6)
        self.assertEqual(str(i), 'Individual 3')

    @given(id_num = integers(),
           customer_class = integers(),
           priority_class=integers())
    def test_init_method_1h(self, id_num, customer_class, priority_class):
        i = ciw.Individual(id_num, customer_class, priority_class)
        self.assertEqual(i.customer_class, customer_class)
        self.assertEqual(i.previous_class, customer_class)
        self.assertEqual(i.priority_class, priority_class)
        self.assertEqual(i.id_number, id_num)
        self.assertEqual(i.service_start_date, False)
        self.assertEqual(i.service_time, False)
        self.assertEqual(i.service_end_date, False)
        self.assertEqual(i.arrival_date, False)
        self.assertEqual(i.destination, False)
        self.assertEqual(i.queue_size_at_arrival, False)
        self.assertEqual(i.queue_size_at_departure, False)
        self.assertEqual(i.data_records, [])

    @given(id_num = integers())
    def test_init_method_2h(self, id_num):
        i = ciw.Individual(id_num)
        self.assertEqual(i.customer_class, 0)
        self.assertEqual(i.previous_class, 0)
        self.assertEqual(i.priority_class, 0)
        self.assertEqual(i.id_number, id_num)
        self.assertEqual(i.service_start_date, False)
        self.assertEqual(i.service_time, False)
        self.assertEqual(i.service_end_date, False)
        self.assertEqual(i.arrival_date, False)
        self.assertEqual(i.destination, False)
        self.assertEqual(i.queue_size_at_arrival, False)
        self.assertEqual(i.queue_size_at_departure, False)
        self.assertEqual(i.data_records, [])

    @given(id_num = integers(),
           customer_class = integers())
    def test_repr_methodh(self, id_num, customer_class):
        i = ciw.Individual(id_num, customer_class)
        self.assertEqual(str(i), 'Individual ' + str(id_num))
