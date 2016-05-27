from __future__ import division

class Server(object):
    """
    A class to contain server information
    """
    def __init__(self, node, id_number):
        """
        Initialise the server object
        """
        self.node = node
        self.id_number = id_number
        self.cust = False
        self.busy = False
        self.offduty = False

    def __repr__(self):
        """
        Represents the Server instance as a string
        """
        return 'Server %s at Node %s' % (self.id_number,
            self.node.id_number)