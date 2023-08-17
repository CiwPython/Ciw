import unittest
import ciw
from hypothesis import given
from hypothesis.strategies import floats, integers


class TestDataRecord(unittest.TestCase):
    def test_init_method(self):
        r = ciw.DataRecord(
            id_number=2,
            customer_class=2,
            original_customer_class=2,
            node=1,
            arrival_date=2,
            waiting_time=0,
            service_start_date=2,
            service_time=3,
            service_end_date=5,
            time_blocked=3,
            exit_date=8,
            destination=1,
            queue_size_at_arrival=0,
            queue_size_at_departure=3,
            server_id=1,
            record_type="service",
        )
        self.assertEqual(r.id_number, 2)
        self.assertEqual(r.customer_class, 2)
        self.assertEqual(r.original_customer_class, 2)
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
        self.assertEqual(r.server_id, 1)
        self.assertEqual(r.record_type, "service")

        r = ciw.DataRecord(
            id_number=355,
            customer_class=4,
            original_customer_class=3,
            node=1,
            arrival_date=5.7,
            waiting_time=2.5,
            service_start_date=8.2,
            service_time=2.1,
            service_end_date=10.3,
            time_blocked=0.0,
            exit_date=10.3,
            destination=-1,
            queue_size_at_arrival=32,
            queue_size_at_departure=21,
            server_id=100,
            record_type="service",
        )
        self.assertEqual(r.id_number, 355)
        self.assertEqual(r.customer_class, 4)
        self.assertEqual(r.original_customer_class, 3)
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
        self.assertEqual(r.server_id, 100)
        self.assertEqual(r.record_type, "service")

    @given(
        arrival_date=floats(min_value=0.0, max_value=99999.99),
        service_time=floats(min_value=0.0, max_value=99999.99),
        inter_service_start_date=floats(min_value=0.0, max_value=99999.99),
        inter_exit_date=floats(min_value=0.0, max_value=99999.99),
        node=integers(),
        id_number=integers(),
        destination=integers(),
        customer_class=integers(),
        original_customer_class=integers(),
        queue_size_at_arrival=integers(),
        queue_size_at_departure=integers(),
        server_id=integers(),
    )
    def test_init_methodh(
        self,
        arrival_date,
        service_time,
        inter_service_start_date,
        inter_exit_date,
        node,
        id_number,
        destination,
        customer_class,
        original_customer_class,
        queue_size_at_arrival,
        queue_size_at_departure,
        server_id,
    ):
        # Define parameters
        service_start_date = arrival_date + inter_service_start_date
        service_end_date = service_time + service_start_date
        exit_date = service_start_date + inter_exit_date + service_time
        time_blocked = exit_date - (service_time + service_start_date)
        waiting_time = service_start_date - arrival_date
        service_time = service_end_date - service_start_date
        r = ciw.DataRecord(
            id_number=id_number,
            customer_class=customer_class,
            original_customer_class=original_customer_class,
            node=node,
            arrival_date=arrival_date,
            waiting_time=waiting_time,
            service_start_date=service_start_date,
            service_time=service_time,
            service_end_date=service_end_date,
            time_blocked=time_blocked,
            exit_date=exit_date,
            destination=destination,
            queue_size_at_arrival=queue_size_at_arrival,
            queue_size_at_departure=queue_size_at_departure,
            server_id=server_id,
            record_type="service",
        )

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
        self.assertEqual(r.server_id, server_id)
        self.assertEqual(r.record_type, "service")
