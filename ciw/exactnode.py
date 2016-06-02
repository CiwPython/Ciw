from .node import Node
from .arrival_node import ArrivalNode
from decimal import Decimal, getcontext

class ExactNode(Node):
    """
    Inherits from the Node class, implements a more
    precise version of addition to fix discrepencies
    with floating point numbers.
    """
    def increment_time(self, original, increment):
        """
        Increments the original time by the increment
        """
        return Decimal(str(original)) + Decimal(str(increment))

    def get_service_time(self, cls):
        """
        Returns a service time for the given customer class
        """
        return Decimal(str(self.simulation.service_times[self.id_number][cls]()))

    def get_now(self, current_time):
        """
        Gets the current time
        """
        return Decimal(str(current_time))


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

    def inter_arrival(self, nd, cls):
        """
        Samples the inter-arrival time for next class and node.
        """
        return Decimal(str(self.simulation.inter_arrival_times[nd][cls]()))
