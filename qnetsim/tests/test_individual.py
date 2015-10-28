import unittest
import qnetsim

class TestIndividual(unittest.TestCase):

    def test_init_method_1(self):
        i = qnetsim.Individual(22, 3)
        self.assertEqual(i.customer_class, 3)
        self.assertEqual(i.id_number, 22)
        self.assertEqual(i.service_start_date, False)
        self.assertEqual(i.service_time, False)
        self.assertEqual(i.service_end_date, False)
        self.assertEqual(i.arrival_date, False)
        self.assertEqual(i.data_records, {})

    def test_init_method_2(self):
        i = qnetsim.Individual(5)
        self.assertEqual(i.customer_class, 0)
        self.assertEqual(i.id_number, 5)
        self.assertEqual(i.service_start_date, False)
        self.assertEqual(i.service_time, False)
        self.assertEqual(i.service_end_date, False)
        self.assertEqual(i.arrival_date, False)
        self.assertEqual(i.data_records, {})

    def test_repr_method(self):
        i = qnetsim.Individual(3, 6)
        self.assertEqual(str(i), 'Individual 3')