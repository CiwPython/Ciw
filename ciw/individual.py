class Individual(object):
    """A class representing an individual agent in a queueing network simulation.

    An Individual instance models the flow of an agent through a queueing network, tracking its arrival time, service time, priority, and other relevant data. This class provides a framework for simulating and analyzing the behavior of such agents.

    Parameters
    ----------
    id_number : int
        A unique identifier for the individual.
    customer_class : str, optional
        The customer class to which the individual belongs (default is 'Customer').
    priority_class : int, optional
        The priority class of the individual (default is 0).
    simulation : bool, optional
        A flag indicating whether the individual is part of a simulation (default is False).

    Attributes
    ----------
    arrival_date : bool or float
        Timestamp for the arrival of the individual.
    service_start_date : bool or float
        Timestamp for the start of service for the individual.
    service_time : bool or float
        Time taken for the service.
    service_end_date : bool or float
        Timestamp for the end of service for the individual.
    exit_date : bool or float
        Timestamp when the individual exits the system.
    id_number : int
        Unique identifier for the individual.
    data_records : list
        A list to store additional data records.
    customer_class : str
        The customer class to which the individual belongs.
    previous_class : str
        The previous customer class of the individual.
    priority_class : int
        The priority class of the individual.
    prev_priority_class : int
        The previous priority class of the individual.
    original_class : str
        The original customer class of the individual.
    is_blocked : bool
        Indicates if the individual is blocked.
    server : bool or Server object
        Indicates whether the individual is assigned to a server.
    queue_size_at_arrival : bool or int
        Size of the queue at the time of arrival.
    queue_size_at_departure : bool or int
        Size of the queue at the time of departure.
    destination : bool or int
        The destination node in the network.
    interrupted : bool
        Indicates if the individual's service was interrupted.
    node : bool or int
        The node in the network where the individual is located.
    simulation : bool or Simulation object
        A flag indicating whether the individual is part of a simulation.

    Methods
    -------
    __repr__()
        Returns a string representation of the individual as 'Individual <id_number>'.

    Usage
    -----
    You can create and manipulate instances of the Individual class to simulate and study the behavior of agents within a queueing network.

    Example
    -------
    ```
    individual = Individual(id_number=1, customer_class='Gold', priority_class=1, simulation=True)
    ```

    For more details on the attributes and methods, please refer to the class documentation.
    """

    def __init__(self, id_number, customer_class='Customer', priority_class=0, simulation=False):
        """
        Initialise an individual.
        """
        self.arrival_date = False
        self.service_start_date = False
        self.service_time = False
        self.service_end_date = False
        self.exit_date = False
        self.id_number = id_number
        self.data_records = []
        self.customer_class = customer_class
        self.previous_class = customer_class
        self.priority_class = priority_class
        self.prev_priority_class = priority_class
        self.original_class = customer_class
        self.is_blocked = False
        self.server = False
        self.queue_size_at_arrival = False
        self.queue_size_at_departure = False
        self.destination = False
        self.interrupted = False
        self.node = False
        self.simulation = simulation

    def __repr__(self):
        """Represents an Individual instance as a string.
        """
        return f"Individual {self.id_number}"
