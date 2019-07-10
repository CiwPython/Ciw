from .node import Node
from .arrival_node import ArrivalNode
from decimal import Decimal, getcontext
from .server import Server

class ExactNode(Node):
    """
    Inherits from the Node class, implements a more
    precise version of addition to fix discrepencies
    with floating point numbers.
    """
    def create_starting_servers(self):
        """
        Initialise the servers
        """
        return [Server(self, i + 1, Decimal('0.0')) for i in range(self.c)]

    def increment_time(self, original, increment):
        """
        Increments the original time by the increment
        """
        return Decimal(str(original)) + Decimal(str(increment))

    def get_service_time(self, ind):
        """
        Returns a service time for the given customer class
        """
        return Decimal(str(self.simulation.service_times[self.id_number][ind.customer_class]._sample(self.simulation.current_time, ind=ind)))

    def get_now(self):
        """
        Gets the current time
        """
        return Decimal(self.simulation.current_time)


class ExactArrivalNode(ArrivalNode):
    """
    Inherits from the ArrivalNode class, implements a
    more precise version of addition to fix discrepencies
    with floating point numbers.
    """
    def increment_time(self, original, increment):
        """
        Increments the original time by the increment
        """
        return Decimal(str(original)) + Decimal(str(increment))

    def inter_arrival(self, nd, clss):
        """
        Samples the inter-arrival time for next class and node.
        """
        return Decimal(str(self.simulation.inter_arrival_times[nd][clss]._sample(self.simulation.current_time)))

