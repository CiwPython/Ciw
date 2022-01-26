from .node import Node

class PSNode(Node):
    """
    Class for a Limited Processor Sharing node, used instead of the Node class.
      - In Processor Sharing systems the service 'load' is shared between equally
        between all customers at the node. That is, while there are x customers
        present, the service slows down x-fold, and so the service time increases
        x-fold.
      - Now the `number_of_servers' represents the node capacity; the maximum
        number of customers allowed to share the service load at a time.
        Customers arriving when the node is overcapacity wait in line.
    """
    def __init__(self, id_, simulation):
        """
        Initialises the node. Differs to the Node class by:
          - Sets the `last_occupancy' to 0; required to calculate service times
             for the current period
          - `ps_capacity` is the node capacity
          - `c' is set to infinity, as within capacity the code logic behaves
             more similar to an infinite server queue
        """
        self.last_occupancy = 0
        super().__init__(id_, simulation)
        self.ps_threshold = self.simulation.network.service_centres[id_ - 1].ps_threshold
        self.ps_capacity = self.c
        self.c = float('inf')
        
    def update_all_service_end_dates(self):
        """
        For each individual reveiving service, calculates the projected end
        service dates if the system state remains contant.
        """
        next_occupancy = min(self.number_of_individuals, self.ps_capacity)
        inds_in_service = [ind for ind in self.all_individuals if ind.with_server]
        for ind in inds_in_service:
            current_period = self.simulation.current_time - ind.date_last_update
            if self.last_occupancy > 0:
                share_completed = (self.ps_threshold * current_period) / max(self.last_occupancy, self.ps_threshold)
            else:
                share_completed = 0
            ind.time_left -= share_completed
            ind.service_end_date = self.simulation.current_time + ((ind.time_left * max(next_occupancy, self.ps_threshold)) / self.ps_threshold)
            ind.date_last_update = self.simulation.current_time

        self.last_occupancy = next_occupancy
        self.date_last_update = self.simulation.current_time
    
    def begin_service_if_possible_accept(self, next_individual):
        """
        Begins the service of the next individual (at acceptance point):
          - give an arrival date and service time
          - if there's free capacity, give a start date and service time to complete
          - mark individual as 'with server'
          - update all customers' service times
        """
        next_individual.arrival_date = self.get_now()
        next_individual.with_server = False
        if self.number_of_individuals <= self.ps_capacity:
            next_individual.service_start_date = self.get_now()
            next_individual.date_last_update = self.get_now()
            next_individual.service_time = self.get_service_time(next_individual)
            next_individual.time_left = next_individual.service_time
            next_individual.with_server = True
            self.update_all_service_end_dates()

    def begin_service_if_possible_release(self, ind=None):
        """
        Begins the service of the next individual (at point
        of previous individual's release)
          - check if there are any individuals waiting for capacity
          - give a start date and 'last update' date
          - sample a service time and this is the time left
          - update all customers' service times
        """
        if self.number_of_individuals >= self.ps_capacity:
            ind = self.all_individuals[self.ps_capacity-1]
            ind.service_start_date = self.get_now()
            ind.date_last_update = self.get_now()
            ind.service_time = self.get_service_time(ind)
            ind.time_left = ind.service_time
            ind.with_server = True
        self.update_all_service_end_dates()
