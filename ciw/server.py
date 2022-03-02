from __future__ import division

class Server(object):
    """
    A class to contain server information.
    """
    def __init__(self, node, id_number, start_date=0.0):
        """
        Initialise the server object.
        """
        self.node = node
        self.id_number = id_number
        self.cust = False
        self.busy = False
        self.offduty = False
        self.all_time = False
        self.start_date = start_date
        self.busy_time = False
        self.total_time = False
        self.shift_end = False
        self.next_end_service_date = float('Inf')

    @property
    def utilisation(self):
        return self.busy_time / self.total_time

    def __repr__(self):
        """
        Represents the Server instance as a string.
        """
        return 'Server %s at Node %s' % (self.id_number,
            self.node.id_number)