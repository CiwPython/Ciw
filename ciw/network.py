class ServiceCentre(object):
    """
    An information store for each service centre in the queueing network
    """
    def __init__(self,
                 number_of_servers,
                 queueing_capacity,
                 class_change_matrix=None,
                 schedule=None,
                 preempt=False):
        """
        Initialises the ServiceCentre object
        """
        self.number_of_servers = number_of_servers
        self.queueing_capacity = queueing_capacity
        self.class_change_matrix = class_change_matrix
        self.schedule = schedule
        self.preempt = preempt


class CustomerClass(object):
    """
    An information store for each customer class in the queueing network
    """
    def __init__(self,
                 arrival_distributions,
                 service_distributions,
                 transition_matrix,
                 priority_class,
                 baulking_functions):
        """
        Initialises the CutomerCass object
        """
        self.arrival_distributions = arrival_distributions
        self.service_distributions = service_distributions
        self.transition_matrix = transition_matrix
        self.priority_class = priority_class
        self.baulking_functions = baulking_functions

class Network(object):
    """
    An information store the queueing network
    """
    def __init__(self, service_centres, customer_classes):
        """
        Initialises the Network object
        """
        self.service_centres = service_centres
        self.customer_classes = customer_classes
        self.number_of_nodes = len(service_centres)
        self.number_of_classes = len(customer_classes)
        self.number_of_priority_classes = len(set([cls.priority_class for cls in customer_classes]))
        self.priority_class_mapping = {i:cls.priority_class for i,cls in enumerate(customer_classes)}