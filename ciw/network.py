class ServiceCentre(object):
    """
    An information store for each service centre in the queueing network.
    Contains all information that is independent of customer class:
      - number of servers
      - queueing capacity
      - server schedules + preemtion status
      - class change matrix
    """
    def __init__(self,
                 number_of_servers,
                 queueing_capacity,
                 class_change_matrix=None,
                 schedule=None,
                 preempt=False):
        """
        Initialises the ServiceCentre object.
        """
        self.number_of_servers = number_of_servers
        self.queueing_capacity = queueing_capacity
        self.class_change_matrix = class_change_matrix
        self.schedule = schedule
        self.preempt = preempt


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
    def __init__(self,
                 arrival_distributions,
                 service_distributions,
                 routing,
                 priority_class,
                 baulking_functions,
                 batching_distributions):
        """
        Initialises the CutomerCass object.
        """
        self.arrival_distributions = arrival_distributions
        self.service_distributions = service_distributions
        self.batching_distributions = batching_distributions
        self.routing = routing
        self.priority_class = priority_class
        self.baulking_functions = baulking_functions

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
        self.number_of_priority_classes = len(set([clss.priority_class for clss in customer_classes]))
        self.priority_class_mapping = {i: clss.priority_class for i, clss in enumerate(customer_classes)}