import ciw
import itertools

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

    def next_node_for_rerouting(self, ind, node_id):
        """
        Chooses the next node when rerouting preempted customer.
        """
        return self.routers[node_id - 1].next_node_for_rerouting(ind)

    def next_node_for_jockeying(self, ind, node_id):
        """
        Chooses the next node when jockeying to another node after reneging.
        """
        return self.routers[node_id - 1].next_node_for_jockeying(ind)


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
        ind.route = self.route_function(ind, self.simulation)

    def next_node(self, ind, node_id):
        """
        Chooses the next node from the process-based pre-defined route.
        """
        if len(ind.route) == 0:
            node_index = -1
        else:
            node_index = ind.route.pop(0)
        return self.simulation.nodes[node_index]

    def next_node_for_rerouting(self, ind, node_id):
        """
        Chooses the next node when rerouting preempted customer.
        """
        return self.next_node(ind, node_id)

    def next_node_for_jockeying(self, ind, node_id):
        """
        Chooses the next node when jockeying to another node after reneging.
        """
        return self.simulation.nodes[-1]

class FlexibleProcessBased(ProcessBased):
    """
    A class to route an individual based on a pre-defined process.
    """
    def __init__(self, route_function, rule, choice):
        """
        Initialises the routing object.

        Takes:
            - route_function: a function that returns a pre-defined route 
        """
        self.route_function = route_function
        if rule not in ['any', 'all']:
            raise ValueError("Flexible routing rules must be one of 'any' or 'all'.")
        if choice not in ['random', 'jsq', 'lb']:
            raise ValueError("Flexible routing choices must be one of 'random', 'jsq', or 'lb'.")
        self.rule = rule
        self.choice = choice

    def find_next_node_from_subset(self, subset, ind):
        """
        Finds the next node within a subset of nodes
        according to the 'choice' parameter
        """
        if self.choice == 'random':
            return ciw.random_choice(subset)
        if self.choice == 'jsq':
            temp_router = JoinShortestQueue(destinations=subset)
            temp_router.initialise(self.simulation, None)
            nd = temp_router.next_node(ind)
            return nd.id_number
        if self.choice == 'lb':
            temp_router = LoadBalancing(destinations=subset)
            temp_router.initialise(self.simulation, None)
            nd = temp_router.next_node(ind)
            return nd.id_number

    def update_individual_route(self, ind, next_node_id):
        """
        Updates the individual route by removing chosen nodes
        along the route, according to the 'rule' parameter
        """
        if self.rule == 'any':
            ind.route = ind.route[1:]
        if self.rule == 'all':
            ind.route[0].remove(next_node_id)
            if len(ind.route[0]) == 0:
                ind.route = ind.route[1:]

    def next_node(self, ind, node_id):
        """
        Chooses the next node from the process-based pre-defined route.
        """
        if len(ind.route) == 0:
            node_index = -1
        else:
            node_index = self.find_next_node_from_subset(ind.route[0], ind)
            self.update_individual_route(ind, node_index)
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

    def next_node_for_rerouting(self, ind):
        """
        By default, the next node for rerouting uses the same method as next_node.
        """
        return self.next_node(ind)

    def next_node_for_jockeying(self, ind):
        """
        Chooses the next node when jockeying to another node after reneging.
        """
        return self.simulation.nodes[-1]


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
                raise ValueError("Routing probabilities must be a float.")
            if p < 0 or p > 1:
                raise ValueError("Routing probabilities must be between 0 and 1.")
        if sum(probs) > 1.0:
            raise ValueError("Routing probabilities must sum to 1 or less.")
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


class Direct(NodeRouting):
    """
    A router that sends the individual directly to another node.
    """
    def __init__(self, to):
        """
        Initialises the routing object.

        Takes:
            - to: a the node index to send to.
        """
        self.to = to

    def next_node(self, ind):
        """
        Chooses the node 'to' with probability 1.
        """
        return self.simulation.nodes[self.to]


class Leave(NodeRouting):
    """
    A router that sends the individual directly to the exit node.
    """
    def next_node(self, ind):
        """
        Chooses the exit node with probability 1.
        """
        return self.simulation.nodes[-1]


class JoinShortestQueue(NodeRouting):
    """
    A router that sends the individual to the node
    with the shortest queue from a list of destinations.
    """
    def __init__(self, destinations, tie_break='random'):
        """
        Initialises the routing object.

        Takes:
            - destinations: a list of node indices
            - tie_break: the method to deal with ties.
                + "random" - randomly choose between ties
                + "order" - prioritise nodes in the order given by the destinations
        """
        self.destinations = destinations
        self.tie_break = tie_break

    def error_check_at_initialise(self):
        if not set(self.destinations).issubset(set([nd.id_number for nd in self.simulation.nodes[1:]])):
            raise ValueError("Routing destinations should be a subset of the nodes in the network.")

    def get_queue_size(self, node_index):
        """
        Gets the size of the queue at the node_index.
        """
        return self.simulation.nodes[node_index].number_of_individuals - self.simulation.nodes[node_index].number_in_service

    def next_node(self, ind):
        """
        Chooses the node from the destinations with the shortest queue.
        """
        shortest_queues = []
        shortest_queue_size = float('inf')
        for node_index in self.destinations:
            queue_size = self.get_queue_size(node_index)
            if queue_size == shortest_queue_size:
                shortest_queues.append(node_index)
            if queue_size < shortest_queue_size:
                shortest_queues = [node_index]
                shortest_queue_size = queue_size
        if self.tie_break == 'random':
            next_node_index = ciw.random_choice(shortest_queues)
            return self.simulation.nodes[next_node_index]
        if self.tie_break == 'order':
            next_node_index = shortest_queues[0]
            return self.simulation.nodes[next_node_index]


class LoadBalancing(JoinShortestQueue):
    """
    A version of JoinShortestQueue that also counts customers in service.
    """
    def get_queue_size(self, node_index):
        """
        Gets the size of the queue at the node_index.
        """
        return self.simulation.nodes[node_index].number_of_individuals


class Cycle(NodeRouting):
    """
    A router that cycles through destinations, repeating the cycle once ended.
    """
    def __init__(self, cycle):
        """
        Initialises the routing object.

        Takes:
            - cycle: an ordered sequence of nodes.
        """
        self.cycle = cycle
        self.generator = itertools.cycle(self.cycle)

    def error_check_at_initialise(self):
        if not set(self.cycle).issubset(set([nd.id_number for nd in self.simulation.nodes[1:]])):
            raise ValueError("Routing destinations should be a subset of the nodes in the network.")

    def next_node(self, ind):
        """
        Chooses the node 'to' with probability 1.
        """
        next_node_index = next(self.generator)
        return self.simulation.nodes[next_node_index]
