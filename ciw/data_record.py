from collections import namedtuple

DataRecord = namedtuple('Record', [
	'id_number',
	'customer_class',
	'node',
    'arrival_date',
    'waiting_time',
    'service_start_date',
    'service_time',
    'service_end_date',
    'time_blocked',
    'exit_date',
    'destination',
    'queue_size_at_arrival',
    'queue_size_at_departure'
    ])