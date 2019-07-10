import unittest
import ciw
from hypothesis import given
from hypothesis.strategies import floats, integers

class TestDataRecord(unittest.TestCase):
    def test_init_method(self):
        r = ciw.DataRecord(2, 2, 1, 2, 0, 2, 3, 5, 3, 8, 1, 0, 3)
        self.assertEqual(r.id_number, 2)
        self.assertEqual(r.customer_class, 2)
        self.assertEqual(r.node, 1)
        self.assertEqual(r.arrival_date, 2)
        self.assertEqual(r.waiting_time, 0)
        self.assertEqual(r.service_start_date, 2)
        self.assertEqual(r.service_time, 3)
        self.assertEqual(r.service_end_date, 5)
        self.assertEqual(r.time_blocked, 3)
        self.assertEqual(r.exit_date, 8)
        self.assertEqual(r.destination, 1)
        self.assertEqual(r.queue_size_at_arrival, 0)
        self.assertEqual(r.queue_size_at_departure, 3)

        r = ciw.DataRecord(355, 3, 1, 5.7, 2.5, 8.2, 2.1, 10.3, 0.0, 10.3, -1, 32, 21)
        self.assertEqual(r.id_number, 355)
        self.assertEqual(r.customer_class, 3)
        self.assertEqual(r.node, 1)
        self.assertEqual(r.arrival_date, 5.7)
        self.assertEqual(r.waiting_time, 2.5)
        self.assertEqual(r.service_start_date, 8.2)
        self.assertEqual(r.service_time, 2.1)
        self.assertEqual(r.service_end_date, 10.3)
        self.assertEqual(r.time_blocked, 0.0)
        self.assertEqual(r.exit_date, 10.3)
        self.assertEqual(r.destination, -1)
        self.assertEqual(r.queue_size_at_arrival, 32)
        self.assertEqual(r.queue_size_at_departure, 21)


    @given(arrival_date = floats(min_value = 0.0, max_value = 99999.99),
           service_time = floats(min_value = 0.0, max_value = 99999.99),
           inter_service_start_date = floats(min_value = 0.0, max_value = 99999.99),
           inter_exit_date = floats(min_value = 0.0, max_value = 99999.99),
           node = integers(),
           id_number = integers(),
           destination = integers(),
           customer_class = integers(),
           queue_size_at_arrival = integers(),
           queue_size_at_departure = integers())
    def test_init_methodh(self,
                          arrival_date,
                          service_time,
                          inter_service_start_date,
                          inter_exit_date,
                          node,
                          id_number,
                          destination,
                          customer_class,
                          queue_size_at_arrival,
                          queue_size_at_departure):
        # Define parameters
        service_start_date = arrival_date + inter_service_start_date
        service_end_date = service_time + service_start_date
        exit_date = service_start_date + inter_exit_date + service_time
        time_blocked = exit_date - (service_time + service_start_date)
        waiting_time = service_start_date - arrival_date
        service_time = service_end_date - service_start_date
        r = ciw.DataRecord(id_number, customer_class, node, arrival_date,
            waiting_time, service_start_date, service_time, service_end_date,
            time_blocked, exit_date, destination, queue_size_at_arrival,
            queue_size_at_departure)

        # The tests
        self.assertEqual(r.id_number, id_number)
        self.assertEqual(r.customer_class, customer_class)
        self.assertEqual(r.node, node)
        self.assertEqual(r.arrival_date, arrival_date)
        self.assertEqual(r.waiting_time, waiting_time)
        self.assertEqual(r.service_start_date, service_start_date)
        self.assertEqual(r.service_time, service_time)
        self.assertEqual(r.service_end_date, service_end_date)
        self.assertEqual(r.time_blocked, time_blocked)
        self.assertEqual(r.exit_date, exit_date)
        self.assertEqual(r.destination, destination)
        self.assertEqual(r.queue_size_at_arrival, queue_size_at_arrival)
        self.assertEqual(r.queue_size_at_departure, queue_size_at_departure)
