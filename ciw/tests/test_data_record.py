import unittest
import ciw
from hypothesis import given, assume
from hypothesis.strategies import floats, integers

class TestDataRecord(unittest.TestCase):

    def test_init_method(self):
        r = ciw.DataRecord(2, 3, 2, 8, 1, 2)
        self.assertEqual(r.arrival_date, 2)
        self.assertEqual(r.wait, 0)
        self.assertEqual(r.service_start_date, 2)
        self.assertEqual(r.service_time, 3)
        self.assertEqual(r.service_end_date, 5)
        self.assertEqual(r.blocked, 3)
        self.assertEqual(r.exit_date, 8)
        self.assertEqual(r.node, 1)
        self.assertEqual(r.customer_class, 2)

        r = ciw.DataRecord(5.7, 2.1, 8.2, 10.3, 1, 3)
        self.assertEqual(r.arrival_date, 5.7)
        self.assertEqual(round(r.wait, 1), 2.5)
        self.assertEqual(r.service_start_date, 8.2)
        self.assertEqual(r.service_time, 2.1)
        self.assertEqual(round(r.service_end_date, 1), 10.3)
        self.assertEqual(round(r.blocked, 1), 0.0)
        self.assertEqual(r.exit_date, 10.3)
        self.assertEqual(r.node, 1)
        self.assertEqual(r.customer_class, 3)


    @given(arrival_date=floats(min_value=0.0, max_value=99999.99),
           service_time=floats(min_value=0.0, max_value=99999.99),
           inter_service_start_date=floats(min_value=0.0, max_value=99999.99),
           inter_exit_date=floats(min_value=0.0, max_value=99999.99),
           node=integers(),
           customer_class=integers())
    def test_init_methodh(self,
                          arrival_date,
                          service_time,
                          inter_service_start_date,
                          inter_exit_date,
                          node,
                          customer_class):
        # Define parameters
        service_start_date = arrival_date+inter_service_start_date
        exit_date = service_start_date+inter_exit_date+service_time
        r = ciw.DataRecord(arrival_date, service_time, service_start_date, exit_date, node, customer_class)

        # The tests
        self.assertEqual(r.arrival_date, arrival_date)
        self.assertEqual(r.wait, service_start_date - arrival_date)
        self.assertEqual(r.service_start_date, service_start_date)
        self.assertEqual(r.service_time, service_time)
        self.assertEqual(r.service_end_date, service_start_date + service_time)
        self.assertEqual(r.blocked, exit_date - (service_time + service_start_date))
        self.assertEqual(r.exit_date, exit_date)
        self.assertEqual(r.node, node)
        self.assertEqual(r.customer_class, customer_class)
