import ciw

class NetworkRouting:
    """
    A class to hold a number of routing objects for each node.
    """
    def __init__(self, routers):
        """
        Sets up the router objects for each node.
        """
        self.routers = routers

    def initialise(self, simulation):
        """
        Gives the simulation and node attributes to the routing objects.
        """
        self.simulation = simulation
        for router, node in zip(self.routers, self.simulation.transitive_nodes):
            router.initialise(self.simulation, node)

    def initialise_individual(self, ind):
        """
        A method that is called at the arrival node when the individual is spawned.
        """
        pass

    def next_node(self, ind, node_id):
        """
        Chooses the next node.
        """
        return self.routers[node_id - 1].next_node(ind)


class TransitionMatrix(NetworkRouting):
    """
    A class to hold a number of probabilistic routing objects.
    """
    def __init__(self, transition_matrix):
        """
        Sets up the relevant probabilistic router objects for each node.
        """
        n_destinations = len(transition_matrix)
        self.routers = [
            Probabilistic(
                destinations=[i for i in range(1, n_destinations + 1)],
                probs=row
            ) for row in transition_matrix
        ]

    def initialise(self, simulation):
        super().initialise(simulation)
        if len(self.routers) != simulation.network.number_of_nodes:
            raise ValueError("Ensure a transition matrix is given, and that the number of rows is equal to the number of nodes in the network.")


class ProcessBased(NetworkRouting):
    """
    A class to route an individual based on a pre-defined process.
    """
    def __init__(self, route_function):
        """
        Initialises the routing object.

        Takes:
            - route_function: a function that returns a pre-defined route 
        """
        self.route_function = route_function

    def initialise(self, simulation):
        """
        Gives the simulation and node attributes to the routing objects.
        """
        self.simulation = simulation

    def initialise_individual(self, ind):
        """
        A method that is called at the arrival node when the individual is spawned.
        """
        ind.route = self.route_function(ind)

    def next_node(self, ind, node_id):
        """
        Chooses the next node from the process-based pre-defined route.
        """
        if len(ind.route) == 0:
            node_index = -1
        else:
            node_index = ind.route.pop(0)
        return self.simulation.nodes[node_index]


class NodeRouting:
    """
    A generic routing class to determine next sampled node.
    """
    def initialise(self, simulation, node):
        """
        Gives the simulation and node attributes to the routing object.
        """
        self.simulation = simulation
        self.node = node
        self.error_check_at_initialise()

    def error_check_at_initialise(self):
        pass

class Probabilistic(NodeRouting):
    """
    A router that probabilistically chooses the next node.
    """
    def __init__(self, destinations, probs):
        """
        Initialises the routing object.

        Takes:
            - destinations: a list of node indices
            - probs: a list of probabilities associated with each destination
        """
        for p in probs:
            if not isinstance(p, float):
                raise ValueError("Routing probabilities must be between 0 and 1, and sum to less than 1.")
            if p < 0 or p > 1:
                raise ValueError("Routing probabilities must be between 0 and 1, and sum to less than 1.")
        if sum(probs) > 1.0:
            raise ValueError("Routing probabilities must be between 0 and 1, and sum to less than 1.")
        self.destinations = destinations + [-1]
        self.probs = probs + [1 - sum(probs)]

    def error_check_at_initialise(self):
        if len(self.probs) != len(self.destinations):
            raise ValueError("Routing probabilities should correspond to destinations, and so should be lists of the same length.")
        if not set(self.destinations).issubset(set([nd.id_number for nd in self.simulation.nodes[1:]])):
            raise ValueError("Routing destinations should be a subset of the nodes in the network.")

    def next_node(self, ind):
        """
        Probabilistically chooses the next node from the destinations.
        """
        node_index = ciw.random_choice(self.destinations, self.probs)
        return self.simulation.nodes[node_index]


