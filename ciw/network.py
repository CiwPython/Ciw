from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class ServiceCentre:
    """
    An information store for each service centre in the queueing network.

    Contains all information that is independent of customer class:
        - number of servers
        - queueing capacity
        - server schedules + preemption status
        - class change matrix
    """

    number_of_servers: int
    queueing_capacity: int
    class_change_matrix = None
    priority_preempt: bool = False
    ps_threshold: int = 1
    server_priority_function: Optional[Callable] = None
    service_discipline: Optional[str] = None
    class_change_time: bool = False


class CustomerClass(object):
    """
    An information store for each customer class in the queueing network.
    Contains all information that is dependent on customer class:
      - arrival distributions
      - service distributions
      - routing matrices/functions
      - priority class
      - baulking functions
      - batching distributions
    """

    def __init__(
        self,
        arrival_distributions,
        service_distributions,
        routing,
        priority_class,
        baulking_functions,
        batching_distributions,
        reneging_time_distributions,
        reneging_destinations,
        class_change_time_distributions,
    ):
        """
        Initialises the CutomerCass object.
        """
        self.arrival_distributions = arrival_distributions
        self.service_distributions = service_distributions
        self.batching_distributions = batching_distributions
        self.routing = routing
        self.priority_class = priority_class
        self.baulking_functions = baulking_functions
        self.reneging_time_distributions = reneging_time_distributions
        self.reneging_destinations = reneging_destinations
        self.class_change_time_distributions = class_change_time_distributions


class Network(object):
    """
    An information store the queueing network.
    Contains a list of ServiceCentre objects for each
    service centre, and a list of CustomerClass objects
    for each customer class.
    """

    def __init__(self, service_centres, customer_classes):
        """
        Initialises the Network object
        """
        self.service_centres = service_centres
        self.customer_classes = customer_classes
        self.number_of_nodes = len(service_centres)
        self.number_of_classes = len(customer_classes)
        self.customer_class_names = sorted(customer_classes.keys())
        self.number_of_priority_classes = len(
            set([clss.priority_class for clss in customer_classes.values()])
        )
        self.priority_class_mapping = {clss: customer_classes[clss].priority_class for clss in customer_classes.keys()}
        for nd_id, node in enumerate(self.service_centres):
            if all(clss.reneging_time_distributions[nd_id] == None for clss in self.customer_classes.values()):
                node.reneging = False
            else:
                node.reneging = True
        if any(dist is not None for clss in customer_classes.values() for dist in clss.class_change_time_distributions.values()):
            for node in self.service_centres:
                node.class_change_time = True
