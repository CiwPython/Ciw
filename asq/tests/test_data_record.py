import unittest
import asq

class TestDataRecord(unittest.TestCase):

    def test_init_method(self):
        r = asq.DataRecord(2, 3, 2, 8, 1, 2)
        self.assertEqual(r.arrival_date, 2)
        self.assertEqual(r.wait, 0)
        self.assertEqual(r.service_start_date, 2)
        self.assertEqual(r.service_time, 3)
        self.assertEqual(r.service_end_date, 5)
        self.assertEqual(r.blocked, 3)
        self.assertEqual(r.exit_date, 8)
        self.assertEqual(r.node, 1)
        self.assertEqual(r.customer_class, 2)

        r = asq.DataRecord(5.7, 2.1, 8.2, 10.3, 1, 3)
        self.assertEqual(r.arrival_date, 5.7)
        self.assertEqual(round(r.wait, 1), 2.5)
        self.assertEqual(r.service_start_date, 8.2)
        self.assertEqual(r.service_time, 2.1)
        self.assertEqual(round(r.service_end_date, 1), 10.3)
        self.assertEqual(round(r.blocked, 1), 0.0)
        self.assertEqual(r.exit_date, 10.3)
        self.assertEqual(r.node, 1)
        self.assertEqual(r.customer_class, 3)