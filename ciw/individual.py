from __future__ import division

class Individual(object):
    """
    Class for an individual
    """
    def __init__(self, id_number, customer_class=0, priority_class=0):
        """
        Initialise an individual
        """
        self.arrival_date = False
        self.service_start_date = False
        self.service_time = False
        self.service_end_date = False
        self.exit_date = False
        self.id_number = id_number
        self.data_records = []
        self.customer_class = customer_class
        self.previous_class = customer_class
        self.priority_class = priority_class
        self.prev_priority_class = priority_class
        self.is_blocked = False
        self.server = False
        self.queue_size_at_arrival = False
        self.queue_size_at_departure = False
        self.destination = False

    def __repr__(self):
        """
        Represents an Individual instance as a string
        """
        return 'Individual %s' % self.id_number