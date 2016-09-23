from __future__ import division

class DataRecord(object):
    """
    A class for a data record
    """
    def __init__(self,
                arrival_date,
                service_end_date,
                service_start_date,
                exit_date,
                node,
                destination,
                customer_class,
                queue_size_at_arrival,
                queue_size_at_departure):
        """
        Initialises a data record instance.
        """
        self.arrival_date = arrival_date
        self.service_time = service_end_date - service_start_date
        self.service_start_date = service_start_date
        self.exit_date = exit_date
        self.customer_class = customer_class
        self.queue_size_at_arrival = queue_size_at_arrival
        self.queue_size_at_departure = queue_size_at_departure
        self.service_end_date = service_end_date
        self.wait = self.service_start_date - self.arrival_date
        self.blocked = self.exit_date - self.service_end_date
        self.node = node
        self.destination = destination

    def __repr__(self):
        """
        Represents the Data Record
        """
        return "Data Record"
