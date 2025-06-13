from typing import List

from .node import Node
from .arrival_node import ArrivalNode
from decimal import Decimal
from .server import Server


class ExactNode(Node):
    """Exact numerical precision node.

    This class inherits from the Node class, and
    implements a more precise version of addition to
    fix discrepencies with floating point numbers.
    """
    
    @property
    def now(self) -> Decimal:
        """Get the current time."""
        return Decimal(self.simulation.current_time)

    def create_starting_servers(self) -> List[Server]:
        """Initialise the servers at this node."""
        return [Server(self, i + 1, Decimal("0.0")) for i in range(self.c)]

    def increment_time(self, original, increment) -> Decimal:
        """Increment the original time by the increment."""
        return Decimal(str(original)) + Decimal(str(increment))

    def get_service_time(self, ind) -> Decimal:
        """Return a service time for the given customer class."""
        return Decimal(
            str(
                self.simulation.service_times[self.id_number][
                    ind.customer_class
                ]._sample(self.simulation.current_time, ind=ind)
            )
        )


class ExactArrivalNode(ArrivalNode):
    """Node with exact numerical time precision.

    Inherits from the ArrivalNode class, implements a
    more precise version of addition to fix discrepencies
    with floating point numbers.
    """

    def increment_time(self, original, increment) -> Decimal:
        """Increment the original time by the increment."""
        return Decimal(str(original)) + Decimal(str(increment))

    def inter_arrival(self, nd, clss) -> Decimal:
        """Samples the inter-arrival time for next class and node.

        Parameters
        ----------
        nd (Node): Next node.
        clss (Individual): Individual class to be selected next.

        """
        return Decimal(
            str(
                self.simulation.inter_arrival_times[nd][clss]._sample(
                    self.simulation.current_time
                )
            )
        )
