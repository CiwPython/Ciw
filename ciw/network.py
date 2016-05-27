class ServiceCentre(object):
    """
    An information store for each service centre in the queueing network
    """
    def __init__(self,
                 number_of_servers,
                 queueing_capacity,
                 class_change_matrix=None,
                 schedule=None):
        """
        Initialises the ServiceCentre object
        """
        self.number_of_servers = number_of_servers
        self.queueing_capacity = queueing_capacity
        self.class_change_matrix = class_change_matrix
        self.schedule = schedule


class CustomerClass(object):
    """
    An information store for each customer class in the queueing network
    """
    def __init__(self,
                 arrival_distributions,
                 service_distributions,
                 transition_matrix):
        """
        Initialises the CutomerCass object
        """
        self.arrival_distributions = arrival_distributions
        self.service_distributions = service_distributions
        self.transition_matrix = transition_matrix

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