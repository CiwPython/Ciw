class ServiceCentre:
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